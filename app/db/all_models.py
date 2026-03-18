# Este archivo registra todos los modelos con SQLAlchemy.
# Impórtalo en main.py y en alembic/env.py para asegurar
# que todos los mappers estén disponibles antes de usarlos.

from app.models.roles           import Rol            # noqa: F401
from app.models.usuarios        import Usuario        # noqa: F401
from app.models.estudiantes     import Estudiante     # noqa: F401
from app.models.equipos         import Equipo         # noqa: F401
from app.models.movimientos     import Movimiento     # noqa: F401
from app.models.auditoria       import Auditoria      # noqa: F401
from app.models.token_blacklist import TokenBlacklist  # noqa: F401
