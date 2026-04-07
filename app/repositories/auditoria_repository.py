from typing import Optional
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from app.models.auditoria import Auditoria


def create_auditoria(
    db: Session,
    usuario_id: int,
    evento: str,
    tipo_auditoria: str,
    tabla_id: int,
    valor_anterior: str,
    valor_nuevo: str,
    url: str,
) -> None:
    """Registra una entrada de auditoría. No hace commit — se espera que el llamador lo gestione."""
    db.add(
        Auditoria(
            usuario_id=usuario_id,
            evento=evento,
            tipo_auditoria=tipo_auditoria,
            tabla_id=tabla_id,
            valor_anterior=valor_anterior,
            valor_nuevo=valor_nuevo,
            url=url,
            fecha_novedad=datetime.utcnow(),
        )
    )


def list_auditoria_filtrada(
    db: Session,
    modulo: Optional[str] = None,
    actor_id: Optional[int] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[Auditoria], int]:
    query = db.query(Auditoria).options(joinedload(Auditoria.usuario))

    if modulo:
        patron = f"%{modulo}%"
        query = query.filter(
            or_(
                Auditoria.evento.ilike(patron),
                Auditoria.tipo_auditoria.ilike(patron),
                Auditoria.url.ilike(patron),
            )
        )

    if actor_id:
        query = query.filter(Auditoria.usuario_id == actor_id)

    if fecha_desde:
        query = query.filter(Auditoria.fecha_novedad >= fecha_desde)

    if fecha_hasta:
        query = query.filter(Auditoria.fecha_novedad <= fecha_hasta)

    total = query.count()
    registros = (
        query.order_by(Auditoria.fecha_novedad.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return registros, total
