# Author:  NIKOLA LADISLAVOVA, nikola.ladislavova@gmail.com
# Created: Feb 25, 2021
# Purpose: Chromatography

# Copyright (c) 2021, Nikola Ladislavova, UCT, Prague

import pandas as pd
import numpy as np


# FUNCTIONS

def get_column_names(start_table_area):
    list_of_renames = []
    list_of_compounds = []
    for compound in start_table_area.index:
        list_of_compounds.append(compound)
    count = 0
    for element in list_of_compounds:
        for ilimint in range(count,len(list_of_compounds)):
            rename = list_of_compounds[count]+"/"+list_of_compounds[ilimint]
            list_of_renames.append(rename)  
        count = count+1
    return list_of_renames


def get_matrix_height(start_table_height, list_of_renames):
    final_table_height = pd.DataFrame()
    for column in start_table_height.iteritems():
        column_name = column[0]
        column_x = column[1]
        array = np.column_stack(column_x)
        array2 = array
        with np.errstate(divide="ignore", invalid="ignore"):
            result = array.reshape(-1, 1)/array2
            df_matrix = pd.DataFrame(result)
            df_matrix = df_matrix.fillna("0")
            df_matrix.to_csv("results/height/height_matrix_"+column_name+".txt", sep="\t")
            df_matrix = df_matrix.where(np.triu(np.ones(df_matrix.shape), k=0).astype(np.bool))
            df_matrix = pd.DataFrame(df_matrix.stack().to_frame().values).T
            df_matrixx = df_matrix.rename(index={0: column_name})
            final_table_height = final_table_height.append(df_matrixx)
    final_table_height.set_axis([list_of_renames], axis=1, inplace=True)
    final_table_height.to_csv("results/height/height_singlerow.txt", sep="\t")


def get_matrix_area(start_table_area, list_of_renames):
    final_table_area = pd.DataFrame()
    for column in start_table_area.iteritems():
        column_name = column[0]
        column_x = column[1]
        array = np.column_stack(column_x)
        array2 = array
        with np.errstate(divide = "ignore", invalid = "ignore"):
            result = array.reshape(-1, 1)/array2
            df_matrix = pd.DataFrame(result)
            df_matrix = df_matrix.fillna("0")
            df_matrix.to_csv("results/area/area_matrix_"+column_name+".txt", sep = "\t")
            df_matrix = df_matrix.where(np.triu(np.ones(df_matrix.shape), k=0).astype(np.bool))
            df_matrix = pd.DataFrame(df_matrix.stack().to_frame().values).T
            df_matrixx = df_matrix.rename(index={0: column_name})
            final_table_area = final_table_area.append(df_matrixx)
    final_table_area.set_axis([list_of_renames], axis=1, inplace=True)
    final_table_area.to_csv("results/area/area_singlerow.txt", sep="\t")


def main():
    print("Set up environment")
    #########################
    # get input from the user#
    a = ((input("Enter the name of file for area matrix: ")) + ".txt")
    h = ((input("Enter the name of file for height matrix: ")) + ".txt")
    if a != ".txt" and h != ".txt":
        start_table_height = pd.read_csv(h, sep="\t", header=0, index_col=0)
        start_table_area = pd.read_csv(a, sep="\t", header=0, index_col=0)

        print("Getting column names...")
        list_of_renames = get_column_names(start_table_area)

        print("Creating matrices for areas and heights")
        get_matrix_height(start_table_height, list_of_renames)
        get_matrix_area(start_table_area, list_of_renames)
    elif a != ".txt" and h == ".txt":
        start_table_area = pd.read_csv(a, sep="\t", header=0, index_col=0)

        print("Getting column names...")
        list_of_renames = get_column_names(start_table_area)

        print("Creating matrix for areas only")
        get_matrix_area(start_table_area, list_of_renames)
    elif a == ".txt" and h != ".txt":
        start_table_height = pd.read_csv(a, sep="\t", header=0, index_col=0)

        print("Getting column names...")
        list_of_renames = get_column_names(start_table_height)

        print("Creating matrix for heights only")
        get_matrix_height(start_table_height, list_of_renames)
    else:
        print("No valid arguments for generating ration matrices were given.")


main()
