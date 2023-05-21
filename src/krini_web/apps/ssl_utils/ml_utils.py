#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   ml_utils.py
@Time    :   2023/03/30 21:07:19
@Author  :   Patricia Hernando Fernández 
@Version :   1.0
@Contact :   phf1001@alu.ubu.es
@Desc    :   Utils file to create the ML models for the site
"""

import os
import sys
import pickle
import logging
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from apps.home.exceptions import KriniException
from apps.config import DECISION_TREE_KEY, KNN_KEY, NAIVE_BAYES_KEY
from apps.messages import (
    get_exception_message,
    get_constants_message,
    get_message,
)

# Changing paths to src
src_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
sys.path.append(src_path)
from models.classifiers.DemocraticCoClassifier import DemocraticCo
from models.classifiers.TriTrainingClassifier import TriTraining
from models.classifiers.CoForestClassifier import CoForest
from phishing_fvg.phishing_vector_generator import PhishingFVG
from phishing_fvg.user_browsing import UserBrowsing
from phishing_fvg.phishing_utils import (
    get_tfidf,
    get_tfidf_corpus,
    get_csv_data,
    get_data_path,
)


def get_logger(
    name,
    file_name="log_krini",
    logger_level=logging.DEBUG,
    file_level=logging.DEBUG,
):
    """
    Returns a logger with the given name and the given
    parameters.

    Args:
        name (str): logger name.
        file_name(str, optional): file name. Defaults to "log_krini".
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


logger = get_logger("krini-frontend")


def get_co_forest(
    n_trees=3, theta=0.75, max_features="log2", random_state=None
):
    """
    Returns a CoForest classifier

    Args:
        n_trees (int, optional): number of trees. Defaults to 3.
        theta (float, optional): confidence. Defaults to 0.75.
        max_features (str, optional): decision tree split paramenter.
                                      'sqrt' or 'log2'. Defaults to "log2".
        random_state (int, optional): int to generate random state if desired.
                                      Defaults to None.

    Returns:
        object: CoForest classifier
    """
    return CoForest(n_trees, theta, max_features, random_state)


def get_tri_training(h_0, h_1, h_2, random_state=None):
    """
    Returns a TriTraining classifier.
    Strs of the base classifiers are passed as parameters.
    Possible values: "DT", "kNN", "NB".

    Args:
        h_0 (str): name of the first classifier.
        h_1 (str): name of the second classifier.
        h_2 (str): name of the third classifier.
        random_state (int, optional): int to generate random state if desired.

    Returns:
        object: TriTraining classifier
    """
    return TriTraining(
        get_base_cls(h_0), get_base_cls(h_1), get_base_cls(h_2), random_state
    )


def get_democratic_co(base_cls, random_state=None):
    """
    Returns a DemocraticCo classifier.
    Strs of the base classifiers are passed as parameters in a list.
    Possible values: "DT", "kNN", "NB".

    Args:
        base_cls (list): list of base classifiers.
        random_state (int, optional): int to generate random state if desired.

    Returns:
        object: DemocraticCo classifier
    """
    base_cls_obj = [get_base_cls(cls) for cls in base_cls]
    return DemocraticCo(base_cls_obj, random_state)


def get_array_scores(y_test, y_pred, y_pred_proba, want_message=False):
    """
    Returns the accuracy, precision, recall
    f1 and ROC auc scores of the model

    Args:
        y_test (list): list with the real labels
        y_pred (list): list with the predicted labels
        y_pred_proba (list): list with the predicted probabilities
        want_message (bool, optional): if True, returns a message

    Returns:
       (list, str) : tuple containing list with the scores
                     and info about possible errors (or None)
    """
    # filterwarnings("error", category=UndefinedMetricWarning)
    message = None

    try:
        if y_pred_proba.ndim == 1:
            if 1 in y_pred:
                y_pred_proba = np.array(
                    [1 - y_pred_proba, y_pred_proba]
                ).transpose()

            else:
                y_pred_proba = np.array(
                    [y_pred_proba, 1 - y_pred_proba]
                ).transpose()

        auc_score = float(roc_auc_score(y_test, y_pred_proba[:, 1]))

    except (ValueError, IndexError):
        auc_score = 0.0

    metrics = []

    for metric in [
        ("accuracy", accuracy_score(y_test, y_pred)),
        ("precision", precision_score(y_test, y_pred)),
        ("recall", recall_score(y_test, y_pred)),
        ("F1", f1_score(y_test, y_pred)),
        ("AUC ROC", auc_score),
    ]:
        calculated = metric[1]
        metrics.append(calculated)

        if calculated == 0.0:
            if not message:
                message = get_message("zero_scores")

            message += f"{metric[0]}, "

    if message:
        message = message[:-2]
        message += get_message("zero_scores_end")

    if want_message:
        return metrics, message

    return metrics


