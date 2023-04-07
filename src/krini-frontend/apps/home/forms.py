#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   models.py
@Time    :   2023/03/30
@Author  :   Patricia Hernando Fernández 
@Version :   1.0
@Contact :   phf1001@alu.ubu.es
'''

from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import TextField, SelectField, HiddenField, IntegerField
from wtforms.validators import DataRequired

NAIVE_BAYES_NAME = "Naive Bayes"
DECISION_TREE_NAME = "Árbol de decisión"
KNN_NAME = "k-vecinos más cercanos"

class ReportURLForm(FlaskForm):
    """
    Form used to report a URL (whitelist or blacklist)

    Args:
        FlaskForm (class): parent class
    """
    url = TextField(
        "url", id="url_report", validators=[DataRequired("Introduce una URL")]
    )
    type = SelectField(
        "type",
        id="type",
        choices=[("black-list", "Blacklist"), ("white-list", "Whitelist")],
    )

class SearchURLForm(FlaskForm):
    """
    Form used to make the analysis of a URL
    in the index page.

    Args:
        FlaskForm (class): parent class
    """
    url = TextField(
        "url", id="url_search", validators=[DataRequired("Introduce una URL")]
    )
    selected_models = HiddenField(
        "selected_models", render_kw={"id": "selected_models"}
    )

class NewModelForm(FlaskForm):
    """TODO revisar campos obligatorios, docstring

    Args:
        FlaskForm (class): parent class
    """
    model_name = TextField(
        "model_name", id="model_name", validators=[DataRequired("Introduce un nombre")]
    )

    model_version = TextField(
        "model_version", id="model_version", validators=[DataRequired("Introduce una versión")]
    )

    model_description = TextField(
        "model_description", id="model_description"
    )

    model_algorithm = TextField(
        "model_algorithm", id="model_algorithm"
    )

    is_visible = SelectField(
        "is_visible", id="is_visible", choices=[("True", "Visible"), ("False", "No visible")]
    )

    is_default = SelectField(
        "is_default", id="is_default", choices=[("False", "No"), ("True", "Sí")]
    )

    random_state = IntegerField(
        "random_state", id="random_state"
    )

    uploaded_train_csv = FileField(
        "train_file", id="train_file"
    )

    uploaded_test_csv = FileField(
        "test_file", id="test_file"
    )

    train_n_instances = IntegerField(
        "train_n_instances", id="train_n_instances"
    )

    #(no se puede hacer una herencia por las características dinámicas de los formularios)
    #coforest
    max_features = SelectField(
        "max_features", id="max_features", choices=[("log2", "Logaritmo base 2"), ("sqrt", "Raíz cuadrada")]
    )

    n_trees = TextField(  
        "n_trees", id="n_trees"
    )

    thetha = TextField(
        "thetha", id="thetha"
    )

    #tritraining
    cls_one = SelectField(
        "cls_one", id="cls_one", choices=[("kNN", KNN_NAME), ("NB", NAIVE_BAYES_NAME), ("tree", DECISION_TREE_NAME)]
    )

    cls_two = SelectField(
        "cls_two", id="cls_two", choices=[("kNN", KNN_NAME), ("NB", NAIVE_BAYES_NAME), ("tree", DECISION_TREE_NAME)]
    )

    cls_three = SelectField(
        "cls_three", id="cls_three", choices=[("kNN", KNN_NAME), ("NB", NAIVE_BAYES_NAME), ("tree", DECISION_TREE_NAME)]
    )

    # democratic-co
    n_cls_one = IntegerField(
        "n_cls_one", id="n_cls_one"
    )

    n_cls_two = IntegerField(
        "n_cls_two", id="n_cls_two"
    )

    n_cls_three = IntegerField(
        "n_cls_three", id="n_cls_three"
    )
