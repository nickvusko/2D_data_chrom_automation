# -*- coding: utf-8 -*-
# Author:  NIKOLA LADISLAVOVA, nikola.ladislavova@gmail.com
# Created: Oct 30, 2022
# Purpose: Chromatography

import pandas as pd
from scipy import stats
from datetime import date
from numpy import dot
from numpy.linalg import norm
import os

from warnings import filterwarnings

filterwarnings("ignore")


class KPLNew:
    """
    A basic class for creation of a library of detected compounds
    """
    def __init__(self, kpl=None, file_folder="data/", result_folder="renamed_files",
                 preprocess=True, sim_compare="DOT", spectra_transform=(0.53, 1.3), search_window=(30, 0.5),
                 sim_treshold=90):
        """
        :param kpl: path and name of the central library. If it is left to None value, the script will create a new
        library. Please note that all processed samples should be aligned to the same referential table
        or chromatogram.
        :param file_folder: string; path to the folder containing samples to be processed
        :param result_folder: string; path to the result folder
        :param preprocess: boolean; whenever the script should check the samples and merge multiple peaks of the same
        compounds if such case is detected.
        :param sim_compare: ["DOT", "Pearson"]; choose a mathematical approach for mass spectra comparison
        :param spectra_transform: tuple(float, float); first number is for transforming the intensity, tje second number
        transforms mass number. Please refer to https://doi.org/10.1155/2013/509761.
        :param search_window: tuple(float, float); the first number defines the range in the first dimension,
        the second number defines the range in the second dimension.
        The range: <coordinate_of_inspected_row-float, coordinate_of_inspected_row+float>
        Please refer to https://doi.org/10.1016/j.chroma.2007.11.101
        :param sim_treshold: int; percentual threshold for mass spectra comparison
        """
        if kpl is not None:
            self.KPL = pd.read_csv(f"{kpl}", sep="\t", header=0)
            self.KPL_name = "KPL"
            try:
                self.KPL = self.KPL.drop("Unnamed: 0", axis=1)
                print(self.KPL)
            except KeyError:
                print("No need to drop columns")
                pass
        else:
            self.KPL = pd.DataFrame(
                columns=["Name", "1st Dimension Time (s)", "2nd Dimension Time (s)", "Spectrum", "Note", "Checked",
                         "Origin"])
            self.KPL_name = "KPL"
        self.KPL.set_index("Name").to_csv(f"{result_folder}{os.sep}{self.KPL_name}_{date.today()}.txt", sep="\t")
        self.file_folder = file_folder
        self.result_folder = result_folder
        self.sim_compare = sim_compare
        self.spectra_transform = spectra_transform
        self.preprocess = preprocess
        self.search_window = search_window
        self.sim_treshold = sim_treshold
        assert self.sim_compare in ["Pearson", "DOT"], "Choose the proper similarity method: Pearson or DOT"
        assert type(spectra_transform) == tuple, "spectra_transform should be a tuple"
        if not os.path.isdir(f"{self.result_folder}"):
            os.makedirs(f"{self.result_folder}")

    def compare_rows(self):
        """
        The main function for comparing the processed sample rows.
        :return: None
        """
        if self.preprocess:
            for file in [file for file in os.listdir(f"{self.file_folder}") if file.endswith(".txt")]:
                print("Processing file: ", file)
                file_to_compare = pd.read_csv(f"{self.file_folder}{os.sep}{file}", sep="\t", header=0,
                                              usecols=["Name", "1st Dimension Time (s)", "2nd Dimension Time (s)",
                                                       "Spectrum", "Area", "Height"], encoding="latin-1")
                self.merge_peak_entries(file_to_compare, file)
            self.file_folder = f"{self.file_folder}{os.sep}merged_files{os.sep}"
        for file in [file for file in os.listdir(f"{self.file_folder}") if file.endswith(".txt")]:
            print("Processing file: ", file)
            file_to_compare = pd.read_csv(f"{self.file_folder}{os.sep}{file}", sep="\t", header=0, encoding="latin-1")
            file_to_compare = file_to_compare[file_to_compare["2nd Dimension Time (s)"] > 1.5]
            file_to_compare.reset_index(inplace=True, drop=True)
            print(file_to_compare)
            if self.KPL.empty:
                samplecompounddf = pd.DataFrame(file_to_compare.iloc[0, :]).transpose()
                self.KPL = pd.concat([self.KPL, samplecompounddf])
                self.KPL.at[0, "Name"] = "MX00000"
                self.KPL["Checked"] = "False"
                self.KPL["Note"] = samplecompounddf["Name"]
                self.KPL["Origin"] = file
                del samplecompounddf
            for row in file_to_compare.index:
                row_spectra = file_to_compare.at[row, "Spectrum"].split(" ")
                samplemasses_main = dict()
                for indic1 in row_spectra:
                    key = int(float(indic1.split(":")[0]))
                    value = round(float(indic1.split(":")[1]), 2)
                    if key >= 31:
                        samplemasses_main.update({key: value})
                    else:
                        continue
                try:
                    if samplemasses_main[73] >= 800 or samplemasses_main[147] >= 800:
                        continue
                except KeyError:
                    continue
                lower_band_1st = float(file_to_compare.at[row, "1st Dimension Time (s)"] - self.search_window[0])
                upper_band_1st = float(file_to_compare.at[row, "1st Dimension Time (s)"] + self.search_window[0])
                lower_band_2nd = float(file_to_compare.at[row, "2nd Dimension Time (s)"] - self.search_window[1])
                upper_band_2nd = float(file_to_compare.at[row, "2nd Dimension Time (s)"] + self.search_window[1])
                database_f = self.KPL[(lower_band_1st < self.KPL["1st Dimension Time (s)"]) & (
                            self.KPL["1st Dimension Time (s)"] <= upper_band_1st)]
                database_foc = database_f[(lower_band_2nd < database_f["2nd Dimension Time (s)"]) & (
                            database_f["2nd Dimension Time (s)"] <= upper_band_2nd)]
                found = False
                if len(database_foc) > 0:
                    comp_results = {}
                    for idx in database_foc.index:
                        result = self.compare_spectra(samplemasses_main, database_foc.at[idx, "Spectrum"].split(" "))
                        if result >= self.sim_treshold:
                            found = True
                            comp_results[database_foc.at[idx, "Name"]] = result
                    try:
                        file_to_compare.at[row, "Name"] = max(comp_results, key=comp_results.get)
                        print(f"MATCH FOUND - {max(comp_results, key=comp_results.get)}")
                    except:
                        print("NO MATCH FOUND")
                if not found:
                    oldname = int(self.KPL.iat[-1, 0].split("X")[1])
                    newname = "MX" + str(int(oldname) + 1).zfill(5)
                    samplecompounddf = pd.DataFrame(file_to_compare.iloc[row, :]).transpose()
                    samplecompounddf["Name"] = newname
                    self.KPL = pd.concat([self.KPL, samplecompounddf], ignore_index=True)
                    self.KPL.at[self.KPL.index[-1], "Checked"] = "False"
                    self.KPL.at[self.KPL.index[-1], "Note"] = file_to_compare.loc[row, "Name"]
                    self.KPL.at[self.KPL.index[-1], "Origin"] = file
                    file_to_compare.at[row, "Name"] = newname
            file_to_compare = file_to_compare.set_index("Name")
            try:
                file_to_compare.drop(["Z score 1st RT", "Z score 2nd RT", "Euclidian"], axis=1, inplace=True)
            except KeyError:
                print("Variable names are already correct .")
            self.KPL.to_csv(f"{self.result_folder}{os.sep}{self.KPL_name}.txt", sep="\t")
            file_to_compare.to_csv(f"{self.result_folder}{os.sep}{file}", sep="\t")
        self.KPL = self.KPL.set_index("Name")
        self.KPL.to_csv(f"{self.result_folder}{os.sep}{self.KPL_name}.txt", sep="\t")

    def compare_spectra(self, spectrum1: dict, spectrum2: list) -> float:
        """
        Compares spectra of two peaks. Note that the spectra must be in basic ChromaTOF format mass:intensity separated
        by a blank space

        :param spectrum1: dictionary of mass:intensity of the inspected row
        :param spectrum2: dictionary of mass:intensity of the row from central KPL
        :return: The result of spectral correlation coefficient in [%].
        """
        spectrum_table = pd.DataFrame(columns=[x for x in range(31, 801)])
        samplemasses_compare = dict()
        for indic2 in spectrum2:
            key = int(float(indic2.split(":")[0]))
            value = round(float(indic2.split(":")[1]), 2)
            if key >= 31:
                samplemasses_compare.update({key: value})
            else:
                continue
        if self.spectra_transform[0] == 1 and self.spectra_transform[1] == 0:
            pass
        else:
            for spectra in [spectrum1, samplemasses_compare]:
                for key in spectra.keys():
                    spectra[key] = (float(spectra[key]) ** self.spectra_transform[0]) * (
                        float(int(key) ** self.spectra_transform[1]))
        spectrum_table = spectrum_table.append(spectrum1, ignore_index=True).fillna(0)
        spectrum_table = spectrum_table.append(samplemasses_compare, ignore_index=True).fillna(0)
        _1st_array = spectrum_table.iloc[0, :].to_numpy().astype("float")
        _2nd_array = spectrum_table.iloc[1, :].to_numpy().astype("float")
        if self.sim_compare == "Pearson":
            pearson = stats.pearsonr(_1st_array, _2nd_array)
            result = round((pearson[0] * 100), 2)
        else:
            result = round(dot(_1st_array, _2nd_array) / (norm(_1st_array) * norm(_2nd_array)) * 100, 2)
        return result

    def merge_peak_entries(self, file: pd.DataFrame, name: str):
        """
         The function merges the multiple peaks of the same compound (from tailing for example) in the processed sample
        :param file: df of the processed sample
        :param name: name of the processed sample
        :return: None
        """
        if not os.path.isdir(f"{self.file_folder}{os.sep}merged_files"):
            os.makedirs(f"{self.file_folder}{os.sep}merged_files")
        try:
            file["2nd Dimension Time (s)"] = file["2nd Dimension Time (s)"].str.replace(",", ".").astype("float")
        except AttributeError:
            file["2nd Dimension Time (s)"] = file["2nd Dimension Time (s)"].replace(",", ".").astype("float")
        try:
            file = file.rename(columns={"Spectra": "Spectrum"})
        except KeyError:
            pass
        file.reset_index(inplace=True)
        for nmr in file.index:
            df = pd.DataFrame(file.iloc[nmr, :]).transpose()
            lower_band_1 = int(df["1st Dimension Time (s)"] - 0.0001)
            upper_band_1 = int(df["1st Dimension Time (s)"] + 11)
            lower_band_2 = float(df["2nd Dimension Time (s)"] - 0.0001)
            upper_band_2 = float(df["2nd Dimension Time (s)"] - 0.5)
            focus_range = file[file["1st Dimension Time (s)"].between(lower_band_1, upper_band_1)]
            focus_range = focus_range[focus_range["2nd Dimension Time (s)"].between(upper_band_2, lower_band_2)]
            if focus_range.shape[0] > 1:
                row_spectra = file.at[nmr, "Spectrum"].split(" ")
                samplemasses_main = dict()
                for indic1 in row_spectra:
                    key = int(float(indic1.split(":")[0]))
                    value = round(float(indic1.split(":")[1]), 2)
                    if key >= 31:
                        samplemasses_main.update({key: value})
                    else:
                        continue
                for row in focus_range.index:
                    main_df = df
                    compare_df = pd.DataFrame(focus_range.loc[row]).transpose()
                    if main_df.iat[0, 0] == compare_df.iat[0, 0]:
                        continue
                    else:
                        result = self.compare_spectra(samplemasses_main, compare_df.at[row, "Spectrum"].split(" "))
                        if result >= 85:
                            file.iat[row, 0] = file.iat[nmr, 0]
                        pass
        try:
            file = file.drop(["Retention Index", "Group", "Type", "Quant Masses", "S/N", "Weight"], axis=1)
        except KeyError:
            pass
        new_dataframe = self.mask_groupby(file)
        new_dataframe = new_dataframe.drop("index", axis=1)
        new_dataframe = new_dataframe.set_index("Name")
        # new_dataframe = calculate_zscore_times(new_dataframe)
        new_dataframe = new_dataframe.sort_values(by="1st Dimension Time (s)")
        new_dataframe.to_csv(f"{self.file_folder}{os.sep}merged_files{os.sep}{name}", sep="\t")

    @staticmethod
    def mask_groupby(df: pd.DataFrame):
        """
        Performs groupby operation on the supplied dataframe
        :param df: processed dataframe
        :return: pd.DataFrame
        """
        lst_of_indexes = []
        new_dataframe = pd.DataFrame()
        for nmr in df.index:
            if df.iat[nmr, 0] not in lst_of_indexes:
                lst_of_indexes.append(df.iat[nmr, 0])
        for indx in lst_of_indexes:
            mask = df["index"].values == indx
            working_df = df[mask]
            if working_df.shape[0] == 1:
                new_dataframe = pd.concat([new_dataframe, working_df], axis=0, ignore_index=True, sort=False)
                continue
            else:
                repre_df = pd.DataFrame(
                    columns=["index", "Name", "1st Dimension Time (s)", "2nd Dimension Time (s)", "Area", "Height",
                             "Spectrum"])
                area = working_df["Area"].sum()
                max_area = working_df["Area"].idxmax()
                height = working_df["Height"].sum()
                _1stRT = round((1 / area) * sum(working_df["Area"] * working_df["1st Dimension Time (s)"]))
                _2ndRT = (1 / area) * sum(working_df["Area"] * working_df["2nd Dimension Time (s)"])
                repre_df.loc[0] = [working_df.iat[0, 0], working_df.iat[0, 1], _1stRT, _2ndRT, area, height,
                                   working_df.at[max_area, "Spectrum"]]
                new_dataframe = pd.concat([new_dataframe, repre_df], axis=0, ignore_index=True, sort=False)
                pass
        print("Original shape of Dataframe: ", df.shape, "||| New shape if Dataframe: ", new_dataframe.shape)
        del lst_of_indexes
        return new_dataframe

    def run_kpl(self):
        if __name__ == "__main__":
            self.compare_rows()


