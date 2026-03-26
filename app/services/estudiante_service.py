from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.estudiantes import Estudiante
from app.repositories.estudiante_repository import (
    get_estudiante_activo_by_documento,
    get_estudiante_by_id,
)
from app.repositories.equipo_repository import list_equipos_by_estudiante


def buscar_estudiante_activo_por_documento(db: Session, documento: str) -> Estudiante:
    documento_normalizado = documento.strip()
    if not documento_normalizado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El documento es obligatorio",
        )

    estudiante = get_estudiante_activo_by_documento(db, documento_normalizado)
    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado o inactivo",
        )

    return estudiante


def listar_equipos_asociados_por_estudiante(
    db: Session,
    estudiante_id: int,
    solo_disponibles_ingreso: bool = True,
) -> list[dict]:
    estudiante = get_estudiante_by_id(db, estudiante_id)
    if not estudiante or estudiante.estado != "ACTIVO":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado o inactivo",
        )

    equipos = list_equipos_by_estudiante(
        db,
        estudiante_id=estudiante_id,
        solo_disponibles_ingreso=solo_disponibles_ingreso,
    )

    return [
        {
            "id": equipo.id,
            "nombre": equipo.nombre,
            "serial": equipo.serial,
            "tipo": equipo.tipo_equipo,
            "descripcion": equipo.descripcion,
            "estado": equipo.estado,
        }
        for equipo in equipos
    ]
