# -*- coding: utf-8 -*-
"""Script for creation of the kpl."""

import datetime
import json
import logging
import os
import pandas as pd
import statistics
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename, asksaveasfilename

import helper


class KPLCompare:
    """Update user's library."""

    def __init__(self):
        """Initialize the kpl compare class"""
        self.__main_database = pd.DataFrame()
        self.__open_kpl = f"{os.getcwd()}{os.sep}"
        self.__save_kpl = f"{os.getcwd()}{os.sep}"
        self.__input_path = f"{os.getcwd()}{os.sep}data_kpl"
        self.__output_path = f"{os.getcwd()}{os.sep}data_kpl"
        with open(f"{os.getcwd()}{os.sep}config.txt", 'r') as j:
            self.__config_file = json.loads(j.read())
        self.__df = pd.DataFrame()
        logging.basicConfig(filename=f"logs{os.sep}log_kpl_update_{datetime.date.today()}_"
                                     f"{datetime.datetime.now().strftime('%H_%M_%S')}.log",
                            level=logging.DEBUG,
                            format="%(asctime)s %(message)s", filemode="w"
                            )
        self.master = tk.Tk()
        self.setup_window()
        self.master.mainloop()

    def process_files(self) -> None:
        """returns list of files for the analysis"""
        print(self.__open_kpl)
        self.__main_database = pd.read_hdf(self.__open_kpl)
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
                    logging.info("Empty database found, please create a new one.")
                    print("Empty database found, please create a new one.")
                database_foc = self.get_foc_database(row)
                if len(database_foc) == 0:
                    logging.info(f"No matches found in the core database, adding new line for "
                                 f"{self.__df.at[row, 'Name']}.")
                    print(f"No matches found in the core database, adding new line for {self.__df.at[row, 'Name']}.")
                    self.add_new_row(row, file)
                else:
                    spectrum_chrom = helper.transfer_spectrum(self.__df.at[row, "Spectra"].split(" "), transform=False)
                    if not spectrum_chrom:
                        print("empty spectrum detected")
                        continue
                    candidates = {}
                    for kpl_row in database_foc.index:
                        result = helper.compare_spectra(helper.transform_spectrum(spectrum_chrom),
                                                        helper.transform_spectrum(
                                                            self.__main_database.at[kpl_row, "Spectra"]))
                        if result > 90:
                            candidates[kpl_row] = result

                    if candidates:
                        max_value = max(candidates, key=candidates.get)
                        logging.info(f"Match found for {self.__df.at[row, 'Name']}: "
                                     f"{self.__main_database.at[max_value, 'Codename']} "
                                     f"({self.__main_database.at[max_value, 'Name']})")
                        print(f"Match found for {self.__df.at[row, 'Name']}: "
                              f"{self.__main_database.at[max_value, 'Codename']} "
                              f"({self.__main_database.at[max_value, 'Name']})")
                        self.update_record(file, max_value, row)
                    else:
                        logging.info(f"No match found for {self.__df.at[row, 'Name']} "
                                     f"in current database. Adding a new record.")
                        print(f"No match found for {self.__df.at[row, 'Name']} "
                              f"in current database. Adding a new record.")
                        self.add_new_row(row, file)

            logging.info(f"File done: {file.split(f'{os.sep}')[-1].split('.')[0]}.")
            print(f"File done: {file.split(f'{os.sep}')[-1].split('.')[0]}.")
            self.__df.set_index("Codename", inplace=True)
            self.__df.to_csv(f"{self.__output_path}{os.sep}renamed_{file.split(f'{os.sep}')[-1]}", sep="\t")

        logging.info(f"All files renamed successfully.")
        print(f"All files renamed successfully.")
        proc_file.config(text="All done!")
        proc_file.update()

        self.__main_database.to_csv(self.__save_kpl, sep="\t", index=False) if self.__save_kpl.split(".")[
                                                                                   -1] == "txt" else \
            self.__main_database.to_hdf(self.__save_kpl, key="main_database", mode='w',
                                        format='fixed', data_columns=True)
        top_lvl.destroy()
        self.master.destroy()

    def add_new_row(self, row: int, file: str) -> None:
        """
        Add a new line to kpl.

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

    def update_record(self, file: str, match: int, row: int) -> None:
        """Update record of the database hit.

        param file: inspected file
        param match: id of the match line
        param row: df index of the match
        """
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

    def setup_window(self) -> None:
        """Set up GUI window."""
        self.master.title("Compare tool")
        self.master.geometry("600x300")
        # core library
        tk.Label(self.master, text="Loaded library:").grid(row=0, column=0, sticky="W", pady=10)
        in_entry = tk.Entry(self.master, bg="white", width=50)
        in_entry.insert(index=0, string=self.__open_kpl)
        in_entry.config(state=tk.DISABLED)
        in_entry.grid(row=0, column=1, pady=10)
        in_button = tk.Button(self.master, text="Change library",
                              command=lambda: self.get_path_compare(in_entry, "load_kpl"))
        in_button.grid(row=0, column=2, pady=10)

        # output folder line
        tk.Label(self.master, text="Save as:").grid(row=1, column=0, sticky="W", pady=10)
        out_entry = tk.Entry(self.master, bg="white", width=50)
        out_entry.insert(index=0, string=self.__save_kpl)
        out_entry.config(state=tk.DISABLED)
        out_entry.grid(row=1, column=1, pady=10)
        out_button = tk.Button(self.master, text="Set name of the file",
                               command=lambda: self.get_path_compare(out_entry, "save_kpl"))
        out_button.grid(row=1, column=2, pady=10)

        # data set line
        tk.Label(self.master, text="Input files location:").grid(row=2, column=0, sticky="W", pady=10)
        data_entry = tk.Entry(self.master, bg="white", width=50)
        data_entry.insert(index=0, string=self.__input_path)
        data_entry.config(state=tk.DISABLED)
        data_entry.grid(row=2, column=1, pady=10)
        data_button = tk.Button(self.master, text="Change source folder",
                                command=lambda: self.get_path_compare(data_entry, "input"))
        data_button.grid(row=2, column=2, pady=10)

        # output line
        tk.Label(self.master, text="Output files location:").grid(row=3, column=0, sticky="W", pady=10)
        data_entry = tk.Entry(self.master, bg="white", width=50)
        data_entry.insert(index=0, string=self.__input_path)
        data_entry.config(state=tk.DISABLED)
        data_entry.grid(row=3, column=1, pady=10)
        data_button = tk.Button(self.master, text="Change output folder",
                                command=lambda: self.get_path_compare(data_entry, "output"))
        data_button.grid(row=3, column=2, pady=10)

        # create database button
        compare_button = tk.Button(self.master, text="Compare chromatograms \nto database records",
                                   command=self.process_files)
        compare_button.grid(row=5, column=1, pady=10)
        compare_button.config(font=26)

    def get_path_compare(self, entry: tk.Entry, action: str) -> None:
        """Get working folders.

        :param entry: entry widget
        :param action: True if returning value concerns inout folder, False for output folder
        """
        if action == "load_kpl":
            self.__open_kpl = askopenfilename(filetypes=[("HDF5", "*.h5"), ("Text files", "*.txt")],
                                              initialdir=os.getcwd(), defaultextension=".h5")
            entry.config(state=tk.NORMAL)
            entry.delete(0, tk.END)
            entry.insert(0, self.__open_kpl)
            entry.config(state=tk.DISABLED)
        elif action == "save_kpl":
            self.__save_kpl = asksaveasfilename(filetypes=[("HDF5", ".h5"), ("Text files", ".txt")],
                                                initialdir=os.getcwd(), defaultextension=".h5")

            entry.config(state=tk.NORMAL)
            entry.delete(0, tk.END)
            entry.insert(0, self.__save_kpl)
            entry.config(state=tk.DISABLED)
        elif action == "output":
            self.__output_path = askdirectory(initialdir=self.__output_path)

            entry.config(state=tk.NORMAL)
            entry.delete(0, tk.END)
            entry.insert(0, self.__output_path)
            entry.config(state=tk.DISABLED)
        else:
            self.__input_path = askdirectory(initialdir=self.__input_path)
            entry.config(state=tk.NORMAL)
            entry.delete(0, tk.END)
            entry.insert(0, self.__input_path)
            entry.config(state=tk.DISABLED)

    def get_foc_database(self, row: int) -> pd.DataFrame:
        """
        Get the focus on search window in core database.

        param df: currently inspected chromatogram
        param row: currently inspected row
        returns: focused database
        """
        lower_band_1st = float(self.__df.at[row, "1st Dimension Time (s)"] - 50)
        upper_band_1st = float(self.__df.at[row, "1st Dimension Time (s)"] + 50)
        lower_band_2nd = float(self.__df.at[row, "2nd Dimension Time (s)"] - 0.9)
        upper_band_2nd = float(self.__df.at[row, "2nd Dimension Time (s)"] + 0.9)
        database_f = self.__main_database[self.__main_database["1st RT"].between(lower_band_1st,
                                                                                 upper_band_1st)]
        return database_f[database_f["2nd RT"].between(lower_band_2nd, upper_band_2nd)]


if __name__ == "__main__":
    KPLCompare()
