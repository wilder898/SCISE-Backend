from sqlalchemy.orm import Session
from app.models.usuarios import Usuario
from app.schemas.equipo import EquipoCreate
from app.services import equipo_service


def crear_equipo(db: Session, datos: EquipoCreate, usuario_actual: Usuario):
    return equipo_service.crear_equipo(db, datos, usuario_actual)
