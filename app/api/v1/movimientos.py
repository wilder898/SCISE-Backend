from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.usuarios import Usuario
from app.schemas.movimiento import (
    EquipoActivoResponse,
    MovimientoDetalleResponse,
    MovimientoIngresoBatchRequest,
    MovimientoIngresoBatchResponse,
    PaginatedMovimientoResponse,
    MovimientoSalidaBatchRequest,
    MovimientoSalidaBatchResponse,
)
from app.controllers import movimiento_controller

router = APIRouter(prefix="/api/v1/movimientos", tags=["Movimientos"])


@router.get(
    "",
    response_model=PaginatedMovimientoResponse,
)
def listar_movimientos(
    tipo: str | None = Query(default=None),
    fecha: date | None = Query(default=None),
    estudiante_id: int | None = Query(default=None, gt=0),
    serial: str | None = Query(default=None, max_length=150),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=5, ge=1, le=500),
    db: Session = Depends(get_db),
    _usuario_actual: Usuario = Depends(get_current_user),
):
    return movimiento_controller.listar_movimientos(
        db=db,
        tipo=tipo,
        fecha=fecha,
        estudiante_id=estudiante_id,
        serial=serial,
        skip=skip,
        limit=limit,
    )


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


@router.get(
    "/activos/estudiante/{estudiante_id}",
    response_model=list[EquipoActivoResponse],
)
def listar_equipos_activos_estudiante(
    estudiante_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    return movimiento_controller.listar_equipos_activos_por_estudiante(
        db=db,
        estudiante_id=estudiante_id,
        usuario=usuario_actual,
    )


@router.post(
    "/salidas",
    response_model=MovimientoSalidaBatchResponse,
    status_code=status.HTTP_201_CREATED,
)
def registrar_salidas_batch(
    datos: MovimientoSalidaBatchRequest,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    return movimiento_controller.registrar_salidas_batch(
        db=db,
        estudiante_id=datos.estudiante_id,
        equipos_ids=datos.equipos,
        usuario=usuario_actual,
    )


@router.get(
    "/{movimiento_id}",
    response_model=MovimientoDetalleResponse,
)
def obtener_movimiento_por_id(
    movimiento_id: int,
    db: Session = Depends(get_db),
    _usuario_actual: Usuario = Depends(get_current_user),
):
    return movimiento_controller.obtener_movimiento_por_id(
        db=db,
        movimiento_id=movimiento_id,
    )
