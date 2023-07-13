# -*- coding: utf-8 -*-
"""Basic implementation of matrix plot generator."""
import logging
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.preprocessing import StandardScaler
import tkinter as tk


class MPGen:
    """Class of the matrix plot generator."""

    def __init__(self, df: pd.DataFrame, tags: list):
        """
        Initialize the MergeRatios class.

        :param df: df
        :param tags: class tags
        """
        self.log = logging.getLogger(__name__)
        self.log.info("Matrix plot generator running.")
        self.master = tk.Tk()
        self.__top_cor = 0
        self.__df = df
        self.__tags = tags
        self.setup_window()
        self.master.mainloop()

    def setup_window(self) -> None:
        """Set up GUI window."""
        self.master.title("Matrix plot generator setup")

        # set how many correlations should be displayed
        top_label = tk.Label(self.master, text=f"{self.__top_cor}")
        top_label.grid(row=0, column=1, sticky="WE", pady=10)
        tk.Button(self.master, text=f"Top correlations to be displayed:", command=lambda: self.set_top_cor(top_label)).\
            grid(row=0, column=0, sticky="WE", pady=10)

        # start button
        add_confirm = tk.Button(self.master, text="Start", command=self.run)
        add_confirm.grid(row=6, column=0, pady=10, sticky="W")
        add_confirm.config(font=26)

        # close button
        close_button = tk.Button(self.master, text="Close", command=self.master.destroy)
        close_button.grid(row=6, column=1, pady=10, sticky="E")
        close_button.config(font=26)

    def set_top_cor(self, label: tk.Label) -> None:
        """Change setting of top correlations.

        :param label: label widget
        """
        top_lvl = tk.Toplevel()
        top_lvl.title("Set new value")
        top_lvl.geometry("300x250")

        tk.Label(top_lvl, text=f"Count:").grid(row=0, column=0, pady=10, sticky="WE")
        toleration_entry = tk.Entry(top_lvl, bg="white", width=10)
        toleration_entry.grid(row=0, column=1, pady=10, sticky="W")
        tk.Button(top_lvl, text="Set", command=lambda: self.update_destroy(toleration_entry, label, top_lvl)) \
            .grid(row=0, column=1, pady=10, sticky="E")

    def update_destroy(self, entry: tk.Entry, label: tk.Label, window: tk.Toplevel) -> None:
        """Update value of the label and destroy current window"""
        self.__top_cor = entry.get()
        label.config(text=f"Count: {self.__top_cor}")
        label.update()
        self.log.info(f"Number of top correlations to display set to {self.__top_cor}")
        window.destroy()

    def get_top_corrs(self) -> None:
        """Get top correlations."""
        list_of_variables = []
        corr_matrix = self.__df.corr().abs()
        upper_triangle = (corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)).stack().sort_values
                          (ascending=False))
        self.log.info(f"Correlations: {upper_triangle}")
        if len(upper_triangle.index) < int(self.__top_cor):
            return [x for x in upper_triangle.index]
        for inx in [x for x in upper_triangle.index[:int(self.__top_cor)]]:
            for i in inx:
                if i not in list_of_variables:
                    list_of_variables.append(i)
        self.log.info(f"List of compounds involved in top correlations: {list_of_variables}")
        return list_of_variables

    def run(self) -> None:
        """Run the script"""
        focus = self.get_top_corrs()
        df = self.__df[focus]
        scaler = StandardScaler()
        scaler.fit(df)
        scaled_x = scaler.transform(df)
        df_scaled_x = pd.DataFrame(data=scaled_x, index=df.index, columns=df.columns)
        df_scaled_x["Class"] = self.__tags
        g = sns.PairGrid(df_scaled_x, hue="Class", palette="colorblind", corner=True)
        g.map_diag(sns.kdeplot)
        g.map_lower(sns.scatterplot)
        g.add_legend(title="Matrix plot")
        plt.show()
