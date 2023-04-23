#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   exceptions.py
@Time    :   2023/04/03 12:55:58
@Author  :   Patricia Hernando Fernández (modified)
@Version :   2.0
@Contact :   phf1001@alu.ubu.es
@Copy    :  (c) 2019 - present AppSeed.us
"""
import os
from decouple import config

# Constants
NAIVE_BAYES_NAME = "Naive Bayes"
DECISION_TREE_NAME = "Árbol de decisión"
KNN_NAME = "k-vecinos más cercanos"
NAIVE_BAYES_KEY = "NB"
DECISION_TREE_KEY = "tree"
KNN_KEY = "kNN"


class Config(object):
    basedir = os.path.abspath(os.path.dirname(__file__))
    superiordir = os.getcwd()

    # Set up the App SECRET_KEY
    SECRET_KEY = config("SECRET_KEY", default="S#perS3crEt_007")
    WTF_CSRF_SECRET_KEY = config(
        "WTF_CSRF_SECRET_KEY", default="S#perS3crEt_007"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BABEL_DEFAULT_LOCALE = "en"
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(superiordir, "translations")
    LANGUAGES = {"en": "English", "es": "Spanish"}


class ProductionConfig(Config):
    DEBUG = False
    database_url = os.environ.get("DATABASE_URL")

    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = database_url
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600


class DebugConfig(Config):
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
