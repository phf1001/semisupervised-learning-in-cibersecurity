# -*- encoding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import TextField, SelectField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired
from apps.home.models import Available_models


class ReportURLForm(FlaskForm):
    url = TextField('url',
                         id='url_report',
                         validators=[DataRequired()])
    type = SelectField('type',
                             id='type',
                             validators=[DataRequired()],
                             choices=[('blacklist', 'Blacklist'), ('whitelist', 'Whitelist')])


class SearchURLForm(FlaskForm):
    url = TextField('url',
                         id='url_search',
                         validators=[DataRequired()])
    # selected_model = SelectField('selected_model',
    #                         id='selected_model',
    #                         validators=[DataRequired()],
    #                         choices=Available_models.get_models_ids_and_names_list() )

    selected_model = SelectMultipleField('selected_model',
                            id='selected_model',
                            validators=[DataRequired()],
                            choices=Available_models.get_models_ids_and_names_list() )