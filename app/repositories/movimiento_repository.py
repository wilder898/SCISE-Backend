from sqlalchemy.orm import Session
from app.models.movimientos import Movimiento
from typing import Optional


def create_movimiento(db: Session, movimiento: Movimiento) -> Movimiento:
    db.add(movimiento)
    db.commit()
    db.refresh(movimiento)
    return movimiento


def list_movimientos(db: Session, skip: int = 0, limit: int = 50) -> list[Movimiento]:
    return db.query(Movimiento).order_by(Movimiento.fecha_registro.desc()).offset(skip).limit(limit).all()


def list_movimientos_by_equipo(db: Session, equipo_id: int) -> list[Movimiento]:
    return (
        db.query(Movimiento)
        .filter(Movimiento.equipo_id == equipo_id)
        .order_by(Movimiento.fecha_registro.desc())
        .all()
    )


def list_movimientos_by_estudiante(db: Session, estudiante_id: int) -> list[Movimiento]:
    return (
        db.query(Movimiento)
        .filter(Movimiento.estudiante_id == estudiante_id)
        .order_by(Movimiento.fecha_registro.desc())
        .all()
    )


def get_latest_movimiento_by_equipo_and_tipo(
    db: Session,
    equipo_id: int,
    tipo_movimiento: str,
) -> Optional[Movimiento]:
    return (
        db.query(Movimiento)
        .filter(
            Movimiento.equipo_id == equipo_id,
            Movimiento.tipo_movimiento == tipo_movimiento,
        )
        .order_by(Movimiento.fecha_registro.desc())
        .first()
    )
