#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   models.py
@Time    :   2023/03/30
@Author  :   Patricia Hernando Fernández 
@Version :   1.0
@Contact :   phf1001@alu.ubu.es
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import (
    TextField,
    SelectField,
    HiddenField,
    IntegerField,
    FloatField,
)
from wtforms.validators import DataRequired, Regexp, NumberRange

from apps.config import (
    NAIVE_BAYES_KEY,
    NAIVE_BAYES_NAME,
    DECISION_TREE_KEY,
    DECISION_TREE_NAME,
    KNN_KEY,
    KNN_NAME,
)

available_base_cls = [
    (NAIVE_BAYES_KEY, NAIVE_BAYES_NAME),
    (KNN_KEY, KNN_NAME),
    (DECISION_TREE_KEY, DECISION_TREE_NAME),
]


class ReportURLForm(FlaskForm):
    """
    Form used to report a URL (whitelist or blacklist)

    Args:
        FlaskForm (class): parent class
    """

    url = TextField(
        "url",
        id="url_report",
        validators=[DataRequired("empty_url")],
    )
    type = SelectField(
        "type",
        id="type",
        choices=[("black-list", "Blacklist"), ("white-list", "Whitelist")],
        validators=[DataRequired("no_option_selected")],
    )


class SearchURLForm(FlaskForm):
    """
    Form used to make the analysis of a URL
    in the index page.

    Args:
        FlaskForm (class): parent class
    """

    url = TextField(
        "url",
        id="url_search",
        validators=[DataRequired("empty_url")],
    )
    selected_models = HiddenField(
        "selected_models", render_kw={"id": "selected_models"}
    )


class InstanceForm(FlaskForm):
    """
    Form used to create or edit an instance.

    Args:
        FlaskForm (class): parent class
    """

    url = TextField(
        "url", id="url_instance", validators=[DataRequired("empty_url")]
    )

    instance_class = SelectField(
        "instance_class",
        id="instance-class",
        choices=[
            (-1, "Mantener valor actual"),
            (1, "Phishing"),
            (0, "Legítima"),
        ],
    )

    instance_list = SelectField(
        "instance_list",
        id="instance-list",
        choices=[
            (-1, "Mantener valor actual"),
            ("black-list", "Black-list"),
            ("white-list", "White-list"),
        ],
    )

    regenerate_fv = SelectField(
        "regenerate_fv",
        id="regenerate-fv",
        choices=[
            (-1, "Mantener vector actual"),
            (1, "Generar nuevo vector de características"),
        ],
    )


class SmallModelForm(FlaskForm):
    """
    Form used to edit models.

    Args:
        FlaskForm (class): parent class
    """

    model_version = TextField(
        "model_version",
        id="model_version",
        default="1",
        validators=[
            Regexp(
                r"^\d+(.\d){0,2}$",
                message="invalid_version",
            )
        ],
    )

    model_description = TextField("model_description", id="model_description")

    model_algorithm = TextField("model_algorithm", id="model_algorithm")

    is_visible = SelectField(
        "is_visible",
        id="is_visible",
        choices=[("True", "Visible"), ("False", "No visible")],
        default="True",
    )

    is_default = SelectField(
        "is_default",
        id="is_default",
        choices=[("False", "No"), ("True", "Sí")],
        default="False",
    )


class ModelForm(SmallModelForm):
    """
    Form used to manage models.

    Args:
        FlaskForm (class): parent class
    """

    model_name = TextField(
        "model_name",
        id="model_name",
        validators=[DataRequired("empty_name")],
    )

    random_state = IntegerField(
        "random_state",
        id="random_state",
        default=-1,
        validators=[
            DataRequired("empty_random_state"),
        ],
    )

    uploaded_train_csv = FileField("train_file", id="train_file")

    uploaded_test_csv = FileField("test_file", id="test_file")

    train_percentage_instances = IntegerField(
        "train_percentage_instances",
        id="train_percentage_instances",
        default=80,
        validators=[
            DataRequired("empty_train_percentage_instances"),
            NumberRange(
                min=1,
                max=99,
                message="invalid_train_percentage_instances",
            ),
        ],
    )

    # co-forest
    max_features = SelectField(
        "max_features",
        id="max_features",
        choices=[("log2", "Log2"), ("sqrt", "SQRT")],
        default="log2",
    )

    n_trees = IntegerField(
        "n_trees",
        id="n_trees",
        default=6,
        validators=[
            DataRequired("empty_n_trees"),
            NumberRange(
                min=0,
                max=100,
                message="invalid_n_trees",
            ),
        ],
    )

    thetha = FloatField(
        "thetha",
        id="thetha",
        default=0.75,
        validators=[
            DataRequired("empty_thetha"),
            NumberRange(
                min=0.0,
                max=1.0,
                message="invalid_thetha",
            ),
        ],
    )

    # tri-training

    cls_one_tt = SelectField(
        "cls_one", id="cls_one", choices=available_base_cls
    )

    cls_two_tt = SelectField(
        "cls_two", id="cls_two", choices=available_base_cls
    )

    cls_three_tt = SelectField(
        "cls_three", id="cls_three", choices=available_base_cls
    )

    # democratic-co
    cls_one = SelectField("cls_one", id="cls_one", choices=available_base_cls)

    cls_two = SelectField("cls_two", id="cls_two", choices=available_base_cls)

    cls_three = SelectField(
        "cls_three", id="cls_three", choices=available_base_cls
    )

    n_cls_one = IntegerField(
        "n_cls_one",
        id="n_cls_one",
        default=0,
        validators=[
            NumberRange(
                min=0,
                max=10,
                message="invalid_n_clss",
            ),
        ],
    )

    n_cls_two = IntegerField(
        "n_cls_two",
        id="n_cls_two",
        default=0,
        validators=[
            NumberRange(
                min=0,
                max=10,
                message="invalid_n_clss",
            ),
        ],
    )

    n_cls_three = IntegerField(
        "n_cls_three",
        id="n_cls_three",
        default=0,
        validators=[
            NumberRange(
                min=0,
                max=10,
                message="invalid_n_clss",
            ),
        ],
    )


class TestModelForm(FlaskForm):
    """
    Form used to test models.

    Args:
        FlaskForm (class): parent class
    """

    model_name = TextField(
        "model_name",
        id="model_name",
        validators=[DataRequired("empty_name")],
    )

    uploaded_test_csv = FileField("uploaded_test_csv", id="uploaded_test_csv")