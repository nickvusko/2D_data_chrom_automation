# -*- coding: utf-8 -*-
"""Script for creation of KPL."""
import glob
import h5py
import os
import tkinter as tk


class KPLCreate:
    """Create a new KPL library"""
    def __init__(self, input_path: str = f"{os.getcwd()}\\data", result_path: str = f"{os.getcwd()}"):
        """
        Initialize the KPL base class

        :param input_path: str representation of input_folder path. Default value set as working_directory\\data
        :param result_path: str representation of result_folder path. Default value set as working_directory
        """
        self.__main_database = h5py.File(f"{result_path}\\KPL.h5", "w")
        self.__input_path = input_path

    def get_files(self):
        """returns list of files for the analysis"""
        list_of_files_all = []
        return list_of_files_all.append([file for file in glob.iglob(f"{self.__input_path}\\*.txt")])
