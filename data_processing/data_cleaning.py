# -*- coding: utf-8 -*-
"""Main function for data cleaning."""

import logging
import os
import pandas as pd
import tkinter as tk
from tkinter.filedialog import askopenfilenames, asksaveasfilename


class DataCleaning:
    """Class of the data cleaning instance."""

    def __init__(self):
        """Initialize the SortByName class."""
        self.__input_path = f"{os.getcwd()}{os.sep}"
        self.__result_path = f"{os.getcwd()}{os.sep}"
        self.__df = pd.DataFrame()
        self.__class_tags = []
        self.__toleration = 30
        self.log = logging.getLogger(__name__)
        self.log.debug("Initializing data cleaning instance.")
        self.master = tk.Tk()
        self.__split = tk.BooleanVar(self.master)
        self.setup_window()
        self.master.mainloop()

    def setup_window(self) -> None:
        """Set up GUI window."""
        self.master.title("Data cleaning interface")
        self.master.geometry("600x250")

        # input folder line
        tk.Label(self.master, text="Currently set input file:").grid(row=0, column=0, sticky="W", pady=10)
        in_entry = tk.Entry(self.master, bg="white", width=50)
        in_entry.insert(index=0, string=self.__input_path)
        in_entry.config(state=tk.DISABLED)
        in_entry.grid(row=0, column=1, pady=10)
        in_button = tk.Button(self.master, text="Change input file", command=lambda: self.get_path(in_entry))
        in_button.grid(row=0, column=2, pady=10)

        # output folder line
        tk.Label(self.master, text="Currently set output file(s):").grid(row=1, column=0, sticky="W", pady=10)
        out_entry = tk.Entry(self.master, bg="white", width=50)
        out_entry.insert(index=0, string=self.__result_path)
        out_entry.config(state=tk.DISABLED)
        out_entry.grid(row=1, column=1, pady=10)
        out_button = tk.Button(self.master, text="Change output file(s)",
                               command=lambda: self.get_path(out_entry, False))
        out_button.grid(row=1, column=2, pady=10)

        # add class tags
        checkbox_class = tk.Checkbutton(self.master, text="Split classes", variable=self.__split,
                                        command=lambda: self.__split.get())
        checkbox_class.grid(row=2, column=0, pady=10, sticky="WE")

        # zero toleration
        zero_label = tk.Label(self.master, text=f"Max % of zero values: {self.__toleration}")
        zero_label.grid(row=2, column=1, sticky="W", pady=10)

        zero_button = tk.Button(self.master, text="Set", command=lambda: self.set_toleration(zero_label))
        zero_button.grid(row=2, column=1, pady=10)

        # start button
        add_confirm = tk.Button(self.master, text="Start", command=self.zero_values)
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
            self.log.info(f"Input file: {self.__input_path}.")
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
        top_lvl.geometry("300x250")

        tk.Label(top_lvl, text=f"New level [%]:").grid(row=0, column=0, pady=10, sticky="WE")
        toleration_entry = tk.Entry(top_lvl, bg="white", width=10)
        toleration_entry.grid(row=0, column=1, pady=10, sticky="W")
        tk.Button(top_lvl, text="Set", command=lambda: self.update_destroy(toleration_entry, label, top_lvl)) \
            .grid(row=0, column=1, pady=10, sticky="E")

    def update_destroy(self, entry: tk.Entry, label: tk.Label, window: tk.Toplevel) -> None:
        """Update value of the label and destroy current window"""
        self.__toleration = entry.get()
        label.config(text=f"Max % of zero values: {self.__toleration}")
        label.update()
        window.destroy()

    def zero_values(self) -> None:
        """Drop zero values and sort columns."""
        for i in self.__input_path:
            df_start = pd.read_csv(i, index_col=0, header=0, sep="\t")
            tags = df_start["Class"]
            df = df_start.drop("Class", axis=1)
            if not self.__split.get():
                if len(df.index) == 1:
                    self.log.info("Only one row (sample) found. Zero values will be dropped and columns will be "
                                  "sorted in ascending manner")
                    df = df.sort_values
                    df = df.replace(1, 0)
                    df = df.loc[:, (df != 0).any()]
                    final_df = df.sort_values(by=df.index[-1], axis=1)
                    final_df.loc[:, "Class"] = tags
                    final_df.to_csv(f"sorted_{self.__result_path}", sep="\t")
                else:
                    self.log.info("Sorting columns according their standard deviation.")
                    df_sorted = df.iloc[:, (df.std()).argsort()]
                    df_sorted = df_sorted.replace(1, 0)
                    row_count = len(df_sorted.index)
                    self.log.info(f"Dropping columns with more than {self.__toleration} % zero values.")
                    final_table = df_sorted.loc[:, (((row_count - df_sorted.astype(bool).sum(axis=0)) /
                                                     (row_count / 100)) <= self.__toleration)]
                    final_table.loc[:, "Class"] = tags
                    final_table.to_csv(f"{self.__result_path}", sep="\t")
            else:
                for tag in tags.unique():
                    class_df = df[df_start["Class"] == tag]
                    if len(class_df.index) == 1:
                        self.log.info(f"Only one sample (tag {tag}) found. Zero values will be dropped and columns will be "
                                      "sorted in ascending manner")
                        class_df = class_df.sort_values
                        class_df = class_df.replace(1, 0)
                        class_df = class_df.loc[:, (class_df != 0).any()]
                        final_df = class_df.sort_values(by=class_df.index[-1], axis=1)
                        final_df.loc[:, "Class"] = tag
                        self.__result_path = f"{self.__result_path.split('.txt')}_class_{tag}.txt"
                        final_df.to_csv(f"sorted_{self.__result_path}", sep="\t")
                    else:
                        self.log.info(f"Sorting columns according their standard deviation for class {tag}.")
                        df_sorted = class_df.iloc[:, (class_df.std()).argsort()]
                        df_sorted = df_sorted.replace(1, 0)
                        row_count = len(df_sorted.index)
                        self.log.info(f"Dropping columns with more than {self.__toleration} % zero values.")
                        final_table = df_sorted.loc[:, (((row_count - df_sorted.astype(bool).sum(axis=0)) /
                                                         (row_count / 100)) <= int(self.__toleration))]
                        final_table.loc[:, "Class"] = tag
                        path = f"{self.__result_path.split('.txt')[0]}_class_{tag}.txt"
                        final_table.to_csv(f"{path}", sep="\t")
        self.log.info("Data cleaning done. Check the results.")


if __name__ == "__main__":
    DataCleaning()
