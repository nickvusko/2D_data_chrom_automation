# -*- coding: utf-8 -*-
"""Main function for matrix generator."""

import logging
import numpy as np
import os
import pandas as pd
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilenames


class MatrixGen:
    """Class of the matrix generator instance."""

    def __init__(self):
        """Initialize the MatrixGen class."""
        self.__input_path = f"{os.getcwd()}{os.sep}"
        self.__result_path = f"{os.getcwd()}{os.sep}"
        self.__df = pd.DataFrame()
        self.log = logging.getLogger(__name__)
        self.log.debug("Create matrices instance running.")
        self.master = tk.Tk()
        self.setup_window()
        self.master.mainloop()

    def setup_window(self) -> None:
        """Set up GUI window."""
        self.master.title("Matrix generator interface")
        self.master.geometry("600x250")

        # input folder line
        tk.Label(self.master, text="Currently set input folder:").grid(row=0, column=0, sticky="W", pady=10)
        in_entry = tk.Entry(self.master, bg="white", width=50)
        in_entry.insert(index=0, string=self.__input_path)
        in_entry.config(state=tk.DISABLED)
        in_entry.grid(row=0, column=1, pady=10)
        in_button = tk.Button(self.master, text="Change input folder", command=lambda: self.get_path(in_entry))
        in_button.grid(row=0, column=2, pady=10)

        # output folder line
        tk.Label(self.master, text="Currently set output folder:").grid(row=1, column=0, sticky="W", pady=10)
        out_entry = tk.Entry(self.master, bg="white", width=50)
        out_entry.insert(index=0, string=self.__result_path)
        out_entry.config(state=tk.DISABLED)
        out_entry.grid(row=1, column=1, pady=10)
        out_button = tk.Button(self.master, text="Change output folder",
                               command=lambda: self.get_path(out_entry, False))
        out_button.grid(row=1, column=2, pady=10)

        # start button
        add_confirm = tk.Button(self.master, text="Start", command=self.get_matrix)
        add_confirm.grid(row=4, column=1, pady=10, sticky="W")
        add_confirm.config(font=26)

        # close button
        close_button = tk.Button(self.master, text="Close", command=self.master.destroy)
        close_button.grid(row=4, column=1, pady=10, sticky="E")
        close_button.config(font=26)

    def get_path(self, entry: tk.Entry, input_folder: bool = True) -> None:
        """Get working folders.

        :param entry: entry widget
        :param input_folder: True if returning value concerns inout folder, False for output folder
        """
        if input_folder:
            self.__input_path = askopenfilenames(title="Select input file", initialdir=self.__input_path,
                                                 filetypes=[("Text files", "*.txt")], defaultextension=".txt")
            entry.config(state=tk.NORMAL)
            entry.delete(0, tk.END)
            entry.insert(0, self.__input_path)
            entry.config(state=tk.DISABLED)
            self.log.info(f"Source data file set to {self.__input_path}.")
        else:
            self.__result_path = askdirectory(title="Select result folder", initialdir=self.__result_path)
            entry.config(state=tk.NORMAL)
            entry.delete(0, tk.END)
            entry.insert(0, self.__result_path)
            entry.config(state=tk.DISABLED)
            self.log.info(f"Output data folder set to {self.__result_path}.")

    def get_column_names(self) -> tuple[list, list]:
        """Get list of compound and transfer them into compoundX/compoundY format.

        :returns: tuple [list of compounds, list of ratio names]
        """
        list_of_renames = []
        list_of_compounds = [cmpd for cmpd in self.__df.columns if cmpd != "Class"]
        count = 0
        for _ in list_of_compounds:
            for i in range(count, len(list_of_compounds)):
                list_of_renames.append(f"{list_of_compounds[count]}/{list_of_compounds[i]}")
            count += 1
        del count
        self.log.info(f"{len(list_of_compounds)} different compounds collected.")
        return list_of_compounds, list_of_renames

    def get_matrix(self) -> None:
        """Generate matrices for all samples and create summary single row representations."""
        for file in self.__input_path:
            self.__df = pd.read_csv(file, sep="\t", header=0, index_col=0)
            lst_cmpd, lst_rename = self.get_column_names()
            final_table = pd.DataFrame()
            class_tags = self.__df["Class"]
            self.__df = self.__df.drop("Class", axis=1)
            for sample in self.__df.index:
                self.log.info(f"Generating matrix for {sample}.")
                array = np.column_stack(self.__df.loc[sample, :])
                array2 = array.copy()
                with np.errstate(divide="ignore", invalid="ignore"):
                    df_sample = pd.DataFrame(array.reshape(-1, 1)/array2, index=lst_cmpd, columns=lst_cmpd)
                    df_sample = df_sample.fillna("0")
                    df_sample.to_csv(f"{self.__result_path}{os.sep}{sample}.txt", sep="\t")
                    df_single_row = df_sample.where(np.triu(np.ones(df_sample.shape), k=0).astype(np.bool_))
                    df_single_row = pd.DataFrame(df_single_row.stack().to_frame().values).T
                    df_single_row = df_single_row.rename(index={0: sample})
                    final_table = pd.concat([final_table, df_single_row])
                    self.log.info(f"{sample} single row representation was added to the summary file")
            final_table = final_table.replace(np.inf, 0)
            final_table = final_table.set_axis([lst_rename], axis=1)
            final_table["Class"] = class_tags
            if len(class_tags.unique()) > 1:
                final_table.to_csv(f"{self.__result_path}{os.sep}summary_singlerow_summary.txt", sep="\t")
            else:
                final_table.to_csv(f"{self.__result_path}{os.sep}summary_singlerow_{class_tags.unique()[0]}.txt",
                                   sep="\t")
        self.log.info("Generation of matrices done, check results.")


if __name__ == "__main__":
    MatrixGen()
