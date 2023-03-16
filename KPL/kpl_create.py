# -*- coding: utf-8 -*-
"""Script for creation of the KPL."""
import abc
import datetime
import json
import logging
import os
import pandas as pd
import statistics
import tkinter as tk
from tkinter.filedialog import askdirectory

import helper


class KPLCreate:
    """Create a new KPL library."""

    def __init__(self):
        """Initialize the KPL base class"""
        self.__main_database = pd.DataFrame(columns=["Codename", "1st RT", "2nd RT", "Spectra", "Found", "Name",
                                                     "calc_1stRT", "calc_2ndRT", "calc_spectra"])
        self.__input_path = f"{os.getcwd()}{os.sep}data_kpl"
        self.__result_path = f"{os.getcwd()}{os.sep}results"
        with open(f"{os.getcwd()}{os.sep}config.txt", 'r') as j:
            self.__config_file = json.loads(j.read())
        self.__df = pd.DataFrame()
        logging.basicConfig(filename=f"logs{os.sep}log_create_new_kpl_{datetime.date.today()}_"
                                     f"{datetime.datetime.now().strftime('%H_%M_%S')}.log",
                            level=logging.DEBUG,
                            format="%(asctime)s %(message)s", filemode="w"
                            )
        self.master = tk.Tk()
        self.setup_window()
        self.master.mainloop()

    def process_files(self):
        """returns list of files for the analysis"""
        top_lvl = tk.Toplevel()
        top_lvl.title("Progress tracker")
        top_lvl.geometry("300x250")
        proc_file = tk.Label(top_lvl, text="Starting...")
        proc_file.grid(row=0, column=1, pady=10)
        files = helper.get_files(self.__input_path)
        for file in files:
            proc_file.config(text=f"Processing file: {file.split(f'{os.sep}')[-1].split('.')[0]}.")
            proc_file.update()
            logging.info(f"Processing file: {file.split(f'{os.sep}')[-1].split('.')[0]}.")
            print(f"Processing file: {file.split(f'{os.sep}')[-1].split('.')[0]}.")
            self.__df = pd.read_csv(file, sep="\t", header=0, encoding="latin-1")
            helper.check_formatting(self.__df)
            self.__df["Codename"] = ""
            for row in self.__df.index:
                if self.__main_database.empty:
                    logging.info("Initializing the new database with row 0")
                    init_row = {"Codename": "MX00000",
                                "1st RT": float(self.__df.at[row, "1st Dimension Time (s)"]),
                                "2nd RT": float(self.__df.at[row, "2nd Dimension Time (s)"]),
                                "Spectra": helper.transfer_spectrum(self.__df.at[row, "Spectra"].split(" "),
                                                                    transform=False),
                                "Found": [file.split(f"{os.sep}")[-1].split(".")[0]],
                                "Name": self.__df.at[row, "Name"],
                                "calc_1stRT": [float(self.__df.at[row, "1st Dimension Time (s)"])],
                                "calc_2ndRT": [float(self.__df.at[row, "2nd Dimension Time (s)"])],
                                "calc_spectra": helper.transfer_spectrum(self.__df.at[row, "Spectra"].split(" "),
                                                                         transform=False, do_list=True)}
                    self.__df.at[row, "Codename"] = "MX00000"
                    self.__main_database = self.__main_database.append(init_row, ignore_index=True)
                    continue
                if self.__df.at[row, "Name"] not in self.__main_database["Name"].values:
                    self.add_new_row(row, file)
                else:
                    self.update_record(file, self.__df.at[row, "Name"], row)

            logging.info(f"File done: {file.split(f'{os.sep}')[-1].split('.')[0]}.")
            print(f"File done: {file.split(f'{os.sep}')[-1].split('.')[0]}.")
            self.__df.set_index("Codename", inplace=True)
            self.__df.to_csv(f"{self.__result_path}{os.sep}{file.split(f'{os.sep}')[-1]}", sep="\t")

        logging.info(f"The core database was created successfully")
        print(f"The core database was created successfully")
        proc_file.config(text="All done!")
        proc_file.update()

        self.__main_database.to_csv("test.txt", sep="\t")
        self.__main_database.to_hdf(f"Core_KPL_{datetime.date.today()}.h5", key="main_database", mode='w',
                                    format='fixed', data_columns=True)
        top_lvl.destroy()
        self.master.destroy()

    def add_new_row(self, row: int, file: str):
        """
        Add a new line to KPL.

        param file: name of the inspected chromatogram
        param row: inspected row
        """
        newname = "MX" + str(int((self.__main_database.iat[-1, 0].split("X")[1])) + 1).zfill(5)
        try:
            spectra = helper.transfer_spectrum(self.__df.at[row, "Spectra"].split(" "), transform=False)
            spectra_lst = helper.transfer_spectrum(self.__df.at[row, "Spectra"].split(" "),
                                                   transform=False, do_list=True)
        except AttributeError:
            spectra = {0: 0}
            spectra_lst = {0: [0]}
        new_row = {"Codename": newname,
                   "1st RT": float(self.__df.at[row, "1st Dimension Time (s)"]),
                   "2nd RT": float(self.__df.at[row, "2nd Dimension Time (s)"]),
                   "Spectra": spectra,
                   "Found": [file.split(f"{os.sep}")[-1].split(".")[0]],
                   "Name": self.__df.at[row, "Name"],
                   "calc_1stRT": [float(self.__df.at[row, "1st Dimension Time (s)"])],
                   "calc_2ndRT": [float(self.__df.at[row, "2nd Dimension Time (s)"])],
                   "calc_spectra": spectra_lst}
        new_row = pd.Series(new_row).to_frame().T
        self.__main_database = pd.concat([self.__main_database, new_row], ignore_index=True)
        self.__df.at[row, "Codename"] = newname
        logging.info(f"New record added: {newname}.")
        print(f"New record added: {newname}.")

    def update_record(self, file: str, name: str, row: int):
        """Update record of the database hit.

        param file: inspected file
        param name: found name
        param row: df index of the match
        """
        match = self.__main_database.where(self.__main_database == name).dropna(how='all'). \
            dropna(how='all', axis=1).index[0]
        self.__main_database.at[match, "calc_1stRT"].append(float(self.__df.at[row, "1st Dimension Time (s)"]))
        self.__main_database.at[match, "1st RT"] = statistics.median(self.__main_database.at[match, "calc_1stRT"])
        self.__main_database.at[match, "calc_2ndRT"].append(float(self.__df.at[row, "2nd Dimension Time (s)"]))
        self.__main_database.at[match, "2nd RT"] = statistics.median(self.__main_database.at[match, "calc_2ndRT"])
        self.__main_database.at[match, "Found"].append(file.split(f"{os.sep}")[-1].split(".")[0])
        update_calc_spectra = self.__main_database.at[match, "calc_spectra"]
        try:
            df_spectra = helper.transfer_spectrum(self.__df.at[row, "Spectra"].split(" "), transform=False)
        except AttributeError:
            df_spectra = {0: 0}
        for key_df in df_spectra:
            if key_df in update_calc_spectra.keys():
                update_calc_spectra[key_df].append(df_spectra[key_df])
            else:
                update_calc_spectra[key_df] = [df_spectra[key_df]]
        self.__main_database.at[match, "calc_spectra"] = update_calc_spectra
        self.__main_database.at[match, "Spectra"] = {k: statistics.median(v) for k, v in
                                                     self.__main_database.at[match, "calc_spectra"].items()}
        self.__df.at[row, "Codename"] = self.__main_database.at[match, "Codename"]
        logging.info(f"{self.__df.at[row, 'Name']} was identified as the record "
                     f"{self.__main_database.at[match, 'Codename']} ({self.__main_database.at[match, 'Name']})")

    def setup_window(self):
        """Set up GUI window."""
        self.master.title("Core Library Creator")
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

        # create database button
        create_button = tk.Button(self.master, text="Create new \ncore database", command=self.process_files)
        create_button.grid(row=4, column=1, pady=10)
        create_button.config(font=26)

    def get_path(self, entry: tk.Entry, input_folder: bool = True):
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
        else:
            self.__result_path = direct
            entry.config(state=tk.NORMAL)
            entry.delete(0, tk.END)
            entry.insert(0, self.__result_path)
            entry.config(state=tk.DISABLED)


if __name__ == "__main__":
    KPLCreate()
