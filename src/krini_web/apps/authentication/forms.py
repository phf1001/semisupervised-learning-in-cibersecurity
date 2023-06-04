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
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    """
    LoginForm class. It is used to create a form to login in the application.

    Args:
        FlaskForm (class): FlaskForm class from Flask-WTF.
    """

    username = TextField(
        "Username",
        id="username_login",
        validators=[
            DataRequired("no_username"),
            Length(min=1, max=63, message="username_too_long"),
        ],
    )
    password = PasswordField(
        "Password",
        id="pwd_login",
        validators=[DataRequired("no_password")],
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
        validators=[
            DataRequired("no_username"),
            Length(min=1, max=63, message="username_too_long"),
        ],
    )

    email = TextField(
        "Email",
        id="email_create",
        validators=[
            DataRequired("no_email"),
            Length(min=1, max=127, message="email_too_long"),
        ],
    )

    password = PasswordField(
        "Password",
        id="pwd_create",
        validators=[
            DataRequired("no_password"),
            Length(min=8, message="password_too_short"),
        ],
    )

    user_first_name = TextField(
        "Name",
        id="name_create",
        validators=[
            DataRequired("no_name"),
            Length(min=1, max=63, message="first_name_too_long"),
        ],
    )

    user_last_name = TextField(
        "Surname",
        id="surname_create",
        validators=[
            DataRequired("no_surname"),
            Length(min=1, max=63, message="surname_too_long"),
        ],
    )
