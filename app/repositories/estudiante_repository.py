from typing import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.estudiantes import Estudiante


def get_estudiante_by_id(db: Session, estudiante_id: int) -> Optional[Estudiante]:
    return db.query(Estudiante).filter(Estudiante.id == estudiante_id).first()


def get_estudiante_by_documento(db: Session, documento: str) -> Optional[Estudiante]:
    return db.query(Estudiante).filter(Estudiante.documento == documento).first()


def get_estudiante_by_codigo_barras(db: Session, codigo_barras: str) -> Optional[Estudiante]:
    return db.query(Estudiante).filter(Estudiante.codigo_barras == codigo_barras).first()


def get_estudiante_by_email(db: Session, email: str) -> Optional[Estudiante]:
    return db.query(Estudiante).filter(Estudiante.email == email).first()


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


def get_estudiante_activo_by_documento_o_codigo_barras(
    db: Session,
    identificador: str,
) -> Optional[Estudiante]:
    return (
        db.query(Estudiante)
        .filter(
            Estudiante.estado == "ACTIVO",
            or_(
                Estudiante.documento == identificador,
                Estudiante.codigo_barras == identificador,
            ),
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
