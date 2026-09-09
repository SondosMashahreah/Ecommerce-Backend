"""add admin customer message fields

Revision ID: c1a0e3a87a2d
Revises: b4aa53c04626
Create Date: 2026-09-09 19:30:54.629869

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c1a0e3a87a2d"
down_revision: Union[str, Sequence[str], None] = "b4aa53c04626"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    op.add_column(
        "contacts",
        sa.Column(
            "is_read",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "contacts",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "contacts",
        "created_at",
    )

    op.drop_column(
        "contacts",
        "is_read",
    )

    op.drop_column(
        "users",
        "is_active",
    )