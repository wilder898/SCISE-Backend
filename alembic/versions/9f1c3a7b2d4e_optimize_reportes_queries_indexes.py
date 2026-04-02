"""optimize reportes queries indexes

Revision ID: 9f1c3a7b2d4e
Revises: 72c2df07f0e7
Create Date: 2026-03-28 12:05:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "9f1c3a7b2d4e"
down_revision: Union[str, Sequence[str], None] = "72c2df07f0e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Optimizacion para filtros y orden de historico/reportes.
    op.create_index("ix_movimientos_fecha_registro", "movimientos", ["fecha_registro"], unique=False)
    op.create_index(
        "ix_movimientos_tipo_movimiento_fecha_registro",
        "movimientos",
        ["tipo_movimiento", "fecha_registro"],
        unique=False,
    )
    op.create_index(
        "ix_movimientos_estudiante_id_fecha_registro",
        "movimientos",
        ["estudiante_id", "fecha_registro"],
        unique=False,
    )
    op.create_index("ix_equipos_estado", "equipos", ["estado"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_equipos_estado", table_name="equipos")
    op.drop_index("ix_movimientos_estudiante_id_fecha_registro", table_name="movimientos")
    op.drop_index("ix_movimientos_tipo_movimiento_fecha_registro", table_name="movimientos")
    op.drop_index("ix_movimientos_fecha_registro", table_name="movimientos")
