from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.usuarios import Usuario
from app.models.token_blacklist import TokenBlacklist
from app.repositories.usuario_repository import get_usuario_by_correo
from app.repositories.token_blacklist_repository import add_to_blacklist, is_token_revoked
from app.utils.password_utils import verify_password
from app.utils.token_utils import build_token_payload, create_access_token, decode_access_token, extract_jti, extract_user_id
from app.schemas.auth import LoginRequest, TokenResponse


def login(datos: LoginRequest, db: Session) -> dict:
    """Lógica de negocio para autenticación de usuario."""
    usuario = get_usuario_by_correo(db, datos.correo)

    if not usuario or not verify_password(datos.contrasena, usuario.contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    if usuario.estado != "ACTIVO":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )

    payload = build_token_payload(usuario.id, usuario.rol.nombre)
    access_token = create_access_token(payload)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "correo": usuario.correo,
            "rol": usuario.rol.nombre,
        },
    }


def logout(token: str, db: Session) -> dict:
    """Lógica de negocio para cerrar sesión: revoca el token."""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    jti = extract_jti(payload)
    usuario_id = extract_user_id(payload)

    if is_token_revoked(db, jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token ya revocado")

    add_to_blacklist(db, jti, usuario_id)
    return {"message": "Sesión cerrada exitosamente"}
