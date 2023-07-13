# -*- coding: utf-8 -*-
"""Main function for data processing."""
import datetime
import logging
import os
import tkinter as tk

import data_cleaning
import matrix_gen
import merge_ratios
import sort_by_name


class DPMain(tk.Tk):
    """Base class of data processing package."""

    def __init__(self):
        """
        Initialize the DP main class
        """
        super().__init__()
        self.__init_window()
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [:::%(name)s:::] [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler(f"logs{os.sep}log_{datetime.date.today()}_"
                                    f"{datetime.datetime.now().strftime('%H_%M_%S')}.log"),
                logging.StreamHandler()
            ]
        )
        self.mainloop()

    def __init_window(self) -> None:
        """Initialize app window."""
        self.title("Data processing pipe interface")
        self.rowconfigure(0, minsize=100, weight=1)
        self.columnconfigure(3, weight=1, minsize=50)
        btn_sum_table = tk.Button(text="Create summary table", command=sort_by_name.SortByName)
        btn_sum_table.grid(row=0, column=0, sticky="nsew", pady=10, padx=10)

        btn_matrix_gen = tk.Button(text="Create matrices", command=matrix_gen.MatrixGen)
        btn_matrix_gen.grid(row=0, column=1, sticky="nsew", pady=10, padx=10)

        btn_cleaning = tk.Button(text="Data Cleaning", command=data_cleaning.DataCleaning)
        btn_cleaning.grid(row=0, column=2, sticky="nsew", pady=10, padx=10)

        btn_merging = tk.Button(text="Merge tables", command=merge_ratios.MergeTables)
        btn_merging.grid(row=0, column=3, sticky="nsew", pady=10, padx=10)


if __name__ == "__main__":
    DPMain()
