"""add fecha_registro to estudiantes

Revision ID: c48346534739
Revises: b7a1c2d3e4f5
Create Date: 2026-04-04 23:16:19.391187

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c48346534739'
down_revision: Union[str, Sequence[str], None] = 'b7a1c2d3e4f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "estudiantes",
        sa.Column(
            "fecha_registro",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("estudiantes", "fecha_registro")
