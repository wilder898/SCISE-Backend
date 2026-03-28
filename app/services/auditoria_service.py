from datetime import date, datetime, time
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.auditoria_repository import list_auditoria_filtrada


def listar_auditoria(
    db: Session,
    modulo: Optional[str] = None,
    actor_id: Optional[int] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    skip: int = 0,
    limit: int = 20,
) -> dict:
    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="fecha_desde no puede ser mayor que fecha_hasta",
        )

    modulo_normalizado = modulo.strip() if modulo else None
    fecha_desde_dt = (
        datetime.combine(fecha_desde, time.min) if fecha_desde else None
    )
    fecha_hasta_dt = (
        datetime.combine(fecha_hasta, time.max) if fecha_hasta else None
    )

    registros, total = list_auditoria_filtrada(
        db=db,
        modulo=modulo_normalizado,
        actor_id=actor_id,
        fecha_desde=fecha_desde_dt,
        fecha_hasta=fecha_hasta_dt,
        skip=skip,
        limit=limit,
    )

    data = [
        {
            "id": registro.id,
            "usuario_id": registro.usuario_id,
            "actor_nombre": registro.usuario.nombre if registro.usuario else None,
            "evento": registro.evento,
            "tipo_auditoria": registro.tipo_auditoria,
            "tabla_id": registro.tabla_id,
            "valor_anterior": registro.valor_anterior,
            "valor_nuevo": registro.valor_nuevo,
            "url": registro.url,
            "fecha_novedad": registro.fecha_novedad,
        }
        for registro in registros
    ]

    return {
        "data": data,
        "meta": {
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_next": skip + len(data) < total,
        },
    }
