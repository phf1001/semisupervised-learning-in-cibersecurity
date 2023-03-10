# Utils file to create the ML models for the site

import os
import sys
import pickle
#import numpy as np

# Changing paths to src
src_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
sys.path.append(src_path)
from models.classifiers.DemocraticCoClassifier import DemocraticCo
from models.classifiers.TriTrainingClassifier import TriTraining
from models.classifiers.CoForestClassifier import CoForest

def create_coforest():
    return None


def serialize_model(model, filename):
    with open('pickle_models' + os.sep + filename, 'wb') as f:
        pickle.dump(model, f)


def deserialize_model(filename):
    with open('pickle_models' + os.sep + filename, 'rb') as f:
        return pickle.load(f)