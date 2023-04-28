#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   config.py
@Time    :   2023/04/03 12:55:58
@Author  :   Patricia Hernando Fernández (modified)
@Version :   2.0
@Contact :   phf1001@alu.ubu.es
@Copy    :  (c) 2019 - present AppSeed.us
"""
import os
from decouple import config
from apps.messages import get_constants_message

# Constants
CO_FOREST_CONTROL = "CO-FOREST"
TRI_TRAINING_CONTROL = "TRI-TRAINING"
DEMOCRATIC_CO_CONTROL = "DEMOCRATIC-CO"
NAIVE_BAYES_KEY = "NB"
DECISION_TREE_KEY = "DT"
KNN_KEY = "kNN"
NAIVE_BAYES_NAME = get_constants_message("naive_bayes_name")
DECISION_TREE_NAME = get_constants_message("decision_tree_name")
KNN_NAME = get_constants_message("knn_name")
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0"
)
BABEL_DEFAULT = "es"
AVAILABLE_LANGUAGES = ["en", "es"]


class Config(object):
    """General configuration class.

    Args:
        object (object): Object class.
    """

    basedir = os.path.abspath(os.path.dirname(__file__))
    superiordir = os.getcwd()
    SECRET_KEY = config("SECRET_KEY", default="S#perS3crEt_007")
    WTF_CSRF_SECRET_KEY = config(
        "WTF_CSRF_SECRET_KEY", default="S#perS3crEt_007"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BABEL_DEFAULT_LOCALE = BABEL_DEFAULT
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(superiordir, "translations")
    LANGUAGES = AVAILABLE_LANGUAGES


class ProductionConfig(Config):
    """Production configuration class.

    Args:
        Config (Config): General configuration class.
    """

    DEBUG = False
    database_url = os.environ.get("DATABASE_URL")

    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = database_url
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600


class DebugConfig(Config):
    """Debug configuration class.

    Args:
        Config (Config): General configuration class.
    """

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "{}://{}:{}@{}:{}/{}".format(
        config("DB_ENGINE", default="postgresql"),
        config("DB_USERNAME", default="dev"),
        config("DB_PASS", default="123"),
        config("DB_HOST", default="localhost"),
        config("DB_PORT", default=5432),
        config("DB_NAME", default="krini"),
    )


# Load all possible configurations
config_dict = {"Production": ProductionConfig, "Debug": DebugConfig}
