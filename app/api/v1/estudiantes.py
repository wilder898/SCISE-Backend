from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.usuarios import Usuario
from app.schemas.estudiante import (
    EstudianteCreate,
    EstudianteEstadoUpdate,
    EstudianteLookupResponse,
    EstudianteResponse,
    EstudianteUpdate,
)
from app.schemas.equipo import EquipoAsociadoResponse
from app.controllers import estudiante_controller

router = APIRouter(prefix="/api/v1/estudiantes", tags=["Estudiantes"])


@router.get("", response_model=list[EstudianteResponse])
def listar_estudiantes(
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    return estudiante_controller.listar_estudiantes(skip, limit, db, usuario_actual)


@router.get("/by-documento/{documento}", response_model=EstudianteLookupResponse)
def buscar_estudiante_por_documento(
    documento: str,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    return estudiante_controller.buscar_por_documento(documento, db, usuario_actual)


@router.get("/{estudiante_id}/equipos", response_model=list[EquipoAsociadoResponse])
def listar_equipos_asociados(
    estudiante_id: int,
    solo_disponibles_ingreso: bool = True,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    return estudiante_controller.listar_equipos_asociados(
        estudiante_id=estudiante_id,
        solo_disponibles_ingreso=solo_disponibles_ingreso,
        db=db,
        _usuario_actual=usuario_actual,
    )


@router.post(
    "",
    response_model=EstudianteResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_estudiante(
    datos: EstudianteCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_role("Administrador")),
):
    return estudiante_controller.crear_estudiante(datos, db, usuario_actual)


@router.patch("/{estudiante_id}", response_model=EstudianteResponse)
def actualizar_estudiante(
    estudiante_id: int,
    datos: EstudianteUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    return estudiante_controller.actualizar_estudiante(
        estudiante_id=estudiante_id,
        datos=datos,
        db=db,
        usuario_actual=usuario_actual,
    )


@router.patch("/{estudiante_id}/estado", response_model=EstudianteResponse)
def actualizar_estado_estudiante(
    estudiante_id: int,
    datos: EstudianteEstadoUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_role("Administrador")),
):
    return estudiante_controller.actualizar_estado_estudiante(
        estudiante_id=estudiante_id,
        datos=datos,
        db=db,
        _usuario_actual=usuario_actual,
    )
