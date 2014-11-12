""":mod:`favien.user` --- Users
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from sqlalchemy.orm import deferred, dynamic_loader, relationship
from sqlalchemy.schema import Column
from sqlalchemy.sql.expression import false
from sqlalchemy.sql.functions import now
from sqlalchemy.types import BigInteger, Boolean, DateTime, Integer, String

from .orm import Base


class User(Base):
    """Favien users."""

    #: (:class:`sqlalchemy.types.Integer`) The primary key integer.
    id = Column(Integer, primary_key=True)

    #: (:class:`sqlalchemy.types.String`) Screen name, used for profile URL.
    screen_name = Column(String, nullable=False, unique=True)

    #: (:class:`sqlalchemy.types.BigInteger`) Twitter user ID.
    twitter_user_id = Column(BigInteger, nullable=False)

    #: (:class:`sqlalchemy.types.String`) Twitter OAuth token.
    twitter_oauth_token = Column(String, nullable=False)

    #: (:class:`sqlalchemy.types.String`) Twitter OAuth token secret.
    twitter_oauth_token_secret = Column(String, nullable=False)

    #: (:class:`sqlalchemy.orm.relationship`) The user's canvases.
    canvases = relationship('Canvas')

    #: (:class:`sqlalchemy.orm.relationship`) Collaborate canvases.
    collaborate_canvases = relationship('Canvas', secondary='collaborations')

    #: (:class:`sqlalchemy.orm.dynamic_loader`) Canvas collaborations.
    collaborations = dynamic_loader('Collaboration', cascade='all, delete-orphan')

    #: (:class:`sqlalchemy.types.Boolean`) Is this user an administrator?
    admin = deferred(
        Column(Boolean, nullable=False, default=False, server_default=false()),
        group='metadata'
    )

    #: (:class:`sqlalchemy.types.DateTime`) The registered time.
    created_at = deferred(
        Column(DateTime(timezone=True), nullable=False, default=now()),
        group='metadata'
    )

    __tablename__ = 'users'