def get_base_cls(wanted_cls):
    """
    Returns a base classifier from a string.

    Args:
        wanted_cls (str): string with the name of the classifier.
                          Possible values: "DT", "kNN", "NB".

    Raises:
        ValueError: if the classifier is not found.

    Returns:
        object: classifier
    """
    if wanted_cls == DECISION_TREE_KEY:
        return DecisionTreeClassifier()

    if wanted_cls == KNN_KEY:
        return KNeighborsClassifier()

    if wanted_cls == NAIVE_BAYES_KEY:
        return GaussianNB()

    raise ValueError(get_exception_message("base_cls_not_found"))


def generate_tfidf_object(n_documents=100, file_name="tfidf.pkl"):
    """Generates a tfidf object and saves it in a file. Documents are webs from Alexa.

    Args:
        n_documents (int, optional): Number of docs. Defaults to 100.
        file_name (str, optional): File name. Defaults to "tfidf.pkl".
    """
    user = UserBrowsing()
    urls = get_csv_data(get_data_path() + os.sep + "alexa_filtered.csv")[
        :n_documents
    ]
    corpus = get_tfidf_corpus(
        urls, user.get_simple_user_header_agent(), user.proxies
    )
    tfidf = get_tfidf(corpus)
    serialize_model(tfidf, file_name, get_tfidf_directory())


def get_tfidf_object(file_name):
    """Deserializes a tfidf object from a file.

    Args:
        file_name (str): File name.

    Returns:
        object: tfidf object
    """
    return deserialize_model(file_name, get_tfidf_directory())


def get_fv_and_info(
    url, tfidf_file="tfidf.pkl", get_proxy_from_file=False, proxy=None
):
    """
    Returns the feature vector and the info of a url.
    It is assumed that the URL is callable via requests.

    Args:
        url (str): url to get the feature vector from.
        tfidf_file (str, optional): tfidf file. Defaults to "tfidf.pkl".
        get_proxy_from_file (bool, optional): If TOR is getted. Defaults to False.
        proxy (dict, optional): Proxy if desired. Defaults to None.
    """
    try:
        logger.info("Getting feature vector and info from url")
        tfidf = get_tfidf_object(tfidf_file)
        logger.info("TFIDF object loaded")
        ph_entity = PhishingFVG(url, tfidf, get_proxy_from_file, proxy)
        logger.info("PhishingFVG object created")
        ph_entity.set_feature_vector()
        logger.info("Feature vector setted")
        return ph_entity.fv, ph_entity.extra_information

    except Exception as e:
        logger.info(str(e))
        raise KriniException(str(e))


def get_mock_values_fv():
    """Returns mock values for the feature vector.

    Returns:
        (array, dict): mock values and mock extra information
    """
    fv = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 1, 0, 0, 0, 1, 1, 1, 1])
    fv_extra_information = {
        "f1": 2,
        "f2": "@",
        "f3": 51,
        "f4": "login",
        "f5": ".cat",
        "f6": "no",
        "f7": "microsoft",
        "f8": 3,
        "f9": 1,
        "f10": "5",
        "f11": "no",
        "f12": 2,
        "f13": 3,
        "f14": 4,
        "f15": 5,
        "f16": "yes",
        "f17": "",
        "f18": "",
        "f19": "yes",
    }

    return fv, fv_extra_information


