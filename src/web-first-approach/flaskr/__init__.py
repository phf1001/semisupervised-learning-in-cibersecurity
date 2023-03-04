import os
from flask import Flask
from . import db
from . import auth
from . import scanner
from . import general_results
from . import report_url
def create_app(test_config=None):
    """
    Create and configure an instance of
    the Flask application.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    app.register_blueprint(auth.bp)

    app.register_blueprint(scanner.bp)
    app.add_url_rule('/', endpoint='index')

    app.register_blueprint(general_results.bp)
    app.register_blueprint(report_url.bp)
    return app
