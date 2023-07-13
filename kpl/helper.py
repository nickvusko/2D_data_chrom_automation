# -*- coding: utf-8 -*-
"""Helper functions for kpl scripts."""
import glob
import json
from numpy import dot
from numpy.linalg import norm
import os
import pandas as pd
from scipy import stats


def compare_spectra(spectrum1: dict, spectrum2: dict) -> float:
    """
    Compares spectra of two peaks. Note that the spectra must be in basic ChromaTOF format mass:intensity separated
    by a blank space.

    param spectrum1: inspected spectrum
    param spectrum2: kpl spectrum
    returns: float result of the similarity comparison
    """
    with open(f"{os.getcwd()}{os.sep}config.txt", 'r') as j:
        config_file = json.loads(j.read())
    spectrum_table_spectra = pd.DataFrame.from_dict({'spectrum1': spectrum1,
                                                     'spectrum2': spectrum2},
                                                    orient="index").fillna(0)
    _1st_array = spectrum_table_spectra.iloc[0, :].to_numpy().astype("float")
    _2nd_array = spectrum_table_spectra.iloc[1, :].to_numpy().astype("float")
    if config_file["sim_compare"] == "Pearson":
        pearson = stats.pearsonr(_1st_array, _2nd_array)
        return round((pearson[0] * 100), 2)
    elif config_file["sim_compare"] == "DOT":
        return dot(_1st_array, _2nd_array) / (norm(_1st_array) * norm(_2nd_array)) * 100
    else:
        print("No valid method for spectral similarity. Force quit.")
        quit()


def check_formatting(file: pd.DataFrame) -> pd.DataFrame:
    """Helper function for reformatting the input files to a proper format

    param file: dataframe for format check
    returns: reformatted dataframe
    """
    lst_columns = [x for x in file.columns]
    if "1st Dimension Time (s)" not in lst_columns:
        lst_columns[[ix for ix, val in enumerate(lst_columns) if "1st" in val][0]] = "1st Dimension Time (s)"
    if "2nd Dimension Time (s)" not in lst_columns:
        lst_columns[[ix for ix, val in enumerate(lst_columns) if "2nd" in val][0]] = "2nd Dimension Time (s)"
    if "Spectra" not in lst_columns:
        lst_columns[[ix for ix, val in enumerate(lst_columns) if "Spect" in val][0]] = "Spectra"
    file.columns = lst_columns
    if file["2nd Dimension Time (s)"].dtype == object:
        file["2nd Dimension Time (s)"] = file["2nd Dimension Time (s)"].str.replace(",", ".").astype("float")
    for i, name in enumerate(file["Name"]):
        file.at[i, "Name"] = name.encode("utf-8")
    return file


def transfer_spectrum(spectrum: list, transform: bool = True, do_list: bool = False) -> dict:
    """
    Transfer spectrum from a list like representation to a dict.

    param do_list: True if the values should be stored as a list - set to True when adding a new line to kpl
    param spectrum: spectrum from the dataframe (df.at[row, "Spectra"].split(" "))
    param transform: True if data transformation should be performed
    returns: spectrum as a dict
    """
    with open(f"{os.getcwd()}{os.sep}config.txt", 'r') as j:
        config_file = json.loads(j.read())
    masses = dict()
    for indic1 in spectrum:
        key = int(float(indic1.split(":")[0]))
        value = round(float(indic1.split(":")[1]), 2)
        if key >= 31:
            if transform:
                value = round((key ** config_file["transformation"][1]) *
                              (value ** config_file["transformation"][0]), 2)
                masses[key] = [value] if do_list else value
            else:
                masses[key] = [value] if do_list else value
        else:
            continue
    return masses


def transform_spectrum(spectrum: dict, do_list: bool = False) -> dict:
    """Transform spectrum.

    param do_list: True if the values should be stored as a list - set to True when adding a new line to kpl
    param spectrum: spectrum
    returns: transformed spectrum
    """
    with open(f"{os.getcwd()}{os.sep}config.txt", 'r') as j:
        config_file = json.loads(j.read())
    for key, value in spectrum.items():
        value = round((key ** config_file["transformation"][1]) * (value ** config_file["transformation"][0]), 2)
        spectrum.update({key: [value]}) if do_list else spectrum.update({key: value})
    return spectrum


def get_files(path: str) -> list:
    """Get list of files.

    param path: path to the folder
    returns: list of files
    """
    return [file for file in glob.iglob(f"{path}{os.sep}*.txt")]
