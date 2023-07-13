# -*- coding: utf-8 -*-
"""Helper functions for data evaluation package."""
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt


def plot_matrix(y: np.array, y_pred: np.array) -> None:
    """
    Plot confusion matrix.

    :param y: true class tags
    :param y_pred: predicted class tags
    """
    idx = np.sort(np.unique(np.append(y, y_pred)))

    df_cm = pd.DataFrame(confusion_matrix(y, y_pred), index=idx,
                         columns=idx)
    s = sns.heatmap(df_cm, annot=True, cmap="viridis")
    s.set_ylabel("True class")  # set y label
    s.set_xlabel("Predicted class")  # set x label
    plt.show()