class KPLUpdate(KPLNew):
    """
    A basic class for creation of a library of detected compounds
    """
    def __init__(self, kpl="database_compounds.txt", to_compare="database_compounds.txt",
                 file_folder="to_rename", result_folder="renamed_files", sim_compare="DOT",
                 spectra_transform=(0.53, 1.3), search_window=(30, 0.5), sim_treshold=90):
        """
        :param kpl: path and name of the central library. Please note that all processed samples should be aligned to
         the same referential table or chromatogram.
        :param to_compare: path and name of the compared library. lease note that all processed samples
         should be aligned to the same referential table or chromatogram as the central library.
        :param file_folder: string; path to the folder containing samples to be processed
        :param result_folder: string; path to the result folder
        :param sim_compare: ["DOT", "Pearson"]; choose a mathematical approach for mass spectra comparison
        :param spectra_transform: tuple(float, float); first number is for transforming the intensity, tje second number
        transforms mass number. Please refer to https://doi.org/10.1155/2013/509761.
        :param search_window: tuple(float, float); the first number defines the range in the first dimension,
        the second number defines the range in the second dimension.
        The range: <coordinate_of_inspected_row-float, coordinate_of_inspected_row+float>
        Please refer to https://doi.org/10.1016/j.chroma.2007.11.101
        :param sim_treshold: int; percentual threshold for mass spectra comparison
        """
        super().__init__(kpl, file_folder=file_folder, sim_compare=sim_compare, spectra_transform=spectra_transform,
                         search_window=search_window, sim_treshold=sim_treshold, result_folder=result_folder,
                         preprocess=False)
        self.central_KPL = pd.read_csv(f"{kpl}", sep="\t", header=0, index_col=0)
        self.central_KPL_name = kpl
        self.to_compare = pd.read_csv(f"{to_compare}", sep="\t", header=0)
        self.to_compare_name = to_compare
        self.to_rename_folder = file_folder
        self.central_KPL.to_csv(f"{self.central_KPL}_{date.today()}.txt", sep="\t")
        self.to_compare.set_index("Name").to_csv(f"{self.to_compare}_{date.today()}.txt", sep="\t")

    def compare_kpls(self):
        """
        The main function for comparing the libraries.
        :return: None
        """
        rename_dict = dict()
        for row in self.to_compare.index:
            row_spectra = self.to_compare.at[row, "Spectrum"].split(" ")
            samplemasses_main = dict()
            for indic1 in row_spectra:
                key = int(float(indic1.split(":")[0]))
                value = round(float(indic1.split(":")[1]), 2)
                if key >= 31:
                    samplemasses_main.update({key: value})
                else:
                    continue
            lower_band_1st = float(self.to_compare.at[row, "1st Dimension Time (s)"] - self.search_window[0])
            upper_band_1st = float(self.to_compare.at[row, "1st Dimension Time (s)"] + self.search_window[0])
            lower_band_2nd = float(self.to_compare.at[row, "2nd Dimension Time (s)"] - self.search_window[1])
            upper_band_2nd = float(self.to_compare.at[row, "2nd Dimension Time (s)"] + self.search_window[1])
            database_f = self.central_KPL[(lower_band_1st < self.central_KPL["1st Dimension Time (s)"]) & (
                        self.central_KPL["1st Dimension Time (s)"] <= upper_band_1st)]
            database_foc = database_f[(lower_band_2nd < self.central_KPL["2nd Dimension Time (s)"]) & (
                        self.central_KPL["2nd Dimension Time (s)"] <= upper_band_2nd)]
            found = False
            if len(database_foc) > 0:
                for idx in database_foc.index:
                    result = self.compare_spectra(samplemasses_main, database_foc.at[idx, "Spectrum"].split(" "))
                    if result >= self.sim_treshold:
                        rename_dict[self.to_compare.at[row, "Name"]] = idx
                        self.to_compare.at[row, "Name"] = idx
                        found = True
            if not found:
                oldname = int(self.central_KPL.index[-1].split("X")[1])
                newname = "MX" + str(int(oldname) + 1).zfill(5)
                samplecompounddf = pd.DataFrame(self.to_compare.iloc[row, :]).transpose()
                samplecompounddf["Name"] = newname
                samplecompounddf = samplecompounddf.set_index("Name")
                self.central_KPL = pd.concat([self.central_KPL, samplecompounddf])
                self.central_KPL.at[self.central_KPL.index[-1], "Checked"] = "False"
        self.to_compare = self.to_compare.set_index("Name")
        self.to_compare.to_csv(f"{self.to_compare_name}", sep="\t")
        self.central_KPL = self.central_KPL.set_index("Name")
        self.central_KPL.to_csv(f"{self.central_KPL_name}", sep="\t")

        return rename_dict

    def rename_compounds(self, rename_dict: dict):
        """

        :param rename_dict: a dictionary of codes to be renamed in the compared library.
        :return: None
        """
        lst_to_rename = [file for file in os.listdir(f"{self.to_rename_folder}") if file.endswith(".txt")]
        if not os.path.isdir(f"{self.result_folder}"):
            os.makedirs(f"{self.result_folder}")
        for file in lst_to_rename:
            df = pd.read_csv(f"{self.to_rename_folder}{os.sep}{file}", sep="\t", header=0)
            df["Name"].replace(rename_dict, inplace=True)
            df.to_csv(f"{self.result_folder}{os.sep}{file}", sep="\t")

    def run_process(self):
        if __name__ == "__main__":
            dct = self.compare_kpls()
            self.rename_compounds(dct)


run_x = 0
if run_x == 0:
    KPLNew().run_kpl()
else:
    KPLUpdate().run_process()
