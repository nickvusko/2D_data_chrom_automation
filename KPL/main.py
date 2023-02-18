# -*- coding: utf-8 -*-
"""Main function for KPL handling."""

import datetime
import h5py
import os


class KPLBase:
    """Base class of KPL handling"""
    def __init__(self, file_path: str = f"{os.getcwd()}\\KPL.h5", result_path: str = f"{os.getcwd()}\\{datetime.date}"):
        """
        Initialize the KPL base class

        :param file_path: str representation of path to the KPL. Default value set as working_directory\\KPL.h5
        :param result_path: str representation of result_folder path. Default value set as working_directory\\date
        """
        self.__main_database = h5py.File(file_path, "r+")
        self.__result_folder = result_path