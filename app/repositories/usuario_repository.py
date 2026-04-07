from typing import Optional
from sqlalchemy import or_, func
from sqlalchemy.orm import Session, joinedload
from app.models.roles import Rol
from app.models.usuarios import Usuario


def get_usuario_by_id(db: Session, usuario_id: int) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()


def get_usuario_by_correo(db: Session, correo: str) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.correo == correo).first()


def get_usuario_by_documento(db: Session, documento: str) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.documento == documento).first()


def list_usuarios(db: Session, skip: int = 0, limit: int = 50) -> list[Usuario]:
    return db.query(Usuario).offset(skip).limit(limit).all()


def list_usuarios_filtrados(
    db: Session,
    q: Optional[str] = None,
    rol: Optional[str] = None,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Usuario], int]:
    query = db.query(Usuario).options(joinedload(Usuario.rol))

    if q:
        patron = f"%{q}%"
        query = query.filter(
            or_(
                Usuario.nombre.ilike(patron),
                Usuario.documento.ilike(patron),
                Usuario.correo.ilike(patron),
                Usuario.area.ilike(patron),
            )
        )

    if rol:
        query = query.join(Rol, Usuario.rol_id == Rol.id).filter(func.lower(Rol.nombre) == rol.lower())

    if estado:
        query = query.filter(func.lower(Usuario.estado) == estado.lower())

    total = query.count()
    usuarios = query.order_by(Usuario.nombre.asc()).offset(skip).limit(limit).all()
    return usuarios, total


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
