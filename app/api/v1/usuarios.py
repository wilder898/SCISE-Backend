from typing import Optional
from fastapi import APIRouter, Body, Depends, Path, Query, status
from sqlalchemy.orm import Session
from app.controllers import usuario_controller
from app.core.deps import require_role
from app.db.session import get_db
from app.models.usuarios import Usuario
from app.schemas.usuario import (
    MessageResponse,
    PaginatedUsuarioSistemaResponse,
    UsuarioSistemaCreate,
    UsuarioSistemaEstadoUpdate,
    UsuarioSistemaPasswordUpdate,
    UsuarioSistemaPatch,
    UsuarioSistemaResponse,
)

router = APIRouter(prefix="/api/v1/usuarios", tags=["Usuarios"])


@router.get(
    "",
    response_model=PaginatedUsuarioSistemaResponse,
    summary="Listar usuarios del sistema",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permisos (requiere Administrador)"},
    },
)
def listar_usuarios(
    q: Optional[str] = Query(default=None, max_length=150),
    rol: Optional[str] = Query(default=None, max_length=100),
    estado: Optional[str] = Query(default=None, max_length=20),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _usuario_actual: Usuario = Depends(require_role("Administrador")),
):
    return usuario_controller.listar_usuarios(
        db=db,
        q=q,
        rol=rol,
        estado=estado,
        skip=skip,
        limit=limit,
    )


@router.post(
    "",
    response_model=UsuarioSistemaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario del sistema",
    responses={
        400: {"description": "Datos inválidos"},
        401: {"description": "No autenticado"},
        403: {"description": "Sin permisos (requiere Administrador)"},
        409: {"description": "Documento o correo duplicado"},
    },
)
def crear_usuario(
    datos: UsuarioSistemaCreate,
    db: Session = Depends(get_db),
    _usuario_actual: Usuario = Depends(require_role("Administrador")),
):
    return usuario_controller.crear_usuario(db=db, datos=datos)


@router.patch(
    "/{usuario_id}",
    response_model=UsuarioSistemaResponse,
    summary="Actualizar usuario del sistema",
    responses={
        400: {"description": "Datos inválidos"},
        401: {"description": "No autenticado"},
        403: {"description": "Sin permisos (requiere Administrador)"},
        404: {"description": "Usuario no encontrado"},
        409: {"description": "Documento o correo duplicado"},
    },
)
def actualizar_usuario(
    usuario_id: int = Path(..., gt=0),
    datos: UsuarioSistemaPatch = Body(...),
    db: Session = Depends(get_db),
    _usuario_actual: Usuario = Depends(require_role("Administrador")),
):
    return usuario_controller.actualizar_usuario(
        db=db,
        usuario_id=usuario_id,
        datos=datos,
    )


@router.patch(
    "/{usuario_id}/estado",
    response_model=UsuarioSistemaResponse,
    summary="Actualizar estado del usuario del sistema",
    responses={
        400: {"description": "Estado inválido"},
        401: {"description": "No autenticado"},
        403: {"description": "Sin permisos (requiere Administrador)"},
        404: {"description": "Usuario no encontrado"},
    },
)
def actualizar_estado_usuario(
    usuario_id: int = Path(..., gt=0),
    datos: UsuarioSistemaEstadoUpdate = Body(...),
    db: Session = Depends(get_db),
    _usuario_actual: Usuario = Depends(require_role("Administrador")),
):
    return usuario_controller.actualizar_estado_usuario(
        db=db,
        usuario_id=usuario_id,
        datos=datos,
    )


@router.patch(
    "/{usuario_id}/password",
    response_model=MessageResponse,
    summary="Actualizar contraseña del usuario del sistema",
    responses={
        400: {"description": "Datos inválidos"},
        401: {"description": "No autenticado"},
        403: {"description": "Sin permisos (requiere Administrador)"},
        404: {"description": "Usuario no encontrado"},
    },
)
def actualizar_password_usuario(
    usuario_id: int = Path(..., gt=0),
    datos: UsuarioSistemaPasswordUpdate = Body(...),
    db: Session = Depends(get_db),
    _usuario_actual: Usuario = Depends(require_role("Administrador")),
):
    return usuario_controller.actualizar_password_usuario(
        db=db,
        usuario_id=usuario_id,
        datos=datos,
    )
