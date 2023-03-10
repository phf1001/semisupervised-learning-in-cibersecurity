# Utils file to create the ML models for the site

import os
import sys
import pickle
import numpy as np

from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split

# Changing paths to src
src_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
sys.path.append(src_path)
from models.classifiers.DemocraticCoClassifier import DemocraticCo
from models.classifiers.TriTrainingClassifier import TriTraining
from models.classifiers.CoForestClassifier import CoForest


def get_models_directory():
    """
    Returns the path to the directory
    where the models are stored.
    """
    current_dir = os.path.abspath(os.path.realpath(__file__))
    parent_dir = os.path.abspath(os.path.dirname(current_dir))
    models_path = os.path.abspath(os.path.join(parent_dir, 'pickle_models'))
    return models_path 

def obtain_model(model_name):
    """
    Obtains a model from a pickle file if
    it is available, otherwise it returns the
    default model.
    """
    if '.pkl' not in model_name:
        model_name += '.pkl'

    available_models = os.listdir(get_models_directory())

    if model_name in available_models:
        return deserialize_model(model_name)
    
    else:
        return deserialize_model('default.pkl')


def serialize_model(model, filename):
    """Serializes a model to a pickle file"""
    with open(get_models_directory() + os.sep + filename, 'wb') as f:
        pickle.dump(model, f)


def deserialize_model(filename):
    """Deserializes a model from a pickle file"""
    with open(get_models_directory() + os.sep + filename, 'rb') as f:
        return pickle.load(f)
    

def create_democratic_co(model_name, X, y):
    """
    Creates a democratic co classifier, trains it
    and saves it to a pickle file to be used.
    """
    democratic_co = DemocraticCo(cls = [DecisionTreeClassifier(), 
                                         GaussianNB(), 
                                         KNeighborsClassifier(5)], 
                                random_state=10)

    L_train, U_train, Ly_train, Uy_train = train_test_split(
                X, y, test_size=0.8, random_state=5, stratify=y)

    democratic_co.fit(L_train, Ly_train, U_train)
    serialize_model(democratic_co, model_name + '.pkl')
