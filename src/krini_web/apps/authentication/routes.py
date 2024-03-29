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

from flask import render_template, redirect, request, url_for, flash
from flask_login import current_user, login_user, logout_user
import re
from sqlalchemy.exc import SQLAlchemyError
from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import Users
from apps.home.exceptions import KriniException
from apps.authentication.util import verify_pass
from apps.messages import get_form_message, get_exception_message


@blueprint.route("/")
def route_default():
    """
    Redirects to the index page (scan page).

    Returns:
        function: redirect to the index page.
    """
    return redirect(url_for("home_blueprint.index"))


@blueprint.route("/login", methods=["GET", "POST"])
def login():
    """
    Login page. Checks if the data is correct and
    initiates the session.

    Returns:
        function: redirect to the login page or to the
                  index page if the user is logged in.
    """
    login_form = LoginForm(request.form)
    if "login" in request.form and login_form.validate_on_submit():
        username = request.form["username"]
        password = request.form["password"]
        user = Users.query.filter_by(username=username).first()

        if user and verify_pass(password, user.password):
            login_user(user)
            return redirect(url_for("authentication_blueprint.route_default"))

        return render_template(
            "accounts/login.html",
            msg=get_form_message("incorrect_credentials"),
            form=login_form,
        )

    errors = login_form.errors
    if errors:
        msg = ""
        for key in errors.keys():
            message_id = login_form.errors[key][0]
            msg += "<br />" + get_form_message(message_id)
        return render_template("accounts/login.html", form=login_form, msg=msg)

    if not current_user.is_authenticated:
        return render_template("accounts/login.html", form=login_form)

    flash(get_exception_message("already_logged"), "info")
    return redirect(url_for("home_blueprint.index"))


@blueprint.route("/register", methods=["GET", "POST"])
def register():
    """
    Register page. Checks if the data is correct and
    creates a new user. Flashes messages with information.

    Returns:
        function: redirect to the register page or to the
                    index page if the user is logged in.
    """
    try:
        create_account_form = CreateAccountForm(request.form)
        message = None

        if (
            "register" in request.form
            and create_account_form.validate_on_submit()
        ):
            username = request.form["username"]
            email = request.form["email"]

            if not email_is_valid(email):
                raise KriniException(get_form_message("incorrect_email"))

            user = Users.query.filter_by(username=username).first()
            if user:
                raise KriniException(get_form_message("used_username"))

            user = Users.query.filter_by(email=email).first()
            if user:
                raise KriniException(get_form_message("used_email"))

            user = Users(**request.form)
            db.session.add(user)
            db.session.commit()
            return render_template(
                "accounts/register.html",
                msg=get_form_message("account_created"),
                success=True,
                form=create_account_form,
            )

        errors = create_account_form.errors

        if errors:
            logout_user()
            message = ""
            for key in errors.keys():
                message_id = create_account_form.errors[key][0]
                message += "<br />" + get_form_message(message_id)

        if not current_user.is_authenticated:
            return render_template(
                "accounts/register.html", form=create_account_form, msg=message
            )
        flash(get_exception_message("already_logged"), "info")
        return redirect(url_for("home_blueprint.index"))

    except (KriniException, SQLAlchemyError) as e:
        if e.__class__ == KriniException:
            message = str(e)

        else:
            message = get_form_message("account_not_created")

        return render_template(
            "accounts/register.html",
            msg=message,
            success=False,
            form=create_account_form,
        )


def email_is_valid(email):
    """
    Checks if the email is valid using a simple regex.

    Args:
        email (str): email to validate

    Returns:
        boolean:  True if the email is valid, False otherwise
    """
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    return re.fullmatch(regex, email)


@blueprint.route("/logout")
def logout():
    """
    Logout page. Ends the session.

    Returns:
        function: redirect to the login page.
    """
    logout_user()
    return redirect(url_for("authentication_blueprint.login"))


@login_manager.unauthorized_handler
def unauthorized_handler():
    """
    Unauthorized handler. Redirects to a
    special screen with the login page link.

    Returns:
        function: redirect to the 403 page.
    """
    return render_template("specials/page-403.html"), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    """
    Unauthorized handler. Redirects to a
    special screen with the login page link.

    Args:
        error (class): Error.

    Returns:
        function: redirect to the 403 page.
    """
    return render_template("specials/page-403.html"), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    """
    Page not found handler. Redirects to a
    special screen with the home page link.

    Args:
        error (class): Error.

    Returns:
        function: redirect to the 404 page.
    """
    return render_template("specials/page-404.html"), 404


@blueprint.errorhandler(408)
def timeout_error(error):
    """Handles the 408 error.

    Args:
        error (object): error object

    Returns:
        render_template: renders the template for error 408
    """
    return render_template("specials/page-408.html"), 408


@blueprint.errorhandler(500)
def internal_error(error):
    """
    Internal error handler. Redirects to a
    special screen with the home page link.

    Args:
        error (class): Error.

    Returns:
        function: redirect to the 500 page.
    """
    return render_template("specials/page-500.html"), 500
