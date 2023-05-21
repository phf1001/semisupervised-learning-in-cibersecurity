# -*- encoding: utf-8 -*-
"""
@File    :   config.py
@Time    :   2023/04/28 09:30:21
@Author  :   Patricia Hernando Fernández (modified)
@Version :   2.0
@Contact :   phf1001@alu.ubu.es
@Copy    :  (c) 2019 - present AppSeed.us
"""
from flask_migrate import Migrate
from sys import exit
from decouple import config

from apps.config import config_dict
from apps import create_app, db

DEBUG = config("DEBUG", default=True, cast=bool)
get_config_mode = "Debug" if DEBUG else "Production"

try:
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit("Error: Invalid <config_mode>. Expected values [Debug, Production] ")

app = create_app(app_config)
Migrate(app, db)

if DEBUG:
    app.logger.info("DEBUG       = " + str(DEBUG))
    app.logger.info("Environment = " + get_config_mode)
    app.logger.info("DBMS        = " + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info("LOCALE      = " + app.config["BABEL_DEFAULT_LOCALE"])
    app.logger.info(
        "TRANSLATION = " + app.config["BABEL_TRANSLATION_DIRECTORIES"]
    )

else:
    app.logger.info("Environment = " + get_config_mode)

if __name__ == "__main__":
    app.run()
