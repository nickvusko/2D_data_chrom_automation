# -*- coding: utf-8 -*-
"""Main function for kpl handling."""

import datetime
import os
import tkinter as tk
from tkinter.filedialog import askopenfilename

import pandas as pd

import kpl_append
import kpl_create
import kpl_compare


class KPLMain(tk.Tk):
    """Base class of kpl handling"""

    def __init__(self):
        """
        Initialize the kpl main class
        """
        super().__init__()
        self.__init_window()
        self.mainloop()

    def __init_window(self) -> None:
        """Initialize app window."""
        self.title("kpl interface")
        self.rowconfigure(0, minsize=100, weight=1)
        self.columnconfigure(3, weight=1, minsize=50)
        btn_create = tk.Button(text="Create new kpl", command=kpl_create.KPLCreate)
        btn_create.grid(row=0, column=0, sticky="nsew", pady=10, padx=10)

        btn_compare = tk.Button(text="Compare chromatogram to existing kpl", command=kpl_compare.KPLCompare)
        btn_compare.grid(row=0, column=1, sticky="nsew", pady=10, padx=10)

        btn_add = tk.Button(text="Add new compound to the kpl", command=kpl_append.KPLAppend)
        btn_add.grid(row=0, column=2, sticky="nsew", pady=10, padx=10)

        btn_export = tk.Button(text="Export kpl", command=self.export_lib)
        btn_export.grid(row=0, column=3, sticky="nsew", pady=10, padx=10)

    def export_lib(self) -> None:
        """Export library from .h5 to .txt"""
        load_file = askopenfilename(filetypes=[("HDF5", "*.h5")],
                                    initialdir=os.getcwd(), defaultextension=".h5",
                                    title="Select library for export")
        df = pd.read_hdf(load_file)
        name = load_file.split("/")[-1].split('.')[0]
        df.to_csv(f"exported_{name}.txt", sep="\t", index=False)
        print("Database exported.")


if __name__ == "__main__":
    KPLMain()
