from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.usuarios import Usuario
from app.schemas.movimiento import (
    MovimientoIngresoBatchRequest,
    MovimientoIngresoBatchResponse,
)
from app.controllers import movimiento_controller

router = APIRouter(prefix="/api/v1/movimientos", tags=["Movimientos"])


@router.post(
    "/ingresos",
    response_model=MovimientoIngresoBatchResponse,
    status_code=status.HTTP_201_CREATED,
)
def registrar_ingresos_batch(
    datos: MovimientoIngresoBatchRequest,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    return movimiento_controller.registrar_ingresos_batch(
        db=db,
        estudiante_id=datos.estudiante_id,
        equipos_ids=datos.equipos,
        usuario=usuario_actual,
    )
