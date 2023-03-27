# -*- encoding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import TextField, SelectField, HiddenField, IntegerField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired


class ReportURLForm(FlaskForm):
    url = TextField(
        "url", id="url_report", validators=[DataRequired("Introduce una URL")]
    )
    type = SelectField(
        "type",
        id="type",
        validators=[DataRequired("URL is required")],
        choices=[("blacklist", "Blacklist"), ("whitelist", "Whitelist")],
    )

class CheckBoxForm(FlaskForm):
    selected_checkboxes = HiddenField(
        "selected_checkboxes", render_kw={"id": "selected_models"}
    )

    page = IntegerField(
        "page"
    )


class SearchURLForm(FlaskForm):
    url = TextField(
        "url", id="url_search", validators=[DataRequired("Introduce una URL")]
    )
    selected_models = HiddenField(
        "selected_models", render_kw={"id": "selected_models"}
    )

class NewModelForm(FlaskForm):
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
        "cls_one", id="cls_one", choices=[("kNN", "K vecinos más cercanos"), ("NB", "Naive Bayes"), ("tree", "Árbol de decisión")]
    )

    cls_two = SelectField(
        "cls_two", id="cls_two", choices=[("kNN", "K vecinos más cercanos"), ("NB", "Naive Bayes"), ("tree", "Árbol de decisión")]
    )

    cls_three = SelectField(
        "cls_three", id="cls_three", choices=[("kNN", "K vecinos más cercanos"), ("NB", "Naive Bayes"), ("tree", "Árbol de decisión")]
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

# class NewCoforestForm(NewModelForm):
#     max_features = SelectField(
#         "max_features", id="max_features", choices=[("log2", "Logaritmo base 2"), ("sqrt", "Raíz cuadrada")]
#     )

#     n_trees = TextField(  
#         "n_trees", id="n_trees", validators=[DataRequired("Introduce un número")]
#     )

#     thetha = TextField(
#         "thetha", id="thetha", validators=[DataRequired("Introduce un número")]
#     )
