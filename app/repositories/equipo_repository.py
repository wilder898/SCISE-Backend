from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.equipos import Equipo


def get_equipo_by_id(db: Session, equipo_id: int) -> Optional[Equipo]:
    return db.query(Equipo).filter(Equipo.id == equipo_id).first()


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


def create_equipo(db: Session, equipo: Equipo) -> Equipo:
    db.add(equipo)
    db.commit()
    db.refresh(equipo)
    return equipo


def update_equipo(db: Session, equipo: Equipo) -> Equipo:
    db.commit()
    db.refresh(equipo)
    return equipo
