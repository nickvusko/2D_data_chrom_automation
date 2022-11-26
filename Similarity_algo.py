# -*- coding: utf-8 -*-
# Author:  NIKOLA LADISLAVOVA, nikola.ladislavova@gmail.com
# Created: Feb 25, 2021
# Purpose: Chromatography

import pandas as pd
import numpy as np
from scipy import spatial
from scipy.stats import spearmanr
from scipy.stats import kendalltau

list_of_files_std = []
list_of_files_anal = []

#  this block of code builds up the relevant ratios (column names for the final
#  table) from the input files
print("Create a list of standard files. When you are done, press Enter.")
while True:
    inpstd = (input("File name: "))
    if inpstd != "":
        list_of_files_std.append(inpstd + ".txt")
        print("So far added:_", list_of_files_std)
    else:
        break

#  this block of code picks up the relevant ratios (column names of the final
#  table) from the input files
print("Create a list of files for analysis. When you are done, press Enter.")
while True:
    input_anal = (input("File name: "))
    if input_anal != "":
        list_of_files_anal.append(input_anal + ".txt")
        print("So far added:_", list_of_files_anal)
    else:
        break

method = int(input("""Which method you want to apply?
                   1 - Euclidian distance
                   2 - Cosine similarity
                   3 - Pearson´s correlation
                   4 - Spearman´s correlation
                   5 - Kendall´s tau
                   """))
if method == 1:
    for anal in list_of_files_anal:
        sheet_anal = pd.read_csv(anal, sep="\t", header=0).set_index("Unnamed: 0")
        sub_df = pd.DataFrame()
        for index, data in sheet_anal.iterrows():
            data_df = pd.DataFrame(data).transpose()
            for std in list_of_files_std:
                sheet_std = pd.read_csv(std, sep="\t", header=0).set_index("Unnamed: 0")
                for nd, values in sheet_std.iterrows():
                    values_df = pd.DataFrame(values).transpose()
                    work_df = values_df
                    columncount = len(values_df.columns)
                    pre_square_sum = 0
                    for el in range(0, columncount):
                        pre_square_sum += ((float(values_df.iat[0, el]) - float(data_df.iat[0, el])) ** 2) ** (1 / 2)
                    work_df["Euclidian Distance"] = pre_square_sum
                    name1 = str(data_df.index.values[0])
                    name2 = str(values_df.index.values[0])
                    name = name1 + " vs " + name2
                    work_df = work_df.rename(index={name2: name})
                    work_df = work_df["Euclidian Distance"]
                    sub_df = pd.concat([sub_df, work_df], sort="True")
    sub_df = sub_df.rename(columns={0: "Euclidian Distance"})
    sub_df.to_csv("result_" + anal + "_" + std + "_Euclidian Distance.txt", sep="\t")
if method == 2:
    for anal in list_of_files_anal:
        sheet_anal = pd.read_csv(anal, sep="\t", header=0).set_index("Unnamed: 0")
        sub_df = pd.DataFrame()
        for index, data in sheet_anal.iterrows():
            data_df = pd.DataFrame(data).transpose()
            data_array = data_df.to_numpy()
            for std in list_of_files_std:
                sheet_std = pd.read_csv(std, sep="\t", header=0).set_index("Unnamed: 0")
                for nd, values in sheet_std.iterrows():
                    values_df = pd.DataFrame(values).transpose()
                    work_df = values_df
                    values_array = values_df.to_numpy()
                    similarity = 1 - spatial.distance.cosine(values_array, data_array)
                    work_df["Cosine Similarity"] = similarity
                    name1 = str(data_df.index.values[0])
                    name2 = str(values_df.index.values[0])
                    name = name1 + " vs " + name2
                    work_df = work_df.rename(index={name2: name})
                    work_df = work_df["Cosine Similarity"]
                    sub_df = pd.concat([sub_df, work_df], sort="True")
    sub_df = sub_df.rename(columns={0: "Cosine Similarity"})
    print(sub_df)
    sub_df.to_csv("result_" + anal + "_" + std + "_Cosine Similarity.txt", sep="\t")
