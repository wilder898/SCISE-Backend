from typing import Optional
from sqlalchemy.orm import Session
from app.models.usuarios import Usuario
from app.schemas.equipo import EquipoCreate
from app.services import equipo_service


def listar_equipos(
    db: Session,
    q: Optional[str] = None,
    tipo: Optional[str] = None,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> dict:
    return equipo_service.listar_equipos_sistema(
        db=db,
        q=q,
        tipo=tipo,
        estado=estado,
        skip=skip,
        limit=limit,
    )


def crear_equipo(db: Session, datos: EquipoCreate, usuario_actual: Usuario):
    return equipo_service.crear_equipo(db, datos, usuario_actual)
