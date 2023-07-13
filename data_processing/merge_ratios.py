# -*- coding: utf-8 -*-
"""Main function for ratio merge."""

import logging
import numpy as np
import os
import pandas as pd
import tkinter as tk
from tkinter.filedialog import askopenfilenames, asksaveasfilename


class MergeTables:
    """Class of the merge tables instance."""

    def __init__(self):
        """Initialize the MergeRatios class."""
        self.__input_path = f"{os.getcwd()}{os.sep}"
        self.__result_path = f"{os.getcwd()}{os.sep}"
        self.__df = pd.DataFrame()
        self.__toleration = 30
        self.__top_ratios = 300
        self.log = logging.getLogger(__name__)
        self.log.debug("Merge tables instance running.")
        self.master = tk.Tk()
        self.__clean = tk.IntVar(self.master)
        self.__merge_style = tk.IntVar(self.master)
        self.setup_window()
        self.master.mainloop()

    def setup_window(self) -> None:
        """Set up GUI window."""
        self.master.title("Merge tables")

        # list of files
        list_label = tk.Label(self.master, text=f"List of loaded files: {len(self.__input_path)}.")
        list_label.grid(row=2, column=0, sticky="WE", pady=10)

        # input folder line
        tk.Label(self.master, text="Choose input file folder:").grid(row=0, column=0, sticky="W", pady=10)
        in_entry = tk.Entry(self.master, bg="white", width=50)
        in_entry.insert(index=0, string=self.__input_path)
        in_entry.config(state=tk.DISABLED)
        in_entry.grid(row=0, column=1, pady=10)
        in_button = tk.Button(self.master, text="Change input folder", command=lambda: self.get_path(in_entry,
                                                                                                     list_label))
        in_button.grid(row=0, column=2, pady=10)

        # output folder line
        tk.Label(self.master, text="Currently set output file:").grid(row=1, column=0, sticky="W", pady=10)
        out_entry = tk.Entry(self.master, bg="white", width=50)
        out_entry.insert(index=0, string=self.__result_path)
        out_entry.config(state=tk.DISABLED)
        out_entry.grid(row=1, column=1, pady=10)
        out_button = tk.Button(self.master, text="Change output file(s)",
                               command=lambda: self.get_path(out_entry, input_folder=False))
        out_button.grid(row=1, column=2, pady=10)

        # cleaning settings
        zero_label = tk.Label(self.master, text=f"Max % of zero values: {self.__toleration}")
        zero_button = tk.Button(self.master, text="Set", command=lambda: self.set_toleration(zero_label))

        # add cleaning
        checkbox_class = tk.Checkbutton(self.master, text="Add data cleaning step", variable=self.__clean, onvalue=1,
                                        offvalue=0, command=lambda: self.display_cleaning(zero_label, zero_button))
        checkbox_class.grid(row=3, column=0, pady=10)

        # top ratios
        top_label = tk.Label(self.master, text=f"Number of columns with least SD: {self.__top_ratios}")
        top_label.grid(row=2, column=1, sticky="WE", pady=10)

        top_button = tk.Button(self.master, text="Set", command=lambda: self.set_ratios(top_label))
        top_button.grid(row=2, column=1, sticky="E", pady=10)

        # merging settings
        merging_label = tk.Label(self.master, text=f"Set merging rule:")
        merging_label.grid(row=4, column=0, sticky="N", pady=10)

        merging_all = tk.Radiobutton(self.master, text="Intersection", variable=self.__merge_style, value=0)
        merging_all.grid(row=4, column=1, sticky="W")

        merging_all = tk.Radiobutton(self.master, text="Union", variable=self.__merge_style, value=1)
        merging_all.grid(row=5, column=1, sticky="W")

        # start button
        add_confirm = tk.Button(self.master, text="Start", command=self.merge_ratios)
        add_confirm.grid(row=6, column=1, pady=10, sticky="W")
        add_confirm.config(font=26)

        # close button
        close_button = tk.Button(self.master, text="Close", command=self.master.destroy)
        close_button.grid(row=6, column=1, pady=10, sticky="E")
        close_button.config(font=26)

    def get_path(self, entry: tk.Entry, label: tk.Label = None, input_folder: bool = True) -> None:
        """Get working folders.

        :param entry: entry widget
        :param input_folder: True if returning value concerns inout folder, False for output folder
        :param label: label widget
        """
        if input_folder:
            self.__input_path = askopenfilenames(title="Select input folder", initialdir=self.__input_path)
            entry.config(state=tk.NORMAL)
            entry.delete(0, tk.END)
            entry.insert(0, self.__input_path)
            entry.config(state=tk.DISABLED)
            self.log.info(f"Input files: {self.__input_path}.")
            label.config(text=f"List of loaded files: {len( self.__input_path)}")
            label.update()
        else:
            self.__result_path = asksaveasfilename(title="Save as...", initialdir=self.__result_path,
                                                   filetypes=[("Text files", "*.txt")], defaultextension=".txt")
            entry.config(state=tk.NORMAL)
            entry.delete(0, tk.END)
            entry.insert(0, self.__result_path)
            entry.config(state=tk.DISABLED)
            self.log.info(f"Output file(s) {self.__result_path}.")

    def set_toleration(self, label: tk.Label) -> None:
        """Change setting of the null toleration level.

        :param label: label widget
        """
        top_lvl = tk.Toplevel()
        top_lvl.title("Set new NULL toleration level:")

        tk.Label(top_lvl, text=f"New level [%]:").grid(row=0, column=0, pady=10, sticky="WE")
        toleration_entry = tk.Entry(top_lvl, bg="white", width=10)
        toleration_entry.grid(row=0, column=1, pady=10, sticky="W")
        tk.Button(top_lvl, text="Set", command=lambda: self.update_destroy_toleration(toleration_entry, label,
                                                                                      top_lvl)).grid(row=0, column=1,
                                                                                                     pady=10,
                                                                                                     sticky="E")

    def set_ratios(self, label: tk.Label) -> None:
        """Change setting of the null toleration level.

        :param label: label widget
        """
        top_lvl = tk.Toplevel()
        top_lvl.title("Set number of columns with least SD:")

        tk.Label(top_lvl, text=f"Set number:").grid(row=0, column=0, pady=10, sticky="WE")
        toleration_entry = tk.Entry(top_lvl, bg="white", width=10)
        toleration_entry.grid(row=0, column=1, pady=10, sticky="W")
        tk.Button(top_lvl, text="Set", command=lambda: self.update_destroy_ratios(toleration_entry, label, top_lvl)) \
            .grid(row=0, column=1, pady=10, sticky="E")

    def update_destroy_toleration(self, entry: tk.Entry, label: tk.Label, window: tk.Toplevel) -> None:
        """Update value of the label and destroy current window"""
        self.__toleration = entry.get()
        self.log.info(f"Toleration to zero values changed to {self.__toleration}")
        label.config(text=f"Max % of zero values: {self.__toleration}")
        label.update()
        window.destroy()

    def update_destroy_ratios(self, entry: tk.Entry, label: tk.Label, window: tk.Toplevel):
        """Update value of the label and destroy current window"""
        self.__top_ratios = entry.get()
        self.log.info(f"Column count changed to {self.__top_ratios}")
        label.config(text=f"Number of columns with least SD: {self.__top_ratios}")
        label.update()
        window.destroy()

    def display_cleaning(self, zero_label: tk.Label, zero_button: tk.Button):
        """Display cleaning setting if checked."""
        if self.__clean.get() == 1:
            self.log.info("Data cleaning step added to the pipe.")
            zero_label.grid(row=3, column=1, sticky="WE", pady=10)

            zero_button.grid(row=3, column=1, sticky="E", pady=10)
        else:
            self.log.info("Data cleaning step removed from the pipe.")
            zero_label.grid_forget()
            zero_button.grid_forget()

    def call_cleaning(self, df: pd.DataFrame) -> pd.DataFrame:
        """Execute data-cleaning.

        :param df: pd Dataframe
        :returns: cleaned dataframe
        """
        tags = df["Class"]
        df = df.drop("Class", axis=1)
        if len(df.index) == 1:
            self.log.info("Only one row (sample) found. Zero values will be dropped and columns will be "
                          "sorted in ascending manner")
            df = df.sort_values
            final_df = df.sort_values(by=df.index[-1], axis=1)
            final_df["Class"] = tags
            return final_df
        else:
            self.log.info("Sorting columns according their standard deviation.")
            df_sorted = df.iloc[:, (df.std()).argsort()]
            df_sorted = df_sorted.replace(1, 0)
            row_count = len(df_sorted.index)
            self.log.info(f"Dropping columns with more than {self.__toleration} % zero values.")
            final_table = df_sorted.loc[:, (((row_count - df_sorted.astype(bool).sum(axis=0)) /
                                             (row_count / 100)) <= self.__toleration)]
            final_table["Class"] = tags
            return final_table

    def merge_ratios(self) -> None:
        """Main function for merging tables."""
        list_of_columns, class_tags = self.get_columns()
        self.__df = pd.DataFrame(columns=list_of_columns)
        for file in self.__input_path:
            pd_to_merge = pd.read_csv(f"{file}", sep="\t", header=0, index_col=0)
            self.log.info(f"Filtering first {self.__top_ratios} columns with the least SD from file "
                          f"{file.split(os.sep)[-1]}")
            pd_to_merge = pd_to_merge.drop("Class", axis=1)
            df_sorted = pd_to_merge.iloc[:, (pd_to_merge.std()).argsort()]
            self.__df = self.__df.T.join(df_sorted.T, sort=False).T

        self.__df = self.__df.fillna(0)
        self.__df["Class"] = class_tags
        if self.__clean.get():
            self.log.info(f"Applying data cleaning step (toleration set to {self.__toleration}%.")
            self.__df = self.call_cleaning(self.__df)
        self.__df.to_csv(f"{self.__result_path}", sep="\t")
        self.log.info("Merging done.")

    def get_columns(self) -> tuple[list, list]:
        """Get relevant column names

        :returns: tuple(list of relevant columns, list of class tags)
        """
        self.log.info("Gather relevant column names.")
        start_df = pd.read_csv(self.__input_path[0], index_col=0, header=0, sep="\t")
        tag_list = [x for x in start_df["Class"]]
        start_df = start_df.drop("Class", axis=1)
        start_df = start_df.replace(np.inf, 0)
        start_df = start_df.replace(1, 0)
        start_df = start_df.loc[:, (start_df != 0).any()]
        start_df_sorted = start_df.iloc[:, (start_df.std()).argsort()]
        lst_of_columns = [x for x in start_df_sorted.columns[:self.__top_ratios]]
        for file in self.__input_path[1:]:
            df = pd.read_csv(file, index_col=0, header=0, sep="\t")
            tag_list += [x for x in df["Class"]]
            df = df.drop("Class", axis=1)
            df = df.replace(np.inf, 0)
            df = df.replace(1, 0)
            df = df.loc[:, (df != 0).any()]
            df_sorted = df.iloc[:, (df.std()).argsort()]
            if self.__merge_style.get() == 0:  # intersection
                for clmn in lst_of_columns:
                    if clmn not in [x for x in df_sorted.columns[:self.__top_ratios]]:
                        lst_of_columns.remove(clmn)
            else:  # union
                for clmn in [x for x in df_sorted.columns[:self.__top_ratios]]:
                    if clmn not in lst_of_columns:
                        lst_of_columns.append(clmn)

        self.log.info(f"Gathered column names ({'Union' if self.__merge_style.get() == 1 else 'Intersection'}): "
                      f"{lst_of_columns}")

        return lst_of_columns, tag_list


if __name__ == "__main__":
    MergeTables()
