from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.usuario_repository import list_usuarios_filtrados


ESTADOS_VALIDOS = {"ACTIVO", "INACTIVO"}


def listar_usuarios_sistema(
    db: Session,
    q: Optional[str] = None,
    rol: Optional[str] = None,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> dict:
    estado_normalizado = estado.strip().upper() if estado else None
    if estado_normalizado and estado_normalizado not in ESTADOS_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado inválido. Use ACTIVO o INACTIVO",
        )

    q_normalizado = q.strip() if q else None
    rol_normalizado = rol.strip() if rol else None

    usuarios, total = list_usuarios_filtrados(
        db=db,
        q=q_normalizado,
        rol=rol_normalizado,
        estado=estado_normalizado,
        skip=skip,
        limit=limit,
    )

    data = [
        {
            "id": usuario.id,
            "documento": usuario.documento,
            "nombre": usuario.nombre,
            "correo": usuario.correo,
            "area": usuario.area,
            "estado": usuario.estado,
            "rol_id": usuario.rol_id,
            "rol": usuario.rol.nombre if usuario.rol else None,
        }
        for usuario in usuarios
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
