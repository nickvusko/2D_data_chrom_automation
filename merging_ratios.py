# -*- coding: utf-8 -*-
# Author:  NIKOLA LADISLAVOVA, nikola.ladislavova@gmail.com
# Created: Feb 25, 2021
# Purpose: Chromatography
import numpy as np
import pandas as pd


def get_input():
    list_of_files_define = []
    list_of_files_anal = []
    print("Create a list of files to define ratios of interest. When you are done, press Enter.")
    while True:
        inpdefine = (input("File name: "))
        if inpdefine != "":
            list_of_files_define.append(inpdefine+".txt")
            print("So far added:_", list_of_files_define)
        else:
            break

    print("Create a list of files for analysis. When you are done, press Enter.")
    while True:
        inpdefine = (input("File name: "))
        if inpdefine != "":
            list_of_files_anal.append(inpdefine+".txt")
            print("So far added:_", list_of_files_anal)
        else:
            break
    print("Done collecting files for defining the columns.")
    return list_of_files_define, list_of_files_anal


def get_columns_names(list_of_files_define, ratiocount):
    list_of_names = []
    for f in list_of_files_define:
        fh = pd.read_csv(f, header=0, sep="\t", index_col=0)
        fh = fh.iloc[:, :ratiocount]
        for clmn_name in fh.columns:
            if clmn_name in list_of_names:
                continue
            else:
                list_of_names.append(clmn_name)
    return list_of_names


def fill_in_analized(final_table, list_of_files_anal):
    partial_table = pd.DataFrame()
    for f in list_of_files_anal:
        fh = pd.read_csv(f, header=0, sep="\t", index_col=0)
        partial_table = pd.concat([partial_table, fh])
    final_table = pd.concat([final_table, partial_table], axis=0, join="inner")
    return final_table


def main():
    list_of_files_define, list_of_files_anal = get_input()
    zerocount = int(input("How many zeros in column are acceptable? [%] "))
    ratiocount = int(input("How many ratios with the least SD from each dataset you want to involve?"))
    name_of_file = str(input("Enter the name of the result file: "))

    list_of_names = get_columns_names(list_of_files_define, ratiocount)

    final_table = pd.DataFrame(columns=list_of_names)
    for f in list_of_files_define:
        fh = pd.read_csv(f, header=0, sep="\t", index_col=0)
        fh = fh.replace(np.inf, 0)
        final_table = pd.concat([final_table, fh])
    if len(list_of_files_anal) != 0:
        final_table = fill_in_analized(final_table, list_of_files_anal)

    final_table = final_table.fillna(0)
    row_count = len(final_table)
    one_perc = row_count / 100
    final_tablex = final_table[list_of_names]
    final_tablex = final_tablex.loc[:, (((row_count - final_tablex.astype(bool).sum(axis=0)) / one_perc) <= zerocount)]
    print(final_tablex)

    final_tablex.to_csv(name_of_file + ".txt", sep="\t")


main()
