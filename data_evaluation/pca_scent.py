"""Basic implementation of PCA algorithm"""
import datetime
import logging
import numpy as np
import os
import pandas as pd
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import tkinter as tk

_SOLVER = {0: "auto", 1: "full", 2: "arpack", 3: "randomized"}


class PCARun:
    """Base class for PCA."""

    def __init__(self, var=None, clas=None):
        """
        Create PCA model.

        :param var: variables
        :param clas: class tag
        """
        self.log = logging.getLogger(__name__)
        self.log.info("PCA running.")
        self.scaler = StandardScaler()
        self.master = tk.Tk()
        self.var = var
        self.clas = clas
        self.compos = 2
        self.__pca_svd_solver = tk.IntVar(self.master)
        self.setup_window()
        self.master.mainloop()

    def setup_window(self) -> None:
        """Set up GUI window."""
        self.master.title("PCA setup")

        # set principal components
        top_label = tk.Label(self.master, text=f"Number of components: {self.compos}; svd solver: "
                                               f"{_SOLVER[self.__pca_svd_solver.get()]}")
        top_label.grid(row=0, column=1, sticky="WE", pady=10)
        tk.Button(self.master, text=f"Set up PCA:", command=lambda: self.set_compos(top_label)). \
            grid(row=0, column=0, sticky="WE", pady=10)

        rw = 1
        for i in _SOLVER:
            tk.Radiobutton(self.master, text=_SOLVER[i], variable=self.__pca_svd_solver, value=i,
                           command=self.__pca_svd_solver.get).grid(row=rw, column=0, sticky="W")
            rw += 1
        # start button
        add_confirm = tk.Button(self.master, text="Start", command=self.run_pca)
        add_confirm.grid(row=6, column=0, pady=10, sticky="W")
        add_confirm.config(font=26)

        # close button
        close_button = tk.Button(self.master, text="Close", command=self.master.destroy)
        close_button.grid(row=6, column=1, pady=10, sticky="E")
        close_button.config(font=26)

    def set_compos(self, label: tk.Label) -> None:
        """Change setting of top correlations.

        :param label: label widget
        """
        top_lvl = tk.Toplevel()
        top_lvl.title("PCA setup")
        top_lvl.geometry("300x250")

        tk.Label(top_lvl, text=f"Number of principal components: {self.compos}"). \
            grid(row=0, column=0, pady=10, sticky="WE")
        toleration_entry = tk.Entry(top_lvl, bg="white", width=10)
        toleration_entry.grid(row=0, column=1, pady=10, sticky="W")
        tk.Button(top_lvl, text="Set", command=lambda: self.update_destroy(toleration_entry, label, top_lvl)) \
            .grid(row=0, column=1, pady=10, sticky="E")

    def update_destroy(self, entry: tk.Entry, label: tk.Label, window: tk.Toplevel) -> None:
        """Update value of the label and destroy current window"""
        self.compos = entry.get()
        label.config(text=f"Number of components: {self.compos}; svd solver: {_SOLVER[self.__pca_svd_solver.get()]}")
        label.update()
        self.log.info(f"Number of top correlations to display set to {self.compos}")
        self.log.info(f"SVD solver changed to {_SOLVER[self.__pca_svd_solver.get()]}")
        window.destroy()

    def run_pca(self):
        """Run PCA analysis."""
        pca_scent = PCA(n_components=int(self.compos), svd_solver=_SOLVER[self.__pca_svd_solver.get()])
        scaled_x = self.scaler.fit_transform(self.var)
        principal_components = pca_scent.fit_transform(scaled_x)
        self.log.info(f"Explained variance ratios for {self.compos} principal components:\n"
                      f"{pca_scent.explained_variance_ratio_}")

        self.log.info(f"Explained variance for {self.compos} principal components:\n"
                      f"{pca_scent.explained_variance_}")

        self.log.info(f"Singular values for {self.compos} principal components:\n"
                      f"{pca_scent.singular_values_}")

        self.log.info(f"Noise variance for the model:\n"
                      f"{pca_scent.noise_variance_}")

        sns.scatterplot(x=principal_components[:, 0], y=principal_components[:, 1], hue=self.clas, palette="colorblind")
        plt.legend(bbox_to_anchor=(1.04, 1.1), loc="upper left")
        plt.axhline(y=0, color='k', linewidth=1)
        plt.axvline(x=0, color='k', linewidth=1)
        plt.title("PCA plot")  # edit the title
        plt.xlabel('First Principal Component')
        plt.ylabel('Second Principal Component')
        plt.show()

        loadings = pca_scent.components_
        n_features = pca_scent.n_features_
        pc_loadings = dict(zip([f"PC{i}" for i in list(range(1, n_features + 1))], loadings))
        loadings_df = pd.DataFrame.from_dict(pc_loadings)
        # get name of features (variables from original input file)
        path = f"{os.getcwd()}{os.sep}PCA_results{os.sep}{datetime.date.today()}_" \
               f"{datetime.datetime.now().strftime('%H_%M_%S')}"
        if not os.path.exists(path):
            os.makedirs(path)
            self.log.info(f"Folder created: {path}")
        loadings_df["features"] = [x for x in self.var.columns]
        loadings_df = loadings_df.set_index("features")
        loadings_df.to_csv(f"{path}{os.sep}loadings.txt", sep="\t")  # edit line - output file

        xs = loadings[0]
        ys = loadings[1]

        # Plot the loadings on a scatterplot
        for i, varnames in enumerate(loadings_df.index):
            plt.scatter(xs[i], ys[i], s=200)
            plt.arrow(
                0, 0,  # coordinates of arrow base
                xs[i],  # length of the arrow along x
                ys[i],  # length of the arrow along y
                color='b',
                head_width=0.01
            )
            plt.text(xs[i], ys[i], varnames, wrap=True, ha="center")

        # Define the axes
        xticks = np.linspace(-0.8, 0.8, num=5)
        yticks = np.linspace(-0.8, 0.8, num=5)
        plt.xticks(xticks)
        plt.yticks(yticks)
        plt.xlabel('PC1')
        plt.ylabel('PC2')

        # Show plot
        plt.title('2D Loadings plot')
        plt.show()

        df_pca = pd.DataFrame(data=principal_components, index=self.var.index, columns=[f"component:{x}" for x in
                                                                                        range(1, int(self.compos) + 1)])
        df_pca.to_csv(f"{path}{os.sep}principal_components.txt", sep="\t")


if __name__ == "__main__":
    PCARun()
