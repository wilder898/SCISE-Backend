from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.controllers import equipo_controller
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.usuarios import Usuario
from app.schemas.equipo import (
    EquipoCreate,
    EquipoResponse,
    EquipoUpdate,
    PaginatedEquipoSistemaResponse,
)

router = APIRouter(prefix="/api/v1/equipos", tags=["Equipos"])


@router.get(
    "",
    response_model=PaginatedEquipoSistemaResponse,
    summary="Listar equipos registrados",
    responses={
        401: {"description": "No autenticado"},
        400: {"description": "Filtros inválidos"},
    },
)
def listar_equipos(
    q: Optional[str] = Query(default=None, max_length=150),
    tipo: Optional[str] = Query(default=None, max_length=100),
    estado: Optional[str] = Query(default=None, max_length=20),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _usuario_actual: Usuario = Depends(get_current_user),
):
    return equipo_controller.listar_equipos(
        db=db,
        q=q,
        tipo=tipo,
        estado=estado,
        skip=skip,
        limit=limit,
    )


@router.post("", response_model=EquipoResponse, status_code=status.HTTP_201_CREATED)
def crear_equipo(
    datos: EquipoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    return equipo_controller.crear_equipo(db, datos, usuario_actual)


@router.patch("/{equipo_id}", response_model=EquipoResponse)
def actualizar_equipo(
    equipo_id: int,
    datos: EquipoUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    return equipo_controller.actualizar_equipo(
        db=db,
        equipo_id=equipo_id,
        datos=datos,
        usuario_actual=usuario_actual,
    )


@router.delete("/{equipo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_equipo(
    equipo_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    equipo_controller.eliminar_equipo(
        db=db,
        equipo_id=equipo_id,
        usuario_actual=usuario_actual,
    )
