""":mod:`favien.user` --- Users
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from sqlalchemy.orm import deferred
from sqlalchemy.schema import Column
from sqlalchemy.sql.functions import now
from sqlalchemy.types import BigInteger, DateTime, Integer, String

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

    #: (:class:`sqlalchemy.types.DateTime`) The registered time.
    created_at = deferred(
        Column(DateTime(timezone=True), nullable=False, default=now()),
        group='metadata'
    )

    __tablename__ = 'users'
