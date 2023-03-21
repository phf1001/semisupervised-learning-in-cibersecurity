# -*- encoding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import TextField, SelectField, HiddenField, IntegerField, FileField
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

    is_visible = SelectField(
        "is_visible", id="is_visible", choices=[("True", "Visible"), ("False", "No visible")]
    )

    is_default = SelectField(
        "is_default", id="is_default", choices=[("False", "No"), ("True", "Sí")]
    )

    random_state = IntegerField(
        "random_state", id="random_state"
    )


class NewCoforestForm(NewModelForm):
    max_features = SelectField(
        "max_features", id="max_features", choices=[("log2", "Logaritmo base 2"), ("sqrt", "Raíz cuadrada")]
    )

    n_trees = TextField(  
        "n_trees", id="n_trees", validators=[DataRequired("Introduce un número")]
    )

    thetha = TextField(
        "thetha", id="thetha", validators=[DataRequired("Introduce un número")]
    )
