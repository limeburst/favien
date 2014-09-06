""":mod:`favien.web.user` --- User pages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import requests
from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, session as cookie, url_for)
from werkzeug.urls import url_decode
from werkzeug.local import LocalProxy
from requests_oauthlib import OAuth1

from ..user import User
from .db import session


bp = Blueprint('user', __name__)


def get_user(screen_name):
    """Finds a user by :attr:`~favien.user.User.screen_name`.

    :param screen_name: :attr:`User.screen_name <favien.user.User.screen_name>`
    :type screen_name: :class:`sqlalchemy.types.String`
    :returns: The found user.
    :rtype: :class:`~favien.user.User`

    """
    user = session.query(User).filter_by(screen_name=screen_name).first()
    return user


def get_current_user():
    """Gets the currently signed in user."""
    try:
        user_id = cookie['user_id']
    except KeyError:
        user = None
    else:
        user = session.query(User).get(user_id)
    return user


#: (:class:`~werkzeug.local.LocalProxy` of :class:`~favien.user.User`)
#: The currently signed in user.
current_user = LocalProxy(get_current_user)


@bp.app_context_processor
def inject_current_user():
    """Injects :data:`current_user` to templates."""
    return {'current_user': current_user}


@bp.route('/')
def home():
    """Home."""
    return render_template('home.html')


@bp.route('/login/')
def login():
    """Sign in with Twitter."""
    if current_user:
        abort(403)
    config = current_app.config
    oauth = OAuth1(config['TWITTER_API_KEY'],
                   client_secret=config['TWITTER_API_SECRET'])
    r = requests.post(url=config['TWITTER_REQUEST_TOKEN_URL'], auth=oauth)
    response = url_decode(r.content)
    cookie['twitter_oauth_token'] = response['oauth_token']
    cookie['twitter_oauth_token_secret'] = response['oauth_token_secret']
    authorize_url = '{}?oauth_token={}'.format(config['TWITTER_AUTHORIZE_URL'],
                                               cookie['twitter_oauth_token'])
    return redirect(authorize_url)


@bp.route('/logout/')
def logout():
    """Sign out."""
    cookie.pop('user_id', None)
    flash("You have been logged out")
    return redirect(url_for('.home'))


@bp.route('/oauth/callback')
def callback():
    """Callback from Twitter."""
    resource_owner_key = cookie.pop('twitter_oauth_token')
    resource_owner_secret = cookie.pop('twitter_oauth_token_secret')
    config = current_app.config
    oauth = OAuth1(config['TWITTER_API_KEY'],
                   client_secret=config['TWITTER_API_SECRET'],
                   resource_owner_key=resource_owner_key,
                   resource_owner_secret=resource_owner_secret,
                   verifier=request.args['oauth_verifier'])
    r = requests.post(url=config['TWITTER_ACCESS_TOKEN_URL'], auth=oauth)
    response = url_decode(r.content)
    user = session.query(User) \
        .filter_by(twitter_user_id=response['user_id']).first()
    if not user:
        user = User(twitter_user_id=response['user_id'])
        session.add(user)
    user.twitter_oauth_token = response['oauth_token']
    user.twitter_oauth_token_secret = response['oauth_token_secret']
    user.screen_name = response['screen_name']
    session.commit()
    cookie['user_id'] = user.id
    flash("Logged in as {}".format(user.screen_name))
    return redirect(url_for('.home'))


@bp.route('/<screen_name>/')
def profile(screen_name):
    """Profile page.

    :param screen_name: :attr:`~favien.user.User.screen_name`

    """
    user = get_user(screen_name)
    if not user:
        abort(404)
    return render_template('profile.html', user=user)
