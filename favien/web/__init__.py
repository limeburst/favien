""":mod:`favien.web` --- Favien web
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from flask import Flask, request
from flask.ext.babel import Babel

from . import admin, canvas, user
from .db import setup_session


babel = Babel()


def create_app(config):
    """The application factory.

    :param config: The instance relative configuration file to use.
    :returns: A Favien Flask app.
    :rtype: :class:`flask.Flask`

    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile(config)
    setup_session(app)
    app.register_blueprint(admin.bp)
    app.register_blueprint(canvas.bp)
    app.register_blueprint(user.bp)
    babel.init_app(app)
    babel.localeselector(get_locale)
    return app


def get_locale():
    """Chooses the most suitable locale."""
    candidates = [str(locale) for locale in babel.list_translations()]
    return request.accept_languages.best_match(candidates)
