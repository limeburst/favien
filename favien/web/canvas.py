""":mod:`favien.web.canvas` --- Canvas pages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import base64

from flask import (Blueprint, abort, jsonify, redirect, render_template,
                   request, url_for)

from ..canvas import Canvas
from ..user import User
from .db import session
from .user import current_user


bp = Blueprint('canvas', __name__, template_folder='templates/canvas')


def get_canvas(screen_name, canvas_id):
    """Finds a canvas by its :attr:~favien.canvas.Canvas.id`.

    :param screen_name: :attr:`Canvas.artist.screen_name
                               <favien.user.User.screen_name>`
    :param canvas_id: :class:`sqlalchemy.types.Integer`
    :return: Found canvas.

    """
    canvas = session.query(Canvas) \
        .filter_by(id=canvas_id) \
        .filter(Canvas.artist.has(User.screen_name == screen_name))
    return canvas.first()


@bp.route('/<screen_name>/', methods=['POST'])
def add(screen_name):
    """Adds a new canvas work."""
    if screen_name != current_user.screen_name:
        abort(401)
    if not current_user:
        return redirect(url_for('user.login'))
    print(request.form)
    canvas = Canvas(artist_id=current_user.id,
                    title=request.form.get('title'),
                    description=request.form.get('description'))
    session.add(canvas)
    session.commit()
    blob = base64.b64decode(request.form['canvas'].split(',')[1])
    canvas.from_blob(blob)
    return jsonify(location=url_for('canvas.view',
                                    screen_name=canvas.artist.screen_name,
                                    canvas_id=canvas.id))


@bp.route('/<screen_name>/<int:canvas_id>/')
def view(screen_name, canvas_id):
    """Displays a canvas work."""
    canvas = get_canvas(screen_name, canvas_id)
    if not canvas:
        abort(404)
    return render_template('canvas/view_canvas.html', canvas=canvas)


@bp.route('/new/')
def new():
    """Draw a new canvas."""
    if not current_user:
        abort(401)
    return render_template('canvas/new_canvas.html')
