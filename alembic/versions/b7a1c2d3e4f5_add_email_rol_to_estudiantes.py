"""add email and rol to estudiantes

Revision ID: b7a1c2d3e4f5
Revises: 9f1c3a7b2d4e
Create Date: 2026-04-01 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b7a1c2d3e4f5"
down_revision: Union[str, Sequence[str], None] = "9f1c3a7b2d4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("estudiantes", sa.Column("email", sa.String(length=150), nullable=True))
    op.add_column(
        "estudiantes",
        sa.Column(
            "rol",
            sa.String(length=50),
            nullable=False,
            server_default="Aprendiz",
        ),
    )
    op.create_unique_constraint("uq_estudiantes_email", "estudiantes", ["email"])
    op.alter_column("estudiantes", "rol", server_default=None)


def downgrade() -> None:
    op.drop_constraint("uq_estudiantes_email", "estudiantes", type_="unique")
    op.drop_column("estudiantes", "rol")
    op.drop_column("estudiantes", "email")
