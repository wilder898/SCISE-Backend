from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.usuarios import Usuario
from app.schemas.estudiante import EstudianteLookupResponse
from app.schemas.equipo import EquipoAsociadoResponse
from app.controllers import estudiante_controller

router = APIRouter(prefix="/api/v1/estudiantes", tags=["Estudiantes"])


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
