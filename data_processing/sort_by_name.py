# -*- coding: utf-8 -*-
"""Main function for data sort."""

import glob
import logging
import os
import pandas as pd
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename


class SortByName:
    """Class of the sort by name instance."""

    def __init__(self):
        """Initialize the SortByName class."""
        self.__input_path = f"{os.getcwd()}{os.sep}"
        self.__result_path = f"{os.getcwd()}{os.sep}"
        self.__df = pd.DataFrame()
        self.__class_tags = []
        self.log = logging.getLogger(__name__)
        self.log.debug("Create summary table instance running.")
        self.master = tk.Tk()
        self.setup_window()
        self.master.mainloop()

    def setup_window(self) -> None:
        """Set up GUI window."""
        self.master.title("Sort_by_name interface")
        class_tag = tk.StringVar()

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

        # add class tags
        tk.Label(self.master, text="Add class tag:").grid(row=2, column=0, sticky="W", pady=10)
        add_entry = tk.Entry(self.master, bg="white", width=50, textvariable=class_tag)
        add_entry.focus_set()
        add_entry.grid(row=2, column=1, pady=10)
        add_button = tk.Button(self.master, text="Add",
                               command=lambda: self.store_tag(add_entry, add_label))
        add_button.grid(row=2, column=2, pady=10, sticky="W")

        # start button
        add_confirm = tk.Button(self.master, text="Start", command=self.get_concat_tables)
        add_confirm.grid(row=4, column=1, pady=10, sticky="W")
        add_confirm.config(font=26)

        add_label = tk.Label(self.master, text=f"Class tags: {self.__class_tags}")
        add_label.grid(row=3, column=1, sticky="W", pady=10)

        # clear button
        clear_btn = tk.Button(self.master, text="Clear", command=lambda: self.clear_tag(add_label))
        clear_btn.grid(row=3, column=2, pady=10, sticky="E")

        # close button
        close_button = tk.Button(self.master, text="Close", command=self.master.destroy)
        close_button.grid(row=4, column=1, pady=10, sticky="E")
        close_button.config(font=26)

        # load tags button
        load_button = tk.Button(self.master, text="Load", command=lambda: self.load_tags(add_label))
        load_button.grid(row=2, column=3, pady=10, sticky="W")

    def get_path(self, entry: tk.Entry, input_folder: bool = True) -> None:
        """Get working folders.

        :param entry: entry widget
        :param input_folder: True if returning value concerns inout folder, False for output folder
        """
        direct = askdirectory(title="Select input folder" if input_folder else "Select output folder",
                              initialdir=self.__input_path if input_folder else self.__result_path)
        if input_folder:
            self.__input_path = direct
            entry.config(state=tk.NORMAL)
            entry.delete(0, tk.END)
            entry.insert(0, self.__input_path)
            entry.config(state=tk.DISABLED)
            self.log.info(f"Source data folder set to {self.__input_path}.")
        else:
            self.__result_path = direct
            entry.config(state=tk.NORMAL)
            entry.delete(0, tk.END)
            entry.insert(0, self.__result_path)
            entry.config(state=tk.DISABLED)
            self.log.info(f"Output data folder set to {self.__result_path}.")

    def store_tag(self, entry: tk.Entry, label: tk.Label) -> None:
        """Collect class tags.

        :param entry: entry widget
        :param label: label widget
        """
        class_tag = entry.get()
        entry.delete(0, tk.END)
        self.__class_tags.append(class_tag)
        label.config(text=f"Class tags: {self.__class_tags}")
        label.update()

    def load_tags(self, label: tk.Label) -> None:
        """Load .txt file with already prepared class tags.

        :param label: label widget
        """
        fh = askopenfilename(filetypes=[("Text files", "*.txt")], initialdir=os.getcwd(), defaultextension=".txt")
        f = open(fh, 'r').read()
        self.__class_tags = [x.strip() for x in f.split(",")]
        if len(self.__class_tags) > 6:
            label.config(text=f"Number of lass tags: {len(self.__class_tags)}")
        else:
            label.config(text=f"Class tags: {self.__class_tags}")
        label.update()

    def clear_tag(self, label: tk.Label) -> None:
        """Clear class tags.

        :param label: label widget
        """
        self.__class_tags = []
        label.config(text=f"Class tags: {self.__class_tags}")
        label.update()

    def get_names_compounds(self) -> tuple[list, list]:
        """Get names of all compounds in analysed chromatograms and create index list."""
        list_of_files_all = [file for file in glob.iglob(f"{self.__input_path}{os.sep}*.txt")]
        index_lst = []
        for f in list_of_files_all:
            fh = open(f, encoding="utf8")
            for row in fh:
                row_name = row.strip().split("\t")[0]
                if row_name in index_lst or row_name == "Name" or row_name == "" or row_name == "Codename":
                    continue
                else:
                    index_lst.append(row_name)
            fh.close()
        self.log.info(f"{len(index_lst)} compounds from {len(list_of_files_all)} chromatograms collected.")
        return index_lst, list_of_files_all

    def get_concat_tables(self) -> None:
        """Create merged tables for area and height based on index list"""
        self.log.info("Sort by name action initialized. Starting process now.")
        index_lst, list_of_files = self.get_names_compounds()
        df_area_all = pd.DataFrame(index=index_lst)
        df_height_all = pd.DataFrame(index=index_lst)
        for i in list_of_files:
            df = pd.read_csv(i, sep="\t", header=0, index_col=0)
            try:
                df = df.loc[:, ["Area", "Height"]]
            except KeyError:
                self.log.warning("Either Area or Height column is not present")
                quit()
            df = df.groupby(df.index).sum()

            df_area = pd.DataFrame(df["Area"].values, index=df.index, columns=[i])
            df_area_all = df_area_all.join(df_area, sort=False)
            df_area_all.fillna(0).to_csv("area.txt", sep="\t")

            df_height = pd.DataFrame(df["Height"].values, index=df.index, columns=[i])
            df_height_all = df_height_all.join(df_height, sort=False)

        df_area_final, df_height_final = self.add_tags(df_area_all, df_height_all)
        df_area_final.fillna(0).to_csv(f"{self.__result_path}{os.sep}area.txt", sep="\t")
        df_height_final.fillna(0).to_csv(f"{self.__result_path}{os.sep}height.txt", sep="\t")

        self.log.info("Creation of summary table done.")

    def add_tags(self, area_df: pd.DataFrame, height_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Add class tags to dataframes.

        :param area_df: area dataframe
        :param height_df: height dataframe
        """
        self.log.info(f"Collected class tags: {self.__class_tags}.")
        area_df = area_df.T
        class_tags_df = []
        sample_names = []
        for row_name in area_df.index:
            sample_names.append((row_name.split(os.sep)[-1]).split(".")[0])
            found = False
            for tag in self.__class_tags:
                if tag in row_name.split("_"):
                    class_tags_df.append(tag)
                    found = True
                    break
            if not found:
                class_tags_df.append(-1)
        area_df["Class"] = class_tags_df
        area_df["Name"] = sample_names
        area_df = area_df.reset_index(drop=True)
        area_df = area_df.set_index(["Name"])

        height_df = height_df.T
        height_df["Class"] = class_tags_df
        height_df["Name"] = sample_names
        height_df = height_df.reset_index(drop=True)
        height_df = height_df.set_index(["Name"])
        return area_df, height_df


if __name__ == "__main__":
    SortByName()
