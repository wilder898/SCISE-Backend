from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.controllers import equipo_controller
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.usuarios import Usuario
from app.schemas.equipo import EquipoCreate, EquipoResponse

router = APIRouter(prefix="/api/v1/equipos", tags=["Equipos"])


@router.post("", response_model=EquipoResponse, status_code=status.HTTP_201_CREATED)
def crear_equipo(
    datos: EquipoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    return equipo_controller.crear_equipo(db, datos, usuario_actual)
