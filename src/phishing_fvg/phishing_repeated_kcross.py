# -*-coding:utf-8 -*-
"""
@File    :   phishing_repeated_kcross.py
@Time    :   2023/05/21
@Author  :   Patricia Hernando Fernández 
@Version :   1.0
@Contact :   phf1001@alu.ubu.es

This script is used to execute repeated kcross on a external machine.
Since the experiment is expected to last around 2 weeks, it is necessary
to log the results.

PTC-W6004 is skioped since it is intentional
"""
import sys
import os
import json
import pandas as pd
import numpy as np
import logging

from sklearn.metrics import (
    recall_score,
    precision_score,
    auc,
    roc_curve,
    precision_recall_curve,
    accuracy_score,
    f1_score,
)
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB

import warnings

RESULTS_DIRECTORY = "./results/ssl_vs_sl/ssl_vs_sl-1/"
warnings.filterwarnings("ignore")

# Changing paths to src
src_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
sys.path.append(src_path)
from models.classifiers.DemocraticCoClassifier import DemocraticCo
from models.classifiers.TriTrainingClassifier import TriTraining
from models.classifiers.CoForestClassifier import CoForest


def get_logger(
    name="log_phishing",
    file_name="log_phishing",
    logger_level=logging.DEBUG,
    file_level=logging.DEBUG,
):
    """
    Returns a logger with the given name and the given
    parameters.

    Args:
        name (str, optional): logger name. Defaults to "log_phishing".
        file_name(str, optional): file name. Defaults to "log_phishing".
        logger_level (str, optional): Defaults to logging.DEBUG.
        file_level (str, optional): Defaults to logging.DEBUG.

    Returns:
        object: logger object.
    """
    new_logger = logging.getLogger(name)

    if new_logger.hasHandlers():
        new_logger.handlers.clear()

    new_logger.setLevel(logger_level)

    fh = logging.FileHandler(file_name)
    fh.setLevel(file_level)
    fh.setFormatter(
        logging.Formatter(
            "[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    new_logger.addHandler(fh)

    return new_logger


def get_clss(rd=5):
    """Returns a list of classifiers and a list of classifiers names.

    Args:
        rd (int, optional): Random seed. Defaults to 5.

    Returns:
        tuple: (cls, cls_names) where cls is a list of classifiers and
                                cls_names is a list of classifiers names.
    """
    random_forest_all = RandomForestClassifier(
        6, max_features="log2", random_state=rd
    )

    co_forest_six = CoForest(6, 0.75, max_features="log2", random_state=rd)
    co_forest_twenty = CoForest(20, 0.75, max_features="log2", random_state=rd)

    tri_training = TriTraining(
        DecisionTreeClassifier(random_state=rd),
        GaussianNB(),
        KNeighborsClassifier(),
        random_state=rd,
    )

    democratic_co = DemocraticCo(
        [
            DecisionTreeClassifier(random_state=rd),
            GaussianNB(),
            KNeighborsClassifier(),
        ],
        random_state=rd,
    )

    cls = [
        random_forest_all,
        democratic_co,
        co_forest_six,
        co_forest_twenty,
        tri_training,
    ]

    cls_names = ["RF", "DC", "CoF_CLT", "CoF_PL", "TT"]

    return cls, cls_names


def get_first_last_feature(features):
    """Returns the first and last feature index.

    Args:
        features (str): Features to be used.

    Returns:
        tuple: (first_feature, last_feature) where first_feature is the
                                             first index and last_feature
                                             is the last index.
    """
    if features == "F1-F8":
        return 0, 8

    if features == "F9":
        return 8, 9

    if features == "F10-F15":
        return 9, 15

    if features == "F16":
        return 15, 16

    if features == "F17-F19":
        return 16, 19

    return 0, 19


def get_folds(file_name, features="all", rd=5):
    """Returns the features, labels and StratifiedKFold.

    Args:
        file_name (str): File route.
        features (str, optional): Features to be used. Defaults to "all".
        rd (int, optional): Random seed. Defaults to 5.

    Returns:
        tuple: X, y, skf where X is the features, y is the labels
               and skf is the StratifiedKFold.
    """
    df = pd.read_csv(filepath_or_buffer=file_name)
    first_feature, last_feature = get_first_last_feature(features)
    X = df[df.columns[first_feature:last_feature]].values
    y = df.tag.values.astype(int)
    skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=rd)

    return X, y, skf


def get_scores_percentage(
    cls, cls_names, X, y, skf, rd=5, curve="ROC", percentage_labels=0.8
):
    """Returns the scores of the classifiers for a given percentage of labels.
    K-cross validation is used.

    Args:
        cls_names (list): List of classifiers names.
        X (np.array): Features.
        y (np.array): Labels.
        skf (StratifiedKFold): StratifiedKFold.
        rd (int, optional): Random seed. Defaults to 5.
        curve (str, optional): Type of curve used. Defaults to "ROC".
        percentage_labels (float, optional): Percentage of labels. Defaults to 0.8.

    Returns:
        tuple: (scores, recalls, precisions, f1s, AUCs) where each item is a list
                of scores, recalls, precisions, f1s or AUCs for each classifier.
                Index 0 corresponds to the first classifier, index 1 to the second...
    """
    scores = []
    recalls = []
    precisions = []
    f1s = []
    AUCs = []
    n_f = 0

    for train_index, test_index in skf.split(X, y):
        n_f += 1
        logger.info(
            f"Running time: {rd}. Perc. labels: {percentage_labels}. Fold: {n_f}"
        )
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
        L_train, U_train, Ly_train, _ = train_test_split(
            X_train,
            y_train,
            train_size=percentage_labels,
            random_state=rd,
            stratify=y_train,
        )

        scores_experiment = []
        recalls_experiment = []
        precisions_experiment = []
        AUCs_experiment = []
        f1s_experiment = []

        for cl, cl_name in zip(cls, cls_names):
            if cl_name == "RF":
                cl.fit(L_train, Ly_train)

            elif cl_name == "CoF_CLT":
                cl.fit(
                    L_train,
                    Ly_train,
                    U_train,
                    w_init_criteria="confidence_L_all",
                )
            elif cl_name == "CoF_PL":
                cl.fit(
                    L_train, Ly_train, U_train, w_init_criteria="percentage_L"
                )
            else:
                cl.fit(L_train, Ly_train, U_train)

            y_pred = cl.predict(X_test)
            scores_experiment.append(accuracy_score(y_test, y_pred))
            recalls_experiment.append(recall_score(y_test, y_pred))
            precisions_experiment.append(precision_score(y_test, y_pred))
            f1s_experiment.append(f1_score(y_test, y_pred))

            if curve == "ROC":
                fpr, tpr, _ = roc_curve(y_test, cl.predict_proba(X_test)[:, 1])
                AUCs_experiment.append(auc(fpr, tpr))

            else:
                precision, recall, _ = precision_recall_curve(
                    y_test, cl.predict_proba(X_test)[:, 1]
                )
                AUCs_experiment.append(auc(recall, precision))

        scores.append(scores_experiment)
        recalls.append(recalls_experiment)
        precisions.append(precisions_experiment)
        AUCs.append(AUCs_experiment)
        f1s.append(f1s_experiment)

    accuracys = np.mean(scores, axis=0)
    recalls = np.mean(recalls, axis=0)
    precisions = np.mean(precisions, axis=0)
    AUCs = np.mean(AUCs, axis=0)
    f1s = np.mean(f1s, axis=0)

    return accuracys, recalls, precisions, f1s, AUCs


def run_all_percentages(percentages, metrics, file_name, rd=5):
    """For a given random seed, runs all the percentages of labels and returns
    the scores. K-cross validation is used on each label percentage.

    Args:
        percentages (list): List of percentages of labels to be tested.
        metrics (list): List of metrics to be used.
        file_name (str): Name of the file containing the data.
        rd (int, optional): Random seed. It should change. Defaults to 5.

    Returns:
        dict: Dictionary with the scores for each percentage of labels
              for each classifier.
    """
    _, cls_names = get_clss()
    scores_clss = {cls: {metric: [] for metric in metrics} for cls in cls_names}

    for i in percentages:
        clss, cls_names = get_clss(rd=rd)
        X, y, skf = get_folds(file_name=file_name, features="all", rd=rd)

        logger.info(f"Running time: {rd}. Percentage of labels: {i}")
        accuracys, recalls, precisions, f1s, AUCs = get_scores_percentage(
            clss, cls_names, X, y, skf, curve="ROC", percentage_labels=i, rd=rd
        )

        for i, cls_name in enumerate(cls_names):
            scores_clss[cls_name]["Accuracy"].append(accuracys[i])
            scores_clss[cls_name]["Recall"].append(recalls[i])
            scores_clss[cls_name]["Precision"].append(precisions[i])
            scores_clss[cls_name]["F1"].append(f1s[i])
            scores_clss[cls_name]["AUC"].append(AUCs[i])

    # skipcq: PTC-W6004
    with open(
        RESULTS_DIRECTORY + f"results_classifiers_rd_{rd}.json", "w"
    ) as f:
        f.write(json.dumps(scores_clss, indent=4))
    f.close()

    return scores_clss


def run_repeated_kcross_validation(file_name, times=10):
    """Runs the repeated k-cross validation for all the classifiers.

    Args:
        file_name (str): Name of the file containing the data.
        times (int, optional): Times to repeat the k-cv. Defaults to 10.
    """
    percentages = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    metrics = ["Accuracy", "Recall", "Precision", "F1", "AUC"]

    _, cls_names = get_clss()
    general_scores_clss = {
        cls: {metric: [] for metric in metrics} for cls in cls_names
    }

    general_scores_clss_mean = {
        cls: {metric: [] for metric in metrics} for cls in cls_names
    }

    for i in range(times):
        logger.info(f"Running time: {i}")
        scores_clss = run_all_percentages(percentages, metrics, file_name, rd=i)

        for cls in cls_names:
            for metric in metrics:
                general_scores_clss[cls][metric].append(
                    scores_clss[cls][metric]
                )

    # skipcq: PTC-W6004
    with open(
        RESULTS_DIRECTORY + f"results_classifiers_repeated_kcross_{times}.json",
        "w",
    ) as f:
        f.write(json.dumps(general_scores_clss, indent=4))
        f.close()

    for cls in cls_names:
        for metric in metrics:
            general_scores_clss_mean[cls][metric] = list(
                np.mean(general_scores_clss[cls][metric], axis=0)
            )

    # skipcq: PTC-W6004
    with open(
        RESULTS_DIRECTORY
        + f"results_classifiers_repeated_kcross_mean_{times}.json",
        "w",
    ) as f:
        f.write(json.dumps(general_scores_clss_mean, indent=4))
        f.close()


# Global logger object
logger = get_logger()

if __name__ == "__main__":
    run_repeated_kcross_validation(
        times=10, file_name="./fv/results-5_fvg3/mix.csv"
    )
