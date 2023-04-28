# -*- encoding: utf-8 -*-
"""
@File    :   config.py
@Time    :   2023/04/28 09:24:58
@Author  :   Patricia Hernando Fernández (modified)
@Version :   2.0
@Contact :   phf1001@alu.ubu.es
@Copy    :  (c) 2019 - present AppSeed.us
"""
from flask import Flask, session, request
from flask_babel import Babel
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module
from apps.config import BABEL_DEFAULT

db = SQLAlchemy()
login_manager = LoginManager()
babel = Babel()


def get_locale():
    """Get locale.

    Returns:
        str: Locale.
    """
    if request.args.get("language"):
        session["language"] = request.args.get("language")
    return session.get("language", BABEL_DEFAULT)


def create_app(config):
    """Create app.

    Args:
        config (object): configuration object.

    Returns:
        object: Flask object.
    """
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    CSRFProtect(app).init_app(app)
    babel.init_app(app, locale_selector=get_locale)
    return app


def register_extensions(app):
    """
    Register extensions with the Flask application.

    Args:
        app (object): Flask object.
    """
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    """
    Register blueprints with the Flask application.

    Args:
        app (object): Flask object.
    """
    for module_name in ("authentication", "home"):
        module = import_module("apps.{}.routes".format(module_name))
        app.register_blueprint(module.blueprint)


def configure_database(app):
    """
    Configures the database with the Flask application.

    Args:
        app (object): Flask object.
    """

    @app.before_first_request
    def initialize_database():
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        """
        Shutdown session.

        Args:
            exception (object, optional): Exception object. Defaults to None.
        """
        db.session.remove()
