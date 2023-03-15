# -*- encoding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import TextField, SelectField, HiddenField
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