if method == 3:
    for anal in list_of_files_anal:
        sheet_anal = pd.read_csv(anal, sep="\t", header=0).set_index("Unnamed: 0")
        sub_df = pd.DataFrame()
        column_count = len(sheet_anal.columns)
        for index, data in sheet_anal.iterrows():
            data_df = pd.DataFrame(data).transpose()
            data_array = data_df.to_numpy()
            for std in list_of_files_std:
                sheet_std = pd.read_csv(std, sep="\t", header=0).set_index("Unnamed: 0")
                for nd, values in sheet_std.iterrows():
                    values_df = pd.DataFrame(values).transpose()
                    work_df = values_df
                    values_array = values_df.to_numpy()
                    data_mean = data_array.mean()
                    values_mean = values_array.mean()
                    data_less = data_array - data_mean
                    values_less = values_array - values_mean
                    numerator = (np.sum(data_less * values_less))
                    denominator = np.sqrt((np.sum(data_less ** 2)) * (np.sum(values_less ** 2)))
                    similarity = numerator / denominator
                    work_df["Pearson Correlation"] = similarity
                    name1 = str(data_df.index.values[0])
                    name2 = str(values_df.index.values[0])
                    name = name1 + " vs " + name2
                    work_df = work_df.rename(index={name2: name})
                    work_df = work_df["Pearson Correlation"]
                    sub_df = pd.concat([sub_df, work_df], sort="True")
    sub_df = sub_df.rename(columns={0: "Pearson Correlation"})
    print(sub_df)
    sub_df.to_csv("result_" + anal + "_" + std + "_Pearson Correlation.txt", sep="\t")

if method == 4:
    for anal in list_of_files_anal:
        sheet_anal = pd.read_csv(anal, sep="\t", header=0).set_index("Unnamed: 0")
        sub_df = pd.DataFrame()
        column_count = len(sheet_anal.columns)
        for index, data in sheet_anal.iterrows():
            data_df = pd.DataFrame(data).transpose()
            data_array = data_df.to_numpy()
            for std in list_of_files_std:
                sheet_std = pd.read_csv(std, sep="\t", header=0).set_index("Unnamed: 0")
                for nd, values in sheet_std.iterrows():
                    values_df = pd.DataFrame(values).transpose()
                    work_df = values_df
                    values_array = values_df.to_numpy()
                    similarity, _ = spearmanr(values_array.T, data_array.T)
                    work_df["Spearman Correlation"] = similarity
                    name1 = str(data_df.index.values[0])
                    name2 = str(values_df.index.values[0])
                    name = name1 + " vs " + name2
                    work_df = work_df.rename(index={name2: name})
                    work_df = work_df["Spearman Correlation"]
                    sub_df = pd.concat([sub_df, work_df], sort="True")
    sub_df = sub_df.rename(columns={0: "Spearman Correlation"})
    print(sub_df)
    sub_df.to_csv("result_" + anal + "_" + std + "_Spearman Correlation.txt", sep="\t")

if method == 5:
    for anal in list_of_files_anal:
        sheet_anal = pd.read_csv(anal, sep="\t", header=0).set_index("Unnamed: 0")
        sub_df = pd.DataFrame()
        column_count = len(sheet_anal.columns)
        for index, data in sheet_anal.iterrows():
            data_df = pd.DataFrame(data).transpose()
            data_array = data_df.to_numpy()
            for std in list_of_files_std:
                sheet_std = pd.read_csv(std, sep="\t", header=0).set_index("Unnamed: 0")
                for nd, values in sheet_std.iterrows():
                    values_df = pd.DataFrame(values).transpose()
                    work_df = values_df
                    values_array = values_df.to_numpy()
                    similarity, _ = kendalltau(values_array.T, data_array.T)
                    work_df["Kendall Correlation"] = similarity
                    name1 = str(data_df.index.values[0])
                    name2 = str(values_df.index.values[0])
                    name = name1 + " vs " + name2
                    work_df = work_df.rename(index={name2: name})
                    work_df = work_df["Kendall Correlation"]
                    sub_df = pd.concat([sub_df, work_df], sort="True")
    sub_df = sub_df.rename(columns={0: "Kendall Correlation"})
    print(sub_df)
    sub_df.to_csv("result_" + anal + "_" + std + "_Kendall Correlation.txt", sep="\t")
