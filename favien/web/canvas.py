""":mod:`favien.web.canvas` --- Canvas pages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from __future__ import absolute_import

import base64

from flask import (Blueprint, Response, abort, json, jsonify, redirect,
                   render_template, request, url_for, stream_with_context)
from redis import ConnectionError

from ..canvas import Canvas
from ..user import User
from .db import session
from .redis import redis
from .user import current_user, get_user


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
    canvas = Canvas(artist=current_user._get_current_object(),
                    title=request.form.get('title'),
                    description=request.form.get('description'),
                    width=request.form.get('width'),
                    height=request.form.get('height'),
                    strokes=json.loads(request.form.get('strokes')))
    broadcast = request.form.get('broadcast', False)
    replay = request.form.get('replay', False)
    if broadcast == 'true':
        canvas.broadcast = True
    else:
        canvas.broadcast = False
    if replay == 'replay':
        canvas.replay = True
    else:
        canvas.replay = False
    session.add(canvas)
    session.commit()
    blob = base64.b64decode(request.form['canvas'].split(',')[1])
    canvas.from_blob(blob)
    return jsonify(location=url_for('canvas.view',
                                    screen_name=canvas.artist.screen_name,
                                    canvas_id=canvas.id))


@bp.route('/<screen_name>/<int:canvas_id>/', methods=['POST', 'PUT'])
def edit(screen_name, canvas_id):
    """Edits a canvas."""
    canvas = get_canvas(screen_name, canvas_id)
    if not canvas:
        abort(404)
    if canvas.artist != current_user:
        abort(400)
    canvas.title = request.form.get('title')
    canvas.description = request.form.get('description')
    broadcast = request.form.get('broadcast', False)
    replay = request.form.get('replay', False)
    if broadcast == 'true':
        canvas.broadcast = True
    else:
        canvas.broadcast = False
    if replay == 'replay':
        canvas.replay = True
    else:
        canvas.replay = False
    canvas_data = request.form.get('canvas', False)
    if canvas_data:
        canvas.from_blob(base64.b64decode(canvas_data.split(',')[1]))
    session.add(canvas)
    session.commit()
    if not canvas.broadcast:
        try:
            redis.publish(canvas.id, json.dumps({'event': 'terminate'}))
        except ConnectionError:
            pass  # FIXME
    loc = url_for('canvas.view', screen_name=screen_name, canvas_id=canvas_id)
    if request.method == 'PUT':
        return jsonify(location=loc)
    elif request.method == 'POST':
        return redirect(loc)


@bp.route('/<screen_name>/<int:canvas_id>/edit/')
def edit_form(screen_name, canvas_id):
    """Canvas edit page."""
    canvas = get_canvas(screen_name, canvas_id)
    if not canvas:
        abort(404)
    if canvas.artist != current_user:
        abort(400)
    return render_template('canvas/edit_canvas.html', canvas=canvas)


@bp.route('/<screen_name>/<int:canvas_id>/delete/')
def delete(screen_name, canvas_id):
    """Deletes a canvas."""
    canvas = get_canvas(screen_name, canvas_id)
    if not canvas:
        abort(404)
    if canvas.artist != current_user:
        abort(400)
    canvas.key.delete()
    session.delete(canvas)
    session.commit()
    return redirect(url_for('user.profile',
                            screen_name=canvas.artist.screen_name))


@bp.route('/<screen_name>/<int:canvas_id>/')
def view(screen_name, canvas_id):
    """Displays a canvas work."""
    canvas = get_canvas(screen_name, canvas_id)
    if not canvas:
        abort(404)
    return render_template('canvas/view_canvas.html', canvas=canvas)


@bp.route('/<screen_name>/<int:canvas_id>/strokes/')
def strokes(screen_name, canvas_id):
    """Canvas strokes for replaying."""
    canvas = get_canvas(screen_name, canvas_id)
    if not canvas:
        abort(404)
    if not canvas.replay:
        abort(403)
    return jsonify(strokes=canvas.strokes)


@bp.route('/<screen_name>/<int:canvas_id>/strokes/', methods=['POST'])
def append_strokes(screen_name, canvas_id):
    """Append and publish strokes."""
    canvas = get_canvas(screen_name, canvas_id)
    if not canvas:
        abort(404)
    if canvas.artist != current_user and \
       current_user not in canvas.collaborators:
        abort(401)
    if not canvas.broadcast:
        abort(403)
    strokes = json.loads(request.form.get('strokes'))
    try:
        redis.publish(canvas.id, json.dumps({
            'event': 'strokes',
            'user': current_user.screen_name,
            'strokes': strokes
        }))
    except ConnectionError:
        pass  # FIXME
    canvas.strokes = canvas.strokes + strokes
    session.add(canvas)
    session.commit()
    return jsonify()


@bp.route('/<screen_name>/<int:canvas_id>/stream/')
def stroke_stream(screen_name, canvas_id):
    """Server-sent events stream endpoint."""
    canvas = get_canvas(screen_name, canvas_id)
    if not canvas:
        abort(404)
    if not canvas.broadcast:
        abort(405)
    return Response(stream_with_context(generate(canvas)),
                    direct_passthrough=True,
                    mimetype='text/event-stream')


@bp.route('/<screen_name>/<int:canvas_id>/collaborators/', methods=['POST'])
def add_collaborator(screen_name, canvas_id):
    canvas = get_canvas(screen_name, canvas_id)
    if not canvas:
        abort(404)
    if canvas.artist != current_user:
        abort(403)
    screen_name = request.form.get('collaborator')
    if not screen_name:
        abort(400)
    collaborator = get_user(screen_name)
    if not collaborator:
        abort(404)
    canvas.collaborators.append(collaborator)
    session.add(canvas)
    session.commit()
    redis.publish(canvas.id, json.dumps({
        'event': 'add-collaborator',
        'collaborator': request.form['collaborator']
    }))
    return jsonify()


@bp.route('/<screen_name>/<int:canvas_id>/stream/', methods=['POST'])
def stream_publish(screen_name, canvas_id):
    """Stream endpoint for publishing events."""
    canvas = get_canvas(screen_name, canvas_id)
    if not canvas:
        abort(404)
    if not canvas.broadcast:
        abort(405)
    redis.publish(canvas.id, json.dumps({
        'event': request.form['event'],
        'screen_name': current_user.screen_name
    }))
    return jsonify()


def generate(canvas):
    """Canvas stream generator."""
    pubsub = redis.pubsub()
    pubsub.subscribe(canvas.id)
    for event in pubsub.listen():
        if event['type'] == 'message':
            data = json.loads(event['data'])
            if data['event'] == 'terminate':
                return
            if data['event'] == 'add-collaborator':
                if current_user.screen_name == data['collaborator']:
                    data['event'] = 'collaboration-request-accepted'
            yield 'event: {}\r\ndata: {}\r\n\r\n'.format(data['event'],
                                                         event['data'])


@bp.route('/new/')
def new():
    """Draw a new canvas."""
    return render_template('canvas/new_canvas.html')
