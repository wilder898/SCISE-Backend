from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from app.services import auditoria_service


def listar_auditoria(
    db: Session,
    modulo: Optional[str] = None,
    actor_id: Optional[int] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    skip: int = 0,
    limit: int = 20,
) -> dict:
    return auditoria_service.listar_auditoria(
        db=db,
        modulo=modulo,
        actor_id=actor_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        skip=skip,
        limit=limit,
    )
