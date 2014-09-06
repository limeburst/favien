""":mod:`favien.web` --- Favien web
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from flask import Flask

from . import user
from .db import setup_session


def create_app(config):
    """The application factory.

    :param config: The instance relative configuration file to use.
    :returns: A Favien Flask app.
    :rtype: :class:`flask.Flask`

    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile(config)
    setup_session(app)
    app.register_blueprint(user.bp)
    return app
