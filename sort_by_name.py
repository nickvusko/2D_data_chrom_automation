# -*- coding: utf-8 -*-
# Author:  NIKOLA LADISLAVOVA, nikola.ladislavova@gmail.com
# Created: Feb 25, 2021
# Purpose: Chromatography


import pandas as pd
import glob


# get files and create a table
def get_files():
    """returns list of files for the analysis"""
    list_of_files_all = []
    for file in glob.iglob("strely\\*.txt"):
        if file == "area.txt":
            continue
        if file == "height.txt":
            continue
        filename = file
        list_of_files_all.append(filename)
    return list_of_files_all


# get list of compounds
def get_names_compounds(list_of_files_all: list) -> list:
    """get names of all compounds in analysed chromatograms and create index list"""
    index_lst = []
    for f in list_of_files_all:
        # fh = open(f, encoding="utf8")
        # for row in fh:
        #     if row.startswith("MX"):
        #         rowx = row.strip()
        #         rowy = rowx.split("\t")[0]
        #         if rowy in index_lst or rowy == "Name" or rowy == "":
        #             continue
        #         else:
        #             index_lst.append(rowy)
        df = pd.read_csv(f, sep="\t", header = 0, index_col=0)
        for name in df.index:
            if name not in index_lst:
                index_lst.append(name)
    return index_lst


# create summary tables
def get_concat_tables(list_of_files_all: list, index_lst: list) -> None:
    """create merged tables for area and height based on index list"""
    df_area_all = pd.DataFrame(index=index_lst)
    df_height_all = pd.DataFrame(index=index_lst)
    for i in list_of_files_all:
        
        df = pd.read_csv(i, sep="\t", header=0, index_col=0)
        df = df.groupby(df.index).sum()
        try:
            df_area = pd.DataFrame(df["Area"].values, index=df.index, columns=[i])
            df_area_all = df_area_all.join(df_area, sort=False)
            df_area_all.fillna(0).to_csv("area.txt", sep="\t")
        except KeyError:
            print("Area column has not been found")
            pass
        try:
            df_height = pd.DataFrame(df["Height"].values, index=df.index, columns=[i])
            df_height_all = df_height_all.join(df_height, sort=False)
        except KeyError:
            print("Height column has not been found")
            pass
    df_area_all.fillna(0).to_csv("strely\\area.txt", sep="\t")
    df_height_all.fillna(0).to_csv("strely\\height.txt", sep="\t")


def main():
    print("Getting files and indexes")
    l_o_f = get_files()
    index_list = get_names_compounds(l_o_f)
    print("Creating tables...")
    get_concat_tables(l_o_f, index_list)
    print("DONE, CHECK YOUR RESULTS")


main()
