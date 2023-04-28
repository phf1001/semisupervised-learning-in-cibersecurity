#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   models.py
@Time    :   2023/03/30
@Author  :   Patricia Hernando Fernández 
@Version :   1.0
@Contact :   phf1001@alu.ubu.es

Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin

from apps import db, login_manager

from apps.authentication.util import hash_pass


class Users(db.Model, UserMixin):
    """
    Users class. It is used to create a table in the database
    with the users of the application.

    Args:
        db (class): db class from Flask-SQLAlchemy.
        UserMixin (class): UserMixin class from Flask-Login.

    Returns:
        class: Users class.
    """

    __tablename__ = "Users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary)
    user_first_name = db.Column(db.String(64), default="")
    user_last_name = db.Column(db.String(64), default="")
    user_rol = db.Column(db.String(64), default="standard")
    n_urls_accepted = db.Column(db.Integer, default=0)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, "__iter__") and not isinstance(value, str):
                value = value[0]

            if property == "password":
                value = hash_pass(value)  # bytes

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)


@login_manager.user_loader
def user_loader(id):
    """
    Function to load the user.

    Args:
        id (int): id of the user.

    Returns:
        object: user object if found.
    """
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    """
    Function to load the user.

    Args:
        request (object): request object.

    Returns:
        object: user object if found.
    """
    username = request.form.get("username")
    user = Users.query.filter_by(username=username).first()
    return user if user else None
