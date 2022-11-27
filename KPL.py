import pandas as pd
from scipy import stats
from datetime import date
from numpy import dot
from numpy.linalg import norm
import os

from warnings import filterwarnings

filterwarnings("ignore")


class KPLUpdate:
    def __init__(self, central_kpl="database_compounds.txt", to_compare="database_compounds.txt",
                 to_rename_folder="to_rename", sim_compare="DOT", spectra_transform=(0.53, 1.3)):
        self.central_kpl = pd.read_csv(f"{central_kpl}", sep="\t", header=0, index_col=0)
        self.central_kpl_name = central_kpl
        self.to_compare = pd.read_csv(f"{to_compare}", sep="\t", header=0)
        self.to_compare_name = to_compare
        self.to_rename_folder = to_rename_folder
        self.sim_compare = sim_compare
        self.Transformation = spectra_transform
        self.central_kpl.to_csv(f"{self.central_kpl_name}_{date.today()}.txt", sep="\t")
        self.to_compare.set_index("Name").to_csv(f"{self.to_compare}_{date.today()}.txt", sep="\t")
        assert self.sim_compare in ["Pearson, DOT"], "Choose the proper similarity method: Pearson or DOT"
        assert type(spectra_transform) == tuple, "spectra_transform should be a tuple"

    def compare_kpls(self):
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
            lower_band_1st = float(self.to_compare.at[row, "1st Dimension Time (s)"] - 28)
            upper_band_1st = float(self.to_compare.at[row, "1st Dimension Time (s)"] + 28)
            lower_band_2nd = float(self.to_compare.at[row, "2nd Dimension Time (s)"] - 0.7)
            upper_band_2nd = float(self.to_compare.at[row, "2nd Dimension Time (s)"] + 0.7)
            database_foc = self.central_kpl[(lower_band_1st < self.central_kpl["1st Dimension Time (s)"]) & (
                    self.central_kpl["1st Dimension Time (s)"] <= upper_band_1st)]
            database_foc = database_foc[(lower_band_2nd < self.central_kpl["2nd Dimension Time (s)"]) & (
                    self.central_kpl["2nd Dimension Time (s)"] <= upper_band_2nd)]
            found = False
            if len(database_foc) > 0:
                for idx in database_foc.index:
                    result = self.compare_spectra(samplemasses_main, database_foc.at[idx, "Spectrum"].split(" "))
                    if result >= 90:
                        found = True
                        rename_dict[self.to_compare.at[row, "Name"]] = idx
                        self.to_compare.at[row, "Name"] = idx
            if not found:
                oldname = int(self.central_kpl.index[-1].split("X")[1])
                newname = "MX" + str(int(oldname) + 1).zfill(5)
                samplecompounddf = pd.DataFrame(self.to_compare.iloc[row, :]).transpose()
                samplecompounddf["Name"] = newname
                samplecompounddf = samplecompounddf.set_index("Name")
                self.central_kpl = pd.concat([self.central_kpl, samplecompounddf])
                self.central_kpl.at[self.central_kpl.index[-1], "Checked"] = "False"
        self.to_compare = self.to_compare.set_index("Name")
        self.to_compare.to_csv(f"{self.to_compare_name}", sep="\t")
        self.central_kpl = self.central_kpl.set_index("Name")
        self.central_kpl.to_csv(f"{self.central_kpl_name}", sep="\t")

        return rename_dict

    def compare_spectra(self, spectrum1: dict, spectrum2: list) -> float:
        """
        Compares spectra of two peaks. Note that the spectra must be in basic ChromaTOF format mass:intensity
        separated by a blank space.

        Parameters
        ----------
        spectrum1 : dict
                dictionary of mass:intensity of the row from central KPL
        spectrum2 : str
            mass:intensity format separated by a blank space

        Returns
        -------
        float
            The result of spectral correlation coefficient in [%].

        """
        samplemasses_compare = dict()
        for indic2 in spectrum2:
            key = int(float(indic2.split(":")[0]))
            value = float(indic2.split(":")[1])
            if key >= 31:
                if self.Transformation[0] != 1 or self.Transformation[1] != 0:
                    value = round((key ** self.Transformation[1]) * (value ** self.Transformation[0]), 2)
                samplemasses_compare.update({key: value})
            else:
                continue
        spectrum_table_spectra = pd.DataFrame.from_dict({'spectrum1': spectrum1,
                                                         'samplemasses_compare': samplemasses_compare},
                                                        orient="index").fillna(0)
        _1st_array = spectrum_table_spectra.iloc[0, :].to_numpy().astype("float")
        _2nd_array = spectrum_table_spectra.iloc[1, :].to_numpy().astype("float")
        if self.sim_compare == "Pearson":
            pearson = stats.pearsonr(_1st_array, _2nd_array)
            result = round((pearson[0] * 100), 2)
            return result
        elif self.sim_compare == "DOT":
            result = dot(_1st_array, _2nd_array) / (norm(_1st_array) * norm(_2nd_array)) * 100
            return result
        else:
            print("No valid method for spectral similarity. Force quit.")
            quit()

    def rename_compounds(self, rename_dict: dict):
        lst_to_rename = [file for file in os.listdir(f"{self.to_rename_folder}") if file.endswith(".txt")]
        if not os.path.isdir(f"{self.to_rename_folder}{os.sep}renamed"):
            os.makedirs(f"{self.to_rename_folder}{os.sep}renamed")
        for file in lst_to_rename:
            df = pd.read_csv(f"{self.to_rename_folder}{os.sep}{file}", sep="\t", header=0)
            df["Name"].replace(rename_dict, inplace=True)
            df.to_csv(f"{self.to_rename_folder}{os.sep}renamed{os.sep}file", sep="\t")

    def run_process(self):
        if __name__ == "__main__":
            dct = self.compare_kpls()
            self.rename_compounds(dct)


