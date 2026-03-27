from typing import Optional
from sqlalchemy.orm import Session
from app.services import usuario_service


def listar_usuarios(
    db: Session,
    q: Optional[str] = None,
    rol: Optional[str] = None,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> dict:
    return usuario_service.listar_usuarios_sistema(
        db=db,
        q=q,
        rol=rol,
        estado=estado,
        skip=skip,
        limit=limit,
    )
