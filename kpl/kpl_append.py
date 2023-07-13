# -*- coding: utf-8 -*-
"""Script for creation of the kpl."""
import abc
import datetime
import json
import logging
import os
import pandas as pd
import statistics
import tkinter as tk
from tkinter.filedialog import askopenfilename

import helper


class KPLAppend:
    """Create a new kpl library."""

    def __init__(self):
        """Initialize the kpl base class"""
        self.__core_kpl = f"{os.getcwd()}{os.sep}Core.h5"
        self.__user_kpl = f"{os.getcwd()}{os.sep}User.h5"
        self.__codename = ""
        logging.basicConfig(filename=f"log_append_line_to_core_kpl_{datetime.date.today()}_{datetime.date.today()}.log",
                            level=logging.DEBUG,
                            format="%(asctime)s %(message)s", filemode="w"
                            )
        self.master = tk.Tk()
        self.setup_window()
        self.master.mainloop()

    def add_line(self) -> None:
        """returns list of files for the analysis"""
        self.__core_kpl = pd.read_hdf(self.__core_kpl)
        self.__user_kpl = pd.read_hdf(self.__user_kpl)
        new_idx = self.__user_kpl.where(self.__user_kpl == self.__codename).dropna(how='all'). \
            dropna(how='all', axis=1).index[0]
        new_line = self.__user_kpl.loc[new_idx].to_frame().T
        newname = "MX" + str(int((self.__core_kpl.iat[-1, 0].split("X")[1])) + 1).zfill(5)
        new_line.at[0, "Codename"] = newname
        self.__core_kpl = pd.concat([self.__core_kpl, new_line], ignore_index=True)
        logging.info(f"{self.__codename} from user's database added as {newname} into the core database.")
        print(f"{self.__codename} from user's database added as {newname} into the core database.")

    def setup_window(self) -> None:
        """Set up GUI window."""
        self.master.title("Append new line to core kpl")
        self.master.geometry("800x280")
        codename = tk.StringVar()

        # path to core lib
        tk.Label(self.master, text="Loaded library:").grid(row=0, column=0, sticky="W", pady=10)
        in_entry = tk.Entry(self.master, bg="white", width=50)
        in_entry.insert(index=0, string=self.__core_kpl)
        in_entry.config(state=tk.DISABLED)
        in_entry.grid(row=0, column=1, pady=10)
        in_button = tk.Button(self.master, text="Change library",
                              command=lambda: self.get_path(in_entry))
        in_button.grid(row=0, column=2, pady=10)

        # users library
        tk.Label(self.master, text="Currently set output folder:").grid(row=1, column=0, sticky="W", pady=10)
        out_entry = tk.Entry(self.master, bg="white", width=50)
        out_entry.insert(index=0, string=self.__user_kpl)
        out_entry.config(state=tk.DISABLED)
        out_entry.grid(row=1, column=1, pady=10)
        out_button = tk.Button(self.master, text="Change output folder", command=lambda: self.get_path(out_entry, False))
        out_button.grid(row=1, column=2, pady=10)

        tk.Label(self.master, text="MX codename you want to add to core kpl:").grid(row=2, column=0, sticky="W", pady=10)
        add_entry = tk.Entry(self.master, bg="white", width=50, textvariable=codename)
        add_entry.focus_set()
        add_entry.grid(row=2, column=1, pady=10)
        add_button = tk.Button(self.master, text="Add",
                               command=lambda: self.get_codename(add_entry, add_label))
        add_button.grid(row=2, column=2, pady=10)

        # append button
        add_confirm = tk.Button(self.master, text="Add new compound \nto core library", command=self.add_line)
        add_confirm.grid(row=4, column=0, pady=10)
        add_confirm.config(font=26)

        add_label = tk.Label(self.master, text="Add (no codename)")
        add_label.grid(row=3, column=1, sticky="W", pady=10)

        create_button = tk.Button(self.master, text="Close", command=self.master.destroy)
        create_button.grid(row=4, column=2, pady=10)
        create_button.config(font=26)

    def get_path(self, entry: tk.Entry, core: bool = True) -> None:
        """Get working folders.

        :param entry: entry widget
        :param core: True if returning value concerns core library, otherwise False
        """
        if core:
            self.__core_kpl = askopenfilename(filetypes=[("HDF5", "*.h5"), ("Text files", "*.txt")],
                                              initialdir=os.getcwd(), defaultextension=".h5",
                                              title="Select core library")
            entry.config(state=tk.NORMAL)
            entry.delete(0, tk.END)
            entry.insert(0, self.__core_kpl)
            entry.config(state=tk.DISABLED)
        else:
            self.__user_kpl = askopenfilename(filetypes=[("HDF5", "*.h5"), ("Text files", "*.txt")],
                                              initialdir=os.getcwd(), defaultextension=".h5",
                                              title="Select user's library")
            entry.config(state=tk.NORMAL)
            entry.delete(0, tk.END)
            entry.insert(0, self.__user_kpl)
            entry.config(state=tk.DISABLED)

    def get_codename(self, entry: tk.Entry, label: tk. Label):
        """Get the codename of the compound which should be appended.

        :param entry: entry widget
        :param label: label widget
        """
        self.__codename = entry.get()
        label.config(text=f"Add: {self.__codename}")
        label.update()


if __name__ == "__main__":
    KPLAppend()
