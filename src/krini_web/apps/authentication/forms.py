#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   forms.py
@Time    :   2023/03/30 21:05:09
@Author  :   Patricia Hernando Fernández 
@Version :   1.0
@Contact :   phf1001@alu.ubu.es

Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired

from apps.messages import get_form_message

class LoginForm(FlaskForm):
    """
    LoginForm class. It is used to create a form to login in the application.

    Args:
        FlaskForm (class): FlaskForm class from Flask-WTF.
    """

    username = TextField(
        "Username",
        id="username_login",
        validators=[DataRequired(get_form_message("no_username"))],
    )
    password = PasswordField(
        "Password",
        id="pwd_login",
        validators=[DataRequired(get_form_message("no_password"))],
    )


class CreateAccountForm(FlaskForm):
    """
    Form to create a new account. It is used to create a new account in the application.

    Args:
        FlaskForm (class): FlaskForm class from Flask-WTF.
    """

    username = TextField(
        "Username",
        id="username_create",
        validators=[DataRequired("Heyy")],
    )

    email = TextField(
        "Email",
        id="email_create",
        validators=[DataRequired(get_form_message("no_email"))],
    )

    password = PasswordField(
        "Password",
        id="pwd_create",
        validators=[DataRequired(get_form_message("no_password"))],
    )

    user_first_name = TextField(
        "Name",
        id="name_create",
        validators=[DataRequired(get_form_message("no_name"))],
    )

    user_last_name = TextField(
        "Surname",
        id="surname_create",
        validators=[DataRequired(get_form_message("no_surname"))],
    )
