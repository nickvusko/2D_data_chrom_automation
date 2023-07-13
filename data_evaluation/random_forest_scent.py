"""Basic implementation of Random Forest algorithm"""

import datetime
import logging
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
import joblib
import json
import numpy as np
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import tkinter as tk

import helpers


class RFGridSearch:
    """Base class of RF."""

    def __init__(self, df: pd.DataFrame = None, tags=None):
        """
        Perform Grid Search (parameter optimization) for RF.

        :param df: input dataframe
        :param tags: class tags
        """
        self.log = logging.getLogger(__name__)
        self.log.info("RF training running.")
        self.df = df
        self.tags = tags
        self.x_train = None
        self.x_test = None
        self.y_train = None
        self.y_test = None
        self.master = tk.Tk()
        self.split = tk.StringVar(self.master)
        self.split.set("0.25")
        self.path = f"{os.getcwd()}{os.sep}RF_results{os.sep}{datetime.date.today()}_" \
                    f"{datetime.datetime.now().strftime('%H_%M_%S')}"
        if not os.path.exists(self.path):
            os.makedirs(self.path)
            self.log.info(f"Folder created: {self.path}")
        self.rf = RandomForestClassifier()
        self.__best_params = {"n_estimators": None, "max_features": None, "bootstrap": None, "oob_score": None}
        self.setup_window()
        self.master.mainloop()

    def setup_window(self) -> None:
        """Set up GUI window."""
        self.master.title("RF setup")

        # set principal components
        split_label = tk.Label(self.master, text=f"Train/test split ratio: {self.split.get()}")
        split_label.grid(row=0, column=1, sticky="WE", pady=10)
        tk.Button(self.master, text=f"Set split:", command=lambda: self.set_split(split_label)). \
            grid(row=0, column=0, sticky="WE", pady=10)

        # start button
        run_model = tk.Button(self.master, text="Run model", command=lambda: RFClassify(self.x_train, self.x_test,
                                                                                        self.y_train, self.y_test,
                                                                                        self.__best_params[
                                                                                            "n_estimators"],
                                                                                        self.__best_params[
                                                                                            "max_features"],
                                                                                        self.__best_params[
                                                                                            "bootstrap"],
                                                                                        self.__best_params[
                                                                                            "oob_score"],
                                                                                        self.path).run_rf())
        run_model.config(font=26)

        # train button
        tk.Button(self.master, text="Train RF model", command=lambda: self.run_rf(run_model)).grid(row=1, column=1,
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

        tk.Label(top_lvl, text=f"Ratio: {self.split.get()}"). \
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

    def run_rf(self, run_model: tk.Button) -> None:
        """
        Run Grid Search.

        :param run_model: run model button
        :return: y_test predictions
        """
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(self.df, self.tags,
                                                                                test_size=float(self.split.get()),
                                                                                random_state=42)
        param_grid = {"n_estimators": list(range(10, 200, 10)), "max_features": list(range(1, 11, 2)),
                      "bootstrap": [True, False], "oob_score": [True, False]}

        full_cv_classifier = GridSearchCV(self.rf, param_grid, cv=5, scoring='accuracy')

        full_cv_classifier.fit(self.x_train, self.y_train)

        self.log.info(f"Best model found: {full_cv_classifier.best_estimator_.get_params().items()}")

        self.__best_params = full_cv_classifier.best_estimator_.get_params()

        to_export = {"n_estimators": self.__best_params["n_estimators"],
                     "max_features": self.__best_params["max_features"],
                     "bootstrap": self.__best_params["bootstrap"],
                     "oob_score": self.__best_params["oob_score"]}

        with open(f"{self.path}{os.sep}best_params.txt", "w") as file:
            file.write(json.dumps(to_export))

        run_model.grid(row=2, column=1, pady=10, sticky="W")


class RFClassify:
    """Base class of RF classifier """

    def __init__(self, x_train, x_test, y_train, y_test, n_estimators, max_features, bootstrap, oob_score, path):
        """
        Perform classification for RF.

        :param x_train: training variables
        :param x_test: variables for evaluation
        :param y_train: training class tags
        :param n_estimators: number of estimators
        :param max_features: number of max features
        :param bootstrap: [True, False]
        :param oob_score: [True, False]
        :param path: save to
        """
        self.log = logging.getLogger(__name__)
        self.log.debug("RF classifier running.")
        self.x_train = x_train
        self.x_test = x_test
        self.y_train = y_train
        self.y_test = np.array(y_test)
        self.path = path
        self.rf = RandomForestClassifier(n_estimators=n_estimators, max_features=max_features, bootstrap=bootstrap,
                                         oob_score=oob_score)

    def run_rf(self) -> None:
        """Apply RF model."""
        self.rf.fit(self.x_train, self.y_train)

        joblib.dump(self.rf, f"{self.path}{os.sep}rf_model.pkl")

        rf_pred = self.rf.predict(self.x_test)

        report = pd.DataFrame(classification_report(self.y_test, rf_pred, output_dict=True)).T

        report.to_excel(f"{self.path}{os.sep}classification_report.xlsx", index=True)

        self.log.info(f"Random Forest:\n{report}")

        helpers.plot_matrix(self.y_test, rf_pred)
