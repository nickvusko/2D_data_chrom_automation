# -*- coding: utf-8 -*-
"""Helper functions for KPL scripts."""
from numpy import dot
from numpy.linalg import norm
import pandas as pd
from scipy import stats


def compare_spectra(spectrum1: dict, spectrum2: list, transformation: tuple[float, float] = (1.0, 0.0),
                    sim_compare: str = "DOT") -> float:
    """
    Compares spectra of two peaks. Note that the spectra must be in basic ChromaTOF format mass:intensity separated
    by a blank space.

    :param sim_compare: name of the comparison method. Default value set to DOT
    :param spectrum1: dict of mass: intensity values
    :param spectrum2: list of mass: intensity values
    :param transformation: tuple of floats for spectral transformation. default values are set to
    :return: spectral similarity
    """
    samplemasses_compare = dict()
    for indic2 in spectrum2:
        key = int(float(indic2.split(":")[0]))
        value = float(indic2.split(":")[1])
        if key >= 31:
            if transformation[0] != 1 or transformation[1] != 0:
                samplemasses_compare.update({key: (round((key ** transformation[1]) *
                                                         (value ** transformation[0]), 2))})
    spectrum_table_spectra = pd.DataFrame.from_dict({'spectrum1': spectrum1,
                                                     'samplemasses_compare': samplemasses_compare},
                                                    orient="index").fillna(0)
    _1st_array = spectrum_table_spectra.iloc[0, :].to_numpy().astype("float")
    _2nd_array = spectrum_table_spectra.iloc[1, :].to_numpy().astype("float")
    if sim_compare == "Pearson":
        pearson = stats.pearsonr(_1st_array, _2nd_array)
        result = round((pearson[0] * 100), 2)
        return result
    elif sim_compare == "DOT":
        result = dot(_1st_array, _2nd_array) / (norm(_1st_array) * norm(_2nd_array)) * 100
        return result
    else:
        print("No valid method for spectral similarity. Force quit.")
        quit()
