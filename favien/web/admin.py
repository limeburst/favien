""":mod:`favien.web.admin` --- Admin pages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from flask import Blueprint, abort, render_template

from ..user import User
from .db import session
from .user import current_user


bp = Blueprint('admin', __name__, template_folder='templates/admin',
               url_prefix='/admin')


@bp.route('/users/')
def user_list():
    """User list."""
    if not current_user or not current_user.admin:
        abort(401)
    users = session.query(User)
    return render_template('user_list.html', users=users)
