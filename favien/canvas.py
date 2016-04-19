""":mod:`favien.canvas` --- Canvas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import boto3
from botocore.client import Config
from flask import current_app
from sqlalchemy.orm import deferred, dynamic_loader, relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.functions import now
from sqlalchemy.types import Boolean, DateTime, Integer, UnicodeText
from sqlalchemy.dialects.postgres import JSONB

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

    #: (:class:`sqlalchemy.orm.relationship`) Canvas collaborators.
    collaborators = relationship(User, secondary='collaborations')

    #: (:class:`sqlalchemy.orm.dynamic_loader`) Canvas collaborations.
    collaborations = dynamic_loader('Collaboration', cascade='all, delete-orphan')

    #: (:class:`sqlalchemy.types.String`) Canvas title.
    title = Column(UnicodeText)

    #: (:class:`sqlalchemy.types.UnicodeText`) The description of the canvas.
    description = Column(UnicodeText)

    #: (:class:`sqlalchemy.dialects.postgres.JSON`) Canvas brush strokes.
    strokes = deferred(Column(JSONB))

    #: (:class:`sqlalchemy.types.Integer`) Canvas width in pixels.
    width = Column(Integer, nullable=False)

    #: (:class:`sqlalchemy.types.Integer`) Canvas height in pixels.
    height = Column(Integer, nullable=False)

    #: (:class:`sqlalchemy.types.Boolean`) Is this canvas broadcasting?
    broadcast = Column(Boolean, nullable=False)

    #: (:class:`sqlalchemy.types.Boolean`) Is replaying allowed?
    replay = Column(Boolean, nullable=False)

    #: (:class:`sqlalchemy.types.DateTime`) The created time.
    created_at = deferred(
        Column(DateTime(timezone=True), nullable=False, default=now()),
        group='metadata'
    )

    __tablename__ = 'canvases'

    @property
    def key(self):
        return '{}/{}'.format(self.__tablename__, self.id)

    def from_blob(self, blob):
        s3 = boto3.resource('s3')
        o = s3.Object(current_app.config['AWS_S3_BUCKET'], self.key)
        return o.put(Body=blob)

    def get_url(self):
        s3 = boto3.client('s3', config=Config(signature_version='s3v4'))
        return s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': current_app.config['AWS_S3_BUCKET'],
                'Key': self.key,
            },
        )


class Collaboration(Base):
    """:class:`User`\ s collaborate on :class:`Canvas`\ s."""

    #: (:class:`sqlalchemy.types.Integer`) :attr:`~Canvas.id` of :attr:`canvas`.
    canvas_id = Column(Integer, ForeignKey(Canvas.id), primary_key=True)

    #: (:class:`sqlalchemy.types.Integer`) :attr:`~User.id` of :attr:`artist`.
    artist_id = Column(Integer, ForeignKey(User.id), primary_key=True)

    #: (:class:`sqlalchemy.orm.relationship`) Canvas the user is collaborating on.
    canvas = relationship(Canvas)

    #: (:class:`sqlalchemy.orm.relationship`) Collaborating artist.
    artist = relationship(User)

    #: (:class:`sqlalchemy.types.DateTime`) The created time.
    created_at = Column(DateTime(timezone=True), nullable=False, default=now())

    __tablename__ = 'collaborations'
