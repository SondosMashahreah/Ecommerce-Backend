"""add rating comments

Revision ID: e6f8a1b2c3d4
Revises: c1a0e3a87a2d
"""

from alembic import op
import sqlalchemy as sa


revision = "e6f8a1b2c3d4"
down_revision = "c1a0e3a87a2d"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("ratings", sa.Column("comment", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("ratings", "comment")
