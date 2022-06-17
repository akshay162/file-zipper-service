# project/server/__init__.py


import os

from flask import Flask
from flask_bootstrap import Bootstrap4


# register blueprints
from project.server.app.controller.archive_controller import main_blueprint
from project.server.app.util.error_handler import error_blueprint


def create_app(script_info=None):

    # instantiate the app
    app = Flask(__name__)

    # set config
    app_settings = os.getenv("APP_SETTINGS")
    app.config.from_object(app_settings)

    # set up extensions
    Bootstrap4(app)

    app.register_blueprint(main_blueprint)
    app.register_blueprint(error_blueprint)

    # shell context for flask cli
    app.shell_context_processor({"app": app})

    return app
