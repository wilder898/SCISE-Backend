from typing import Optional
from sqlalchemy.orm import Session
from app.models.estudiantes import Estudiante


def get_estudiante_by_id(db: Session, estudiante_id: int) -> Optional[Estudiante]:
    return db.query(Estudiante).filter(Estudiante.id == estudiante_id).first()


def get_estudiante_activo_by_barcode(db: Session, codigo_barras: str) -> Optional[Estudiante]:
    return (
        db.query(Estudiante)
        .filter(
            Estudiante.codigo_barras == codigo_barras,
            Estudiante.estado == "ACTIVO",
        )
        .first()
    )


def get_estudiante_activo_by_documento(db: Session, documento: str) -> Optional[Estudiante]:
    return (
        db.query(Estudiante)
        .filter(
            Estudiante.documento == documento,
            Estudiante.estado == "ACTIVO",
        )
        .first()
    )


def list_estudiantes(db: Session, skip: int = 0, limit: int = 50) -> list[Estudiante]:
    return db.query(Estudiante).offset(skip).limit(limit).all()


def create_estudiante(db: Session, estudiante: Estudiante) -> Estudiante:
    db.add(estudiante)
    db.commit()
    db.refresh(estudiante)
    return estudiante


def update_estudiante(db: Session, estudiante: Estudiante) -> Estudiante:
    db.commit()
    db.refresh(estudiante)
    return estudiante
