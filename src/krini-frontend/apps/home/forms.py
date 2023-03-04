# -*- encoding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import TextField, SelectField, SubmitField
from wtforms.validators import DataRequired

#  report blacklist/whitelist url

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