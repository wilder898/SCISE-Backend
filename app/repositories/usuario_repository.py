from typing import Optional
from sqlalchemy.orm import Session
from app.models.usuarios import Usuario


def get_usuario_by_id(db: Session, usuario_id: int) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()


def get_usuario_by_correo(db: Session, correo: str) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.correo == correo).first()


def get_usuario_by_documento(db: Session, documento: str) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.documento == documento).first()


def list_usuarios(db: Session, skip: int = 0, limit: int = 50) -> list[Usuario]:
    return db.query(Usuario).offset(skip).limit(limit).all()


def create_usuario(db: Session, usuario: Usuario) -> Usuario:
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def update_usuario(db: Session, usuario: Usuario) -> Usuario:
    db.commit()
    db.refresh(usuario)
    return usuario


def delete_usuario(db: Session, usuario: Usuario) -> None:
    db.delete(usuario)
    db.commit()
