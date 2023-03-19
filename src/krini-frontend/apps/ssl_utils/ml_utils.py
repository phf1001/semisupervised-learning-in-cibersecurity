# Utils file to create the ML models for the site

import os
import sys
import pickle
import numpy as np

from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split

from apps.home.models import Available_models

# Changing paths to src
src_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
sys.path.append(src_path)
from models.classifiers.DemocraticCoClassifier import DemocraticCo
from models.classifiers.TriTrainingClassifier import TriTraining
from models.classifiers.CoForestClassifier import CoForest
from phishing_fvg.phishing_vector_generator import PHISH_FVG
from phishing_fvg.user_browsing import user_browsing
from phishing_fvg.phishing_utils import get_tfidf, get_tfidf_corpus, get_csv_data, get_data_path


def generate_tfidf_object(n_documents=100, file_name="tfidf.pkl"):

    user = user_browsing()
    urls = get_csv_data(get_data_path() + os.sep + "alexa_filtered.csv")[: n_documents]
    corpus = get_tfidf_corpus(urls, user.get_simple_user_header_agent(), user.proxies)
    tfidf = get_tfidf(corpus)
    serialize_model(tfidf, file_name, get_tfidf_directory())


def get_tfidf_object(file_name):
    return deserialize_model(file_name, get_tfidf_directory())


def get_fv_and_info(url, tfidf_file="tfidf.pkl", get_proxy_from_file=False, proxy=None):
    """Returns the feature vector and the info of a url"""
    
    # Reintentos, comprobar protocolos, etc
    try:
        msg = "tfidf"
        tfidf = get_tfidf_object(tfidf_file)

        msg = "phishing_fvg"
        ph_entity = PHISH_FVG(url, tfidf, get_proxy_from_file, proxy)
        ph_entity.set_feature_vector()
        return ph_entity.fv, ph_entity.extra_information

    #De momento mock values pero esta función hay que trabajarla mucho
    except:
        raise Exception(msg)

def get_mock_values_fv():
    """Returns a mock feature vector and extra information"""
    fv = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 1, 0, 0, 0, 1, 1, 1, 1])
    fv_extra_information = {"f1": 322, 
                            "f2": '@',
                            "f3": 56,
                            "f4": 'login',
                            "f5": '.cat', #TDL extra encontrado
                            "f6": 'No',
                            "f7": 'Google',
                            "f8": 'No',
                            "f9": 'asterisco',
                            "f10": '5',
                            "f11": 'No', #vacia
                            "f12": 2,
                            "f13": 3,
                            "f14": 4,
                            "f15": 5,
                            "f16": 'No',
                            "f17": 'Natura',
                            "f18": 'Natura',
                            "f19": 'No'
                            }
    
    return fv, fv_extra_information


def translate_tag(tag, caps=False):
    """Translates numerical tags to string."""

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
    Returns the path to the directory
    where the models are stored.
    """
    current_dir = os.path.abspath(os.path.realpath(__file__))
    parent_dir = os.path.abspath(os.path.dirname(current_dir))
    models_path = os.path.abspath(os.path.join(parent_dir, "pickle_models"))
    return models_path


def get_tfidf_directory():
    """
    Returns the path to the directory
    where the tfidf objects are stored.
    """
    current_dir = os.path.abspath(os.path.realpath(__file__))
    parent_dir = os.path.abspath(os.path.dirname(current_dir))
    return os.path.abspath(os.path.join(parent_dir, "tfidf_objects"))


def get_models_files_list():
    """
    Returns a list of the models
    available and serialized.
    Checks the directory.
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

    else:
        return deserialize_model("default.pkl"), False


def serialize_model(model, filename, models_path=None):
    """Serializes a model to a pickle file"""
    if models_path is None:
        models_path = get_models_directory()

    with open(models_path + os.sep + filename, "wb") as f:
        pickle.dump(model, f)


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
