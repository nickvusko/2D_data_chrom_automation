# -*- coding: utf-8 -*-
"""Main script for running data_evaluation."""
import pandas as pd
from nearest_neighbors_scent import KNNGridSearch
from random_forest_scent import RFGridSearch
from pca_scent import PCARun
import tkinter as tk
from tkinter.filedialog import askopenfilename
import logging
import os
import datetime
from matrix_plot_generator import MPGen


class DEMain(tk.Tk):
    """Base class of data evaluation package."""

    def __init__(self):
        """
        Initialize the DE main class
        """
        super().__init__()
        self.__path = ""
        self.__df = pd.DataFrame()
        self.__tags = []
        self.__init_window()
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [:::%(name)s:::] [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler(f"logs{os.sep}log_{datetime.date.today()}_"
                                    f"{datetime.datetime.now().strftime('%H_%M_%S')}.log"),
                logging.StreamHandler()
            ]
        )
        self.log = logging.getLogger(__name__)
        self.mainloop()

    def __init_window(self):
        """Initialize app window."""
        self.title("Data classification and visualization interface")

        # load file
        load_label = tk.Label(self, text=self.__path, bg="white")
        load_label.grid(row=0, column=1, sticky="WE")
        tk.Button(self, text="Load file", command=lambda: self.load_file(load_label)).grid(row=0, column=0, sticky="WE")

        tk.Label(self, text="").grid(row=1, column=0)
        # frame for visualization
        frame_vis = tk.LabelFrame(self, bg="gray89")
        frame_vis.grid(row=2, column=0, padx=10, sticky="WE")

        tk.Label(frame_vis, text="Visualization tools").grid(row=0, columnspan=2, sticky="WE")

        # PCA
        tk.Button(frame_vis, text="PCA", command=lambda: PCARun(self.__df, self.__tags)).grid(row=1, column=0,
                                                                                              sticky="WE")
        # matrix corr
        tk.Button(frame_vis, text="Matrix plot", command=lambda: MPGen(self.__df, self.__tags)).\
            grid(row=1, column=1, sticky="WE")

        frame_class = tk.LabelFrame(self, bg="gray89")
        frame_class.grid(row=2, column=1, padx=10)

        tk.Label(frame_class, text="Classification tools").grid(row=0, columnspan=2, sticky="WE")

        # Nearest Neighbor
        tk.Button(frame_class, text="K-Nearest Neighbor", command=lambda: KNNGridSearch(self.__df, self.__tags))\
            .grid(row=1, column=0, sticky="WE")
        # Random Forest
        tk.Button(frame_class, text="Random Forest", command=lambda: RFGridSearch(self.__df, self.__tags))\
            .grid(row=1, column=1, sticky="WE")

    def load_file(self, label: tk.Label):
        """Load file.

        :param label: label to update
        """
        self.__path = askopenfilename(title="Select input file", initialdir=os.getcwd(),
                                      filetypes=[("Text files", "*.txt")], defaultextension=".txt")
        label.config(text=self.__path)
        label.update()
        self.__df = pd.read_csv(self.__path, sep="\t", header=0, index_col=0)
        self.__tags = [x for x in self.__df["Class"]]
        self.__df = self.__df.drop("Class", axis=1)
        self.log.info(f"File loaded: {self.__path}, shape: {self.__df.shape}, class tags: {set(self.__tags)}")


if __name__ == "__main__":
    DEMain()
