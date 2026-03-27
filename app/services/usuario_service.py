from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.usuarios import Usuario
from app.repositories.rol_repository import get_rol_by_id
from app.repositories.usuario_repository import (
    create_usuario,
    get_usuario_by_correo,
    get_usuario_by_documento,
    list_usuarios_filtrados,
)
from app.schemas.usuario import UsuarioSistemaCreate
from app.utils.password_utils import hash_password


ESTADOS_VALIDOS = {"ACTIVO", "INACTIVO"}


def listar_usuarios_sistema(
    db: Session,
    q: Optional[str] = None,
    rol: Optional[str] = None,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> dict:
    estado_normalizado = estado.strip().upper() if estado else None
    if estado_normalizado and estado_normalizado not in ESTADOS_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado inválido. Use ACTIVO o INACTIVO",
        )

    q_normalizado = q.strip() if q else None
    rol_normalizado = rol.strip() if rol else None

    usuarios, total = list_usuarios_filtrados(
        db=db,
        q=q_normalizado,
        rol=rol_normalizado,
        estado=estado_normalizado,
        skip=skip,
        limit=limit,
    )

    data = [_map_usuario_response(usuario) for usuario in usuarios]

    return {
        "data": data,
        "meta": {
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_next": skip + len(data) < total,
        },
    }


def crear_usuario_sistema(db: Session, datos: UsuarioSistemaCreate) -> dict:
    documento = datos.documento.strip()
    nombre = datos.nombre.strip()
    correo = datos.correo.strip().lower() if datos.correo else None
    area = datos.area.strip() if datos.area else None
    estado = datos.estado.strip().upper()

    if estado not in ESTADOS_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado inválido. Use ACTIVO o INACTIVO",
        )

    if get_usuario_by_documento(db, documento):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese documento",
        )

    if correo and get_usuario_by_correo(db, correo):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese correo",
        )

    rol = get_rol_by_id(db, datos.rol_id)
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rol inválido",
        )

    nuevo_usuario = Usuario(
        documento=documento,
        nombre=nombre,
        correo=correo,
        area=area,
        contrasena=hash_password(datos.contrasena),
        rol_id=datos.rol_id,
        estado=estado,
    )
    usuario_creado = create_usuario(db, nuevo_usuario)
    if not usuario_creado.rol:
        usuario_creado.rol = rol
    return _map_usuario_response(usuario_creado)


def _map_usuario_response(usuario: Usuario) -> dict:
    return {
        "id": usuario.id,
        "documento": usuario.documento,
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "area": usuario.area,
        "estado": usuario.estado,
        "rol_id": usuario.rol_id,
        "rol": usuario.rol.nombre if usuario.rol else None,
    }
