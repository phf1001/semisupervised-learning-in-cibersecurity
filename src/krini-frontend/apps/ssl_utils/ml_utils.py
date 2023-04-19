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
import numpy as np

from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from apps.home.exceptions import KriniException

# Changing paths to src
src_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
sys.path.append(src_path)
from models.classifiers.DemocraticCoClassifier import DemocraticCo
from models.classifiers.TriTrainingClassifier import TriTraining
from models.classifiers.CoForestClassifier import CoForest
from phishing_fvg.phishing_vector_generator import PHISH_FVG
from phishing_fvg.user_browsing import user_browsing
from phishing_fvg.phishing_utils import (
    get_tfidf,
    get_tfidf_corpus,
    get_csv_data,
    get_data_path,
)

NAIVE_BAYES_NAME = "Naive Bayes"
DECISION_TREE_NAME = "Árbol de decisión"
KNN_NAME = "k-vecinos más cercanos"

NAIVE_BAYES_KEY = "NB"
DECISION_TREE_KEY = "tree"
KNN_KEY = "kNN"


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
    Possible values: "tree", "kNN", "NB".

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
    Possible values: "tree", "kNN", "NB".

    Args:
        base_cls (list): list of base classifiers.
        random_state (int, optional): int to generate random state if desired.

    Returns:
        object: DemocraticCo classifier
    """
    base_cls_obj = [get_base_cls(cls) for cls in base_cls]
    return DemocraticCo(base_cls_obj, random_state)


def get_array_scores(y_test, y_pred, y_pred_proba):
    """
    Returns the accuracy, precision, recall
    f1 and ROC auc scores of the model

    Args:
        y_test (list): list with the real labels
        y_pred (list): list with the predicted labels
        y_pred_proba (list): list with the predicted probabilities

    Returns:
       list: list with the scores
    """
    try:
        auc_score = float(roc_auc_score(y_test, y_pred_proba[:, 1]))

    except ValueError:
        auc_score = 0.0

    return [
        float(accuracy_score(y_test, y_pred)),
        float(precision_score(y_test, y_pred)),
        float(recall_score(y_test, y_pred)),
        float(f1_score(y_test, y_pred)),
        auc_score,
    ]


def get_base_cls(wanted_cls):
    """
    Returns a base classifier from a string.

    Args:
        wanted_cls (str): string with the name of the classifier.
                          Possible values: "tree", "kNN", "NB".

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

    raise ValueError("Clasificador no encontrado")


def generate_tfidf_object(n_documents=100, file_name="tfidf.pkl"):
    user = user_browsing()
    urls = get_csv_data(get_data_path() + os.sep + "alexa_filtered.csv")[
        :n_documents
    ]
    corpus = get_tfidf_corpus(
        urls, user.get_simple_user_header_agent(), user.proxies
    )
    tfidf = get_tfidf(corpus)
    serialize_model(tfidf, file_name, get_tfidf_directory())


def get_tfidf_object(file_name):
    return deserialize_model(file_name, get_tfidf_directory())


def get_fv_and_info(
    url, tfidf_file="tfidf.pkl", get_proxy_from_file=False, proxy=None
):
    """
    Returns the feature vector and the info of a url.
    It is assumed that the URL is callable via requests.
    """
    try:
        msg = "Error reconstruyendo el objeto TFIDF"
        tfidf = get_tfidf_object(tfidf_file)

        msg = "Error extrayendo el vector de características"
        ph_entity = PHISH_FVG(url, tfidf, get_proxy_from_file, proxy)
        ph_entity.set_feature_vector()
        return ph_entity.fv, ph_entity.extra_information

    except Exception:
        raise KriniException(msg)


def get_mock_values_fv():
    """Returns a mock feature vector and extra information"""
    fv = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 1, 0, 0, 0, 1, 1, 1, 1])
    fv_extra_information = {
        "f1": 322,
        "f2": "@",
        "f3": 56,
        "f4": "login",
        "f5": ".cat",  # TDL extra encontrado
        "f6": "No",
        "f7": "Google",
        "f8": "No",
        "f9": "asterisco",
        "f10": "5",
        "f11": "No",  # vacia
        "f12": 2,
        "f13": 3,
        "f14": 4,
        "f15": 5,
        "f16": "No",
        "f17": "Natura",
        "f18": "Natura",
        "f19": "No",
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
        translated_tag = "LEGÍTIMA"

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
    Obtains a model from a pickle file if
    it is available, otherwise it returns the
    default model.

    Also includes a flag to check if exists
    """
    if ".pkl" not in model_file_name:
        model_file_name += ".pkl"

    available_models = get_models_files_list()

    if model_file_name in available_models:
        return deserialize_model(model_file_name), True
    return deserialize_model("default.pkl"), False


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
    """Deserializes a model from a pickle file"""
    if models_path is None:
        models_path = get_models_directory()

    with open(models_path + os.sep + filename, "rb") as f:
        return pickle.load(f)


def create_democratic_co(model_name, X, y):
    """
    Creates a democratic co classifier, trains it
    and saves it to a pickle file to be used.
    """
    democratic_co = DemocraticCo(
        cls=[DecisionTreeClassifier(), GaussianNB(), KNeighborsClassifier(5)],
        random_state=10,
    )

    L_train, U_train, Ly_train, Uy_train = train_test_split(
        X, y, test_size=0.8, random_state=5, stratify=y
    )

    democratic_co.fit(L_train, Ly_train, U_train)
    serialize_model(democratic_co, model_name + ".pkl")
