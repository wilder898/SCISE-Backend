from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.equipos import Equipo
from app.models.usuarios import Usuario
from app.repositories.estudiante_repository import get_estudiante_by_id
from app.repositories.equipo_repository import create_equipo
from app.repositories.auditoria_repository import create_auditoria
from app.schemas.equipo import EquipoCreate


def crear_equipo(db: Session, datos: EquipoCreate, usuario_actual: Usuario) -> Equipo:
    estudiante = get_estudiante_by_id(db, datos.estudiante_id)
    if not estudiante or estudiante.estado != "ACTIVO":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado o inactivo",
        )

    equipo = Equipo(
        codigo_barras_equipo=datos.codigo_barras_equipo,
        serial=datos.serial.strip(),
        nombre=datos.nombre.strip(),
        descripcion=(datos.descripcion or "").strip() or None,
        tipo_equipo=(datos.tipo_equipo or "").strip() or None,
        estado="DISPONIBLE",
        usuario_registra=usuario_actual.id,
        estudiante_id=datos.estudiante_id,
    )

    try:
        equipo_creado = create_equipo(db, equipo)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No fue posible registrar el equipo. Verifica si el serial ya existe.",
        ) from exc

    create_auditoria(
        db,
        usuario_actual.id,
        "CREAR_EQUIPO",
        "INSERT",
        equipo_creado.id,
        "",
        equipo_creado.serial,
        "/api/v1/equipos",
    )
    db.commit()
    db.refresh(equipo_creado)
    return equipo_creado
