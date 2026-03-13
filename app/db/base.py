from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Importar TODOS los modelos aquí
from app.models.roles import Rol
from app.models.usuarios import Usuario
from app.models.estudiantes import Estudiante
from app.models.equipos import Equipo
from app.models.movimientos import Movimiento
from app.models.auditoria import Auditoria
from app.models.token_blacklist import TokenBlacklist
