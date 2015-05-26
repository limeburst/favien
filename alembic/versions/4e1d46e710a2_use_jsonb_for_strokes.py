"""use jsonb for strokes

Revision ID: 4e1d46e710a2
Revises: 5a7ec3d139df
Create Date: 2015-05-25 19:47:45.924915

"""
from alembic.op import execute


# revision identifiers, used by Alembic.
revision = '4e1d46e710a2'
down_revision = '5a7ec3d139df'
branch_labels = None
depends_on = None


def upgrade():
    execute('ALTER TABLE canvases ALTER strokes TYPE JSONB USING strokes::JSONB')


def downgrade():
    execute('ALTER TABLE canvases ALTER strokes TYPE JSON USING strokes::JSON')
