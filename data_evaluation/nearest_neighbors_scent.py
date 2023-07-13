"""Basic implementation of K-Nearest and Radius neighbor algorithms"""

import datetime
import logging

import numpy as np
import pandas as pd
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
import joblib
import json
import tkinter as tk
import os

import helpers


class KNNGridSearch:
    """Base class of KNN."""

    def __init__(self, df: pd.DataFrame = None, tags=None):
        """
        Perform Grid Search (parameter optimization) for K-NN.

        :param df: input dataframe
        :param tags: class tags
        """
        self.log = logging.getLogger(__name__)
        self.log.info("KNN training running.")
        self.df = df
        self.tags = tags
        self.x_train = None
        self.x_test = None
        self.y_train = None
        self.y_test = None
        self.master = tk.Tk()
        # self.split = tk.StringVar(self.master)
        # self.split.set("0.25")
        self.split = "0.25"
        self.path = f"{os.getcwd()}{os.sep}KNN_results{os.sep}{datetime.date.today()}_" \
                    f"{datetime.datetime.now().strftime('%H_%M_%S')}"
        if not os.path.exists(self.path):
            os.makedirs(self.path)
            self.log.info(f"Folder created: {self.path}")
        self.scaler = StandardScaler()
        self.knn = KNeighborsClassifier()
        self.__best_params = {"knn__n_neighbors": None, "knn__weights": None}
        self.setup_window()
        self.master.mainloop()

    def setup_window(self) -> None:
        """Set up GUI window."""
        self.master.title("KNN setup")

        # set principal components
        split_label = tk.Label(self.master, text=f"Train/test split ratio: {self.split}")
        split_label.grid(row=0, column=1, sticky="WE", pady=10)
        tk.Button(self.master, text=f"Set split:", command=lambda: self.set_split(split_label)). \
            grid(row=0, column=0, sticky="WE", pady=10)

        # start button
        run_model = tk.Button(self.master, text="Run model", command=lambda: KNNClassify(self.x_train, self.x_test,
                                                                                         self.y_train, self.y_test,
                                                                                         self.__best_params[
                                                                                             "knn__n_neighbors"],
                                                                                         self.__best_params[
                                                                                             "knn__weights"],
                                                                                         self.path).run_knn())
        run_model.config(font=26)

        # train button
        tk.Button(self.master, text="Train KNN model", command=lambda: self.run_knn(run_model)).grid(row=1, column=1,
                                                                                                     padx=20, pady=20,
                                                                                                     sticky="WE")

        # close button
        close_button = tk.Button(self.master, text="Close", command=self.master.destroy)
        close_button.grid(row=6, column=1, pady=10, sticky="E")
        close_button.config(font=26)

    def set_split(self, label: tk.Label) -> None:
        """Change setting of train/test split.

        :param label: label widget
        """
        top_lvl = tk.Toplevel()
        top_lvl.title("Split setup")
        top_lvl.geometry("300x250")

        tk.Label(top_lvl, text=f"Ratio: {self.split}"). \
            grid(row=0, column=0, pady=10, sticky="WE")
        split_entry = tk.Entry(top_lvl, bg="white", width=10)
        split_entry.grid(row=0, column=1, pady=10, sticky="W")
        tk.Button(top_lvl, text="Set", command=lambda: self.update_destroy(split_entry, label, top_lvl)) \
            .grid(row=0, column=1, pady=10, sticky="E")

    def update_destroy(self, entry: tk.Entry, label: tk.Label, window: tk.Toplevel) -> None:
        """Update value of the label and destroy current window"""
        self.split = entry.get()
        label.config(text=f"Train/test split ratio: {self.split}")
        label.update()
        self.log.info(f"Train/test split ratio: set to {self.split}")
        window.destroy()

    def run_knn(self, run_model: tk.Button) -> None:
        """
        Run Grid Search.

        :param run_model: run model button
        :return: y_test predictions
        """
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(self.df, self.tags,
                                                                                test_size=float(self.split),
                                                                                random_state=42)

        operations = [("scaler", self.scaler), ("knn", self.knn)]

        pipe = Pipeline(operations)

        param_grid = {"knn__n_neighbors": list(range(1, 25)), "knn__weights": ["uniform", "distance"]}

        full_cv_classifier = GridSearchCV(pipe, param_grid, cv=5, scoring='accuracy')

        full_cv_classifier.fit(self.x_train, self.y_train)

        self.log.info(f"Best model found: {full_cv_classifier.best_estimator_.get_params().items()}")

        self.__best_params = full_cv_classifier.best_estimator_.get_params()

        to_export = {"knn__n_neighbors": self.__best_params["knn__n_neighbors"],
                     "knn__weights": self.__best_params["knn__weights"]}

        with open(f"{self.path}{os.sep}best_params.txt", "w") as file:
            file.write(json.dumps(to_export))

        run_model.grid(row=2, column=1, pady=10, sticky="W")


class KNNClassify:
    """Base class of KNN classifier """
    def __init__(self, x_train, x_test, y_train, y_test, n_neighbors, weights, path):
        """
        Apply KNN model to the data.

        :param x_train: training variables
        :param x_test: variables for evaluation
        :param y_train: training class tags
        :param y_test: tags for evaluation
        :param n_neighbors: number of neighbors
        :param weights: ["uniform", "distance"]
        :param path: save to
        """
        self.log = logging.getLogger(__name__)
        self.log.debug("KNN classifier running.")
        self.x_train = x_train
        self.x_test = x_test
        self.y_train = y_train
        self.y_test = np.array(y_test)
        self.path = path
        self.scaler = StandardScaler()
        self.knn = KNeighborsClassifier(n_neighbors=n_neighbors, weights=weights)

    def run_knn(self) -> None:
        """
        Run Grid Search.

        :return: y_test predictions
        """
        operations = [("scaler", self.scaler), ("rnn", self.knn)]

        pipe = Pipeline(operations)

        pipe.fit(self.x_train, self.y_train)

        joblib.dump(pipe, f"{self.path}{os.sep}knn_model.pkl")

        knn_pred = pipe.predict(self.x_test)

        report = pd.DataFrame(classification_report(self.y_test, knn_pred, output_dict=True)).T

        report.to_excel(f"{self.path}{os.sep}classification_report.xlsx", index=True)

        self.log.info(f"K-Nearest Neighbour:\n{report}")
        helpers.plot_matrix(self.y_test, knn_pred)
