"""initial

Revision ID: 5a7ec3d139df
Revises: None
Create Date: 2015-03-25 18:28:48.013157

"""
from alembic.op import create_table, drop_table
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.expression import false
from sqlalchemy.types import BigInteger, Boolean, DateTime, Integer, String, UnicodeText


# revision identifiers, used by Alembic.
revision = '5a7ec3d139df'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    create_table('users',
        Column('id', Integer, primary_key=True),
        Column('screen_name', String, nullable=False, unique=True),
        Column('twitter_user_id', BigInteger, nullable=False),
        Column('twitter_oauth_token', String, nullable=False),
        Column('twitter_oauth_token_secret', String, nullable=False),
        Column('admin', Boolean, server_default=false(), nullable=False),
        Column('created_at', DateTime(timezone=True), nullable=False),
    )
    create_table('canvases',
        Column('id', Integer, primary_key=True),
        Column('artist_id', Integer, ForeignKey('users.id'), nullable=False),
        Column('title', UnicodeText),
        Column('description', UnicodeText),
        Column('strokes', JSON),
        Column('width', Integer, nullable=False),
        Column('height', Integer, nullable=False),
        Column('broadcast', Boolean, nullable=False),
        Column('replay', Boolean, nullable=False),
        Column('created_at', DateTime(timezone=True), nullable=False),
    )
    create_table('collaborations',
        Column('canvas_id', Integer, ForeignKey('canvases.id'), primary_key=True),
        Column('artist_id', Integer, ForeignKey('users.id'), primary_key=True),
        Column('created_at', DateTime(timezone=True), nullable=False),
    )


def downgrade():
    drop_table('collaborations')
    drop_table('canvases')
    drop_table('users')
