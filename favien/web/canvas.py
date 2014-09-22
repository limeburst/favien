""":mod:`favien.web.canvas` --- Canvas pages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from flask import Blueprint, abort, render_template

from .user import current_user


bp = Blueprint('canvas', __name__)


@bp.route('/new/')
def new():
    """Draw a new canvas."""
    if not current_user:
        abort(401)
    return render_template('canvas.html')
