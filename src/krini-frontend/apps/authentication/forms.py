#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   forms.py
@Time    :   2023/03/30 21:05:09
@Author  :   Patricia Hernando Fernández 
@Version :   1.0
@Contact :   phf1001@alu.ubu.es

Copyright (c) 2019 - present AppSeed.us
'''

from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = TextField('Username',
                         id='username_login',
                         validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])


class CreateAccountForm(FlaskForm):
    username = TextField('Username',
                         id='username_create',
                         validators=[DataRequired()])
    email = TextField('Email',
                      id='email_create',
                      validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired()])
