from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.controllers import auditoria_controller
from app.core.deps import require_role
from app.db.session import get_db
from app.models.usuarios import Usuario
from app.schemas.auditoria import PaginatedAuditoriaResponse

router = APIRouter(prefix="/api/v1/auditoria", tags=["Auditoria"])


@router.get(
    "",
    response_model=PaginatedAuditoriaResponse,
    summary="Listar eventos de auditoría",
    responses={
        400: {"description": "Rango de fechas inválido"},
        401: {"description": "No autenticado"},
        403: {"description": "Sin permisos (requiere Administrador)"},
    },
)
def listar_auditoria(
    modulo: Optional[str] = Query(default=None, max_length=150),
    actor_id: Optional[int] = Query(default=None, gt=0),
    fecha_desde: Optional[date] = Query(default=None),
    fecha_hasta: Optional[date] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _usuario_actual: Usuario = Depends(require_role("Administrador")),
):
    return auditoria_controller.listar_auditoria(
        db=db,
        modulo=modulo,
        actor_id=actor_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        skip=skip,
        limit=limit,
    )
