from typing import Optional
from sqlalchemy.orm import Session
from app.services import usuario_service
from app.schemas.usuario import (
    UsuarioSistemaCreate,
    UsuarioSistemaEstadoUpdate,
    UsuarioSistemaPasswordUpdate,
    UsuarioSistemaPatch,
)


def listar_usuarios(
    db: Session,
    q: Optional[str] = None,
    rol: Optional[str] = None,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> dict:
    return usuario_service.listar_usuarios_sistema(
        db=db,
        q=q,
        rol=rol,
        estado=estado,
        skip=skip,
        limit=limit,
    )


def crear_usuario(db: Session, datos: UsuarioSistemaCreate) -> dict:
    return usuario_service.crear_usuario_sistema(db=db, datos=datos)


def actualizar_usuario(db: Session, usuario_id: int, datos: UsuarioSistemaPatch) -> dict:
    return usuario_service.actualizar_usuario_sistema(
        db=db,
        usuario_id=usuario_id,
        datos=datos,
    )


def actualizar_estado_usuario(
    db: Session,
    usuario_id: int,
    datos: UsuarioSistemaEstadoUpdate,
) -> dict:
    return usuario_service.actualizar_estado_usuario_sistema(
        db=db,
        usuario_id=usuario_id,
        datos=datos,
    )


def actualizar_password_usuario(
    db: Session,
    usuario_id: int,
    datos: UsuarioSistemaPasswordUpdate,
) -> dict:
    return usuario_service.actualizar_password_usuario_sistema(
        db=db,
        usuario_id=usuario_id,
        datos=datos,
    )
