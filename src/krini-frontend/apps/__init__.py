# -*- encoding: utf-8 -*-
"""Copyright (c) 2019 - present AppSeed.us"""

from flask import Flask
from flask_babel import Babel
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module

db = SQLAlchemy()
login_manager = LoginManager()
babel = Babel()


def get_locale():
    return "en"


def create_app(config):
    """
    Create and configure an instance of
    the Flask application.
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
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    for module_name in ("authentication", "home"):
        module = import_module("apps.{}.routes".format(module_name))
        app.register_blueprint(module.blueprint)


def configure_database(app):
    @app.before_first_request
    def initialize_database():
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()
