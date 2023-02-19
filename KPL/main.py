# -*- coding: utf-8 -*-
"""Main function for KPL handling."""

import datetime
import h5py
import os
import tkinter as tk


class KPLBase:
    """Base class of KPL handling"""
    def __init__(self, file_path: str = f"{os.getcwd()}\\KPL.h5", result_path: str = f"{os.getcwd()}\\{datetime.date}"):
        """
        Initialize the KPL base class

        :param file_path: str representation of path to the KPL. Default value set as working_directory\\KPL.h5
        :param result_path: str representation of result_folder path. Default value set as working_directory\\date
        """
        # self.__main_database = h5py.File(file_path, "r+")
        self.__result_folder = result_path
        self.window = self.__init_window()

    @staticmethod
    def __init_window() -> tk.Tk:
        """Initialize app window

        :return app window"""
        window = tk.Tk()
        window.title("KPL interface")
        window.rowconfigure(0, minsize=50, weight=1)
        window.columnconfigure(4, weight=1, minsize=50)
        btn_create = tk.Button(master=window, text="Create new KPL")
        btn_create.grid(row=0, column=0, sticky="nsew")

        btn_compare = tk.Button(master=window, text="Compare chromatogram to existing KPL")
        btn_compare.grid(row=0, column=1, sticky="nsew")

        btn_add = tk.Button(master=window, text="Add new compound to the KPL")
        btn_add.grid(row=0, column=2, sticky="nsew")

        btn_export = tk.Button(master=window, text="Export KPL")
        btn_export.grid(row=0, column=3, sticky="nsew")

        window.mainloop()
        return window

KPLBase()