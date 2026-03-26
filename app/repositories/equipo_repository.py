from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.equipos import Equipo


def get_equipo_by_id(db: Session, equipo_id: int) -> Optional[Equipo]:
    return db.query(Equipo).filter(Equipo.id == equipo_id).first()


def get_equipo_by_id_with_lock(db: Session, equipo_id: int) -> Optional[Equipo]:
    """Obtiene el equipo por ID con bloqueo de fila para operaciones concurrentes."""
    return db.execute(
        select(Equipo)
        .where(Equipo.id == equipo_id)
        .with_for_update()
    ).scalar_one_or_none()


def get_equipo_by_barcode(db: Session, codigo_barras: str) -> Optional[Equipo]:
    return (
        db.query(Equipo)
        .filter(Equipo.codigo_barras_equipo == codigo_barras)
        .first()
    )


def get_equipo_by_barcode_with_lock(db: Session, codigo_barras: str) -> Optional[Equipo]:
    """Obtiene el equipo con bloqueo de fila para operaciones concurrentes."""
    return db.execute(
        select(Equipo)
        .where(Equipo.codigo_barras_equipo == codigo_barras)
        .with_for_update()
    ).scalar_one_or_none()


def list_equipos(db: Session, skip: int = 0, limit: int = 50) -> list[Equipo]:
    return db.query(Equipo).offset(skip).limit(limit).all()


def list_equipos_by_estudiante(
    db: Session,
    estudiante_id: int,
    solo_disponibles_ingreso: bool = True,
) -> list[Equipo]:
    query = db.query(Equipo).filter(Equipo.estudiante_id == estudiante_id)
    if solo_disponibles_ingreso:
        query = query.filter(Equipo.estado != "INGRESADO")

    return query.order_by(Equipo.nombre.asc()).all()


def create_equipo(db: Session, equipo: Equipo) -> Equipo:
    db.add(equipo)
    db.commit()
    db.refresh(equipo)
    return equipo


def update_equipo(db: Session, equipo: Equipo) -> Equipo:
    db.commit()
    db.refresh(equipo)
    return equipo