def translate_tag(tag, caps=False):
    """
    Translates the tag to a human readable string.

    Args:
        tag (int): tag to translate.
        caps (bool, optional): whether to return the string
                               in uppercase or not. Defaults to
                               False.

    Returns:
        str: human readable string.
    """
    translated_tag = ""

    if tag == 0:
        translated_tag = get_constants_message("legitimate_upper")

    elif tag == 1:
        translated_tag = "PHISHING"

    if caps:
        return translated_tag

    return translated_tag.lower()


def get_models_directory():
    """
    Returns the path to the directory where the models are stored.

    Returns:
        str: path to the directory where the models are stored.
    """
    current_dir = os.path.abspath(os.path.realpath(__file__))
    parent_dir = os.path.abspath(os.path.dirname(current_dir))
    models_path = os.path.abspath(os.path.join(parent_dir, "pickle_models"))

    if not os.path.exists(models_path):
        os.makedirs(models_path)

    return models_path


def get_temporary_train_files_directory():
    """
    Returns the path to the directory where the temporary train files are stored.

    Returns:
        str: path to the directory where the temporary train files are stored.
    """
    current_dir = os.path.abspath(os.path.realpath(__file__))
    parent_dir = os.path.abspath(os.path.dirname(current_dir))
    files_path = os.path.abspath(
        os.path.join(parent_dir, "temporal" + os.path.sep + "train_files")
    )

    if not os.path.exists(files_path):
        os.makedirs(files_path)

    return files_path


def get_temporary_download_directory():
    """
    Returns the path to the directory
    where the temporary downloads files are stored.

    Returns:
        str: path to the directory where the temporary downloads files are stored.
    """
    current_dir = os.path.abspath(os.path.realpath(__file__))
    parent_dir = os.path.abspath(os.path.dirname(current_dir))
    files_path = os.path.abspath(
        os.path.join(parent_dir, "temporal" + os.path.sep + "downloads")
    )

    if not os.path.exists(files_path):
        os.makedirs(files_path)

    return files_path


def get_tfidf_directory():
    """
    Obtains the path to the directory where the tfidf objects are stored.

    Returns:
        str: path to the directory where the tfidf objects are stored.
    """
    current_dir = os.path.abspath(os.path.realpath(__file__))
    parent_dir = os.path.abspath(os.path.dirname(current_dir))
    return os.path.abspath(os.path.join(parent_dir, "tfidf_objects"))


def get_models_files_list():
    """
    Returns a list of the models available and serialized.
    Checks the directory.

    Returns:
        list: list of the models available and serialized.
    """
    models_path = get_models_directory()
    return os.listdir(models_path)


def obtain_model(model_file_name):
    """
    Obtains a model from a pickle file if it is available.
    Also includes a flag to check if exists

    Args:
        model_file_name (str): name of the file where the model is serialized.

    Returns:
        tuple: model object, flag to check if exists.
    """
    if ".pkl" not in model_file_name:
        model_file_name += ".pkl"

    available_models = get_models_files_list()

    if model_file_name in available_models:
        return deserialize_model(model_file_name), True

    return None, False


def serialize_model(model, filename, models_path=None):
    """
    Serializes a model to a pickle file.

    Args:
        model (object): model to serialize.
        filename (str): name of the file to serialize the model.
        models_path (str, optional): path to the directory where the models
                                     are stores. If none, it will be obtained
                                     from the get_models_directory() function.
    Raises:
        pickle.PicklingError: if there is an error serializing the model.

    Returns:
        str: path to the file where the model was serialized.
    """
    if models_path is None:
        models_path = get_models_directory()

    file_location = models_path + os.sep + filename

    with open(file_location, "wb") as f:
        pickle.dump(model, f)

    return file_location


def deserialize_model(filename, models_path=None):
    """Deserializes a model from a pickle file.

    Args:
        filename (str): name of the file where the model is serialized.
        models_path (str, optional): path if not default. Defaults to None.

    Returns:
        _type_: _description_
    """
    if models_path is None:
        models_path = get_models_directory()

    with open(models_path + os.sep + filename, "rb") as f:
        return pickle.load(f)
