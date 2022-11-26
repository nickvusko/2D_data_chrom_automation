# -*- coding: utf-8 -*-
# Author:  NIKOLA LADISLAVOVA, nikola.ladislavova@gmail.com
# Created: Feb 25, 2021
# Purpose: Chromatography


import pandas as pd
import numpy as np
import sys


def main():
    fh = str((input("Enter the name of the file: ")))
    df_stat = pd.read_csv(fh+".txt", index_col=0, header=0, sep="\t")
    df_stat = df_stat.replace(np.inf, 0)
    if len(df_stat.index) == 1:
        colm_order = df_stat.sort_values
        colm_order = colm_order.replace(1, 0)
        colm_orderx = colm_order.loc[:, (colm_order != 0).any()]
        colm_orderx = colm_orderx.sort_values(by=colm_orderx.index[-1], axis=1)
        colm_orderx.to_csv("ratio_"+fh+".txt", sep="\t")
        print("DONE, PLEASE CHECK YOUR RESULTS")
        sys.exit()
    else:
        zerocount = int(input("Mow many zeros in column are acceptable? [%] "))
        colm_order = df_stat.iloc[:, (df_stat.std()).argsort()]
        colm_order = colm_order.replace(1, 0)
        colm_orderx = colm_order.loc[:, (colm_order != 0).any()]
        row_count = len(colm_orderx.index)
        one_perc = row_count/100
        final_table = colm_orderx.loc[:, (((row_count-colm_orderx.astype(bool).sum(axis=0))/one_perc) <= zerocount)]
        final_table.to_csv("ratio_"+fh+".txt", sep="\t")
        print("DONE, PLEASE CHECK YOUR RESULTS")


main()