class KPLNew:
    def __init__(self, kpl="None", file_folder="data/dataset_1/merged_files", result_folder="renamed_files",
                 preprocess=True, sim_compare="Pearson", spectra_transform=(0.53, 1.3)):
        if kpl != "None":
            self.kpl = pd.read_csv(f"{kpl}", sep="\t", header=0)
            self.kpl_name = "KPL"
            try:
                self.kpl = self.kpl.drop("Unnamed: 0", axis=1)
                print(self.kpl)
            except KeyError:
                print("No need to drop unnamed columns")
                pass
        else:
            self.kpl = pd.DataFrame(
                columns=["Name", "1st Dimension Time (s)", "2nd Dimension Time (s)", "Spectrum", "Note", "Checked",
                         "Origin"])
            self.kpl_name = "KPL"
        self.kpl.set_index("Name").to_csv(f"{result_folder}{os.sep}{self.kpl_name}_{date.today()}.txt", sep="\t")
        self.file_folder = file_folder
        self.result_folder = result_folder
        self.sim_compare = sim_compare
        self.Transformation = spectra_transform
        self.preprocess = preprocess
        if not os.path.isdir(f"{self.result_folder}"):
            os.makedirs(f"{self.result_folder}")

    def compare_rows(self):
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
            if self.kpl.empty:
                samplecompounddf = pd.DataFrame(file_to_compare.iloc[0, :]).transpose()
                self.kpl = pd.concat([self.kpl, samplecompounddf])
                self.kpl.at[0, "Name"] = "MX00000"
                self.kpl["Checked"] = "False"
                self.kpl["Note"] = samplecompounddf["Name"]
                self.kpl["Origin"] = file
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
                if samplemasses_main[73] >= 700 or samplemasses_main[147] >= 700:
                    continue
                lower_band_1st = float(file_to_compare.at[row, "1st Dimension Time (s)"] - 80)
                upper_band_1st = float(file_to_compare.at[row, "1st Dimension Time (s)"] + 80)
                lower_band_2nd = float(file_to_compare.at[row, "2nd Dimension Time (s)"] - 0.9)
                upper_band_2nd = float(file_to_compare.at[row, "2nd Dimension Time (s)"] + 0.9)
                database_f = self.kpl[(lower_band_1st < self.kpl["1st Dimension Time (s)"]) & (
                        self.kpl["1st Dimension Time (s)"] <= upper_band_1st)]
                database_foc = database_f[(lower_band_2nd < database_f["2nd Dimension Time (s)"]) & (
                        database_f["2nd Dimension Time (s)"] <= upper_band_2nd)]
                found = False
                if len(database_foc) > 0:
                    comp_results = {}
                    for idx in database_foc.index:
                        result = self.compare_spectra(samplemasses_main, database_foc.at[idx, "Spectrum"].split(" "))
                        if result >= 80:
                            found = True
                            comp_results[database_foc.at[idx, "Name"]] = result
                    try:
                        file_to_compare.at[row, "Name"] = max(comp_results, key=comp_results.get)
                        print(f"MATCH FOUND - {max(comp_results, key=comp_results.get)}")
                    except ValueError:
                        print("NO MATCH FOUND")
                        pass
                if not found:
                    try:
                        oldname = int(self.kpl.iat[-1, 0].split("X")[1])
                        newname = "MX" + str(int(oldname) + 1).zfill(5)
                        samplecompounddf = pd.DataFrame(file_to_compare.iloc[row, :]).transpose()
                        samplecompounddf["Name"] = newname
                        self.kpl = pd.concat([self.kpl, samplecompounddf], ignore_index=True)
                        self.kpl.at[self.kpl.index[-1], "Checked"] = "False"
                        self.kpl.at[self.kpl.index[-1], "Note"] = file_to_compare.loc[row, "Name"]
                        self.kpl.at[self.kpl.index[-1], "Origin"] = file
                        file_to_compare.at[row, "Name"] = newname
                    except AttributeError:
                        print(self.kpl)
                        quit()
            file_to_compare = file_to_compare.set_index("Name")
            try:
                file_to_compare.drop(["Z score 1st RT", "Z score 2nd RT", "Euclidian"], axis=1, inplace=True)
            except KeyError:
                print("Variable names are already correct .")
            self.kpl.to_csv(f"{self.result_folder}{os.sep}{self.kpl_name}.txt", sep="\t")
            file_to_compare.to_csv(f"{self.result_folder}{os.sep}{file}", sep="\t")
        self.kpl = self.kpl.set_index("Name")
        self.kpl.to_csv(f"{self.result_folder}{os.sep}{self.kpl_name}.txt", sep="\t")

    def merge_peak_entries(self, file, name):
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
                        # print(result)
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

    def mask_groupby(self, df):
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

    def compare_spectra(self, spectrum1: dict, spectrum2: list) -> float:
        """
        Compares spectra of two peaks. Note that the spectra must be in basic ChromaTOF format mass:intensity separated
        by a blank space.

        Parameters
        ----------
        spectrum1 : dict
                dictionary of mass:intensity of the row from central KPL
        spectrum2 : str
            mass:intensity format separated by a blank space

        Returns
        -------
        float
            The result of spectral correlation coefficient in [%].

        """
        samplemasses_compare = dict()
        for indic2 in spectrum2:
            key = int(float(indic2.split(":")[0]))
            value = float(indic2.split(":")[1])
            if key >= 31:
                if self.Transformation[0] != 1 or self.Transformation[1] != 0:
                    value = round((key ** self.Transformation[1]) * (value ** self.Transformation[0]), 2)
                samplemasses_compare.update({key: value})
            else:
                continue
        spectrum_table_spectra = pd.DataFrame.from_dict({'spectrum1': spectrum1,
                                                         'samplemasses_compare': samplemasses_compare},
                                                        orient="index").fillna(0)
        _1st_array = spectrum_table_spectra.iloc[0, :].to_numpy().astype("float")
        _2nd_array = spectrum_table_spectra.iloc[1, :].to_numpy().astype("float")
        if self.sim_compare == "Pearson":
            pearson = stats.pearsonr(_1st_array, _2nd_array)
            result = round((pearson[0] * 100), 2)
            return result
        elif self.sim_compare == "DOT":
            result = dot(_1st_array, _2nd_array) / (norm(_1st_array) * norm(_2nd_array)) * 100
            return result
        else:
            print("No valid method for spectral similarity. Force quit.")
            quit()

    def run_kpl(self):
        if __name__ == "__main__":
            self.compare_rows()


run_x = 0
if run_x == 0:
    KPLNew(preprocess=False, file_folder="D:\\Data_align\\metadata\\rasa",
           result_folder="K:\\transfer\\rasa\\renamed").run_kpl()
else:
    KPLUpdate().run_process()
