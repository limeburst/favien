""":mod:`favien.canvas` --- Canvas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from flask import current_app
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.functions import now
from sqlalchemy.types import Boolean, DateTime, Integer, UnicodeText
from sqlalchemy.dialects.postgres import JSON

from .orm import Base
from .user import User


class Canvas(Base):
    """The canvas work."""

    #: (:class:`sqlalchemy.types.Integer`) The primary key integer.
    id = Column(Integer, primary_key=True)

    #: (:class:`sqlalchemy.types.Integer`) Canvas artist.
    artist_id = Column(Integer, ForeignKey(User.id), nullable=False)

    #: (:class:`sqlalchemy.orm.relationship`) Canvas artist.
    artist = relationship(User)

    #: (:class:`sqlalchemy.types.String`) Canvas title.
    title = Column(UnicodeText)

    #: (:class:`sqlalchemy.types.UnicodeText`) The description of the canvas.
    description = Column(UnicodeText)

    #: (:class:`sqlalchemy.dialects.postgres.JSON`) Canvas brush strokes.
    strokes = deferred(Column(JSON))

    #: (:class:`sqlalchemy.types.Boolean`) Is replaying allowed?
    replay_allowed = Column(Boolean, nullable=False, default=False)

    #: (:class:`sqlalchemy.types.DateTime`) The created time.
    created_at = deferred(
        Column(DateTime(timezone=True), nullable=False, default=now()),
        group='metadata'
    )

    __tablename__ = 'canvases'

    @property
    def key(self):
        config = current_app.config
        c = S3Connection(config['AWS_ACCESS_KEY_ID'], config['AWS_SECRET_KEY'])
        b = c.get_bucket(config['AWS_S3_BUCKET'], validate=False)
        k = Key(b)
        k.key = '{}/{}'.format(self.__tablename__, self.id)
        return k

    def from_blob(self, blob):
        self.key.set_contents_from_string(blob)

    def get_url(self, expires_in=300):
        return self.key.generate_url(expires_in)
