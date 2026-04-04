from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import unicodedata
from app.db.session import get_db
from app.models.usuarios import Usuario
from app.repositories.token_blacklist_repository import is_token_revoked
from app.repositories.usuario_repository import get_usuario_by_id
from app.utils.token_utils import decode_access_token, extract_jti, extract_user_id

# Unica definicion de oauth2_scheme en todo el proyecto
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def _normalize_role(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return text.strip().lower()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """Dependency: obtiene el usuario autenticado desde el JWT.
    Valida firma, expiracion, blacklist y estado del usuario en un solo lugar.
    """
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
        )

    if is_token_revoked(db, extract_jti(payload)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revocado",
        )

    usuario = get_usuario_by_id(db, extract_user_id(payload))
    if not usuario or usuario.estado != "ACTIVO":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario invalido o inactivo",
        )

    return usuario


def require_role(rol_requerido: str):
    """Dependency de orden superior: valida que el usuario tenga un rol especifico."""

    def role_checker(usuario: Usuario = Depends(get_current_user)):
        usuario_role = _normalize_role(usuario.rol.nombre if usuario and usuario.rol else "")
        required_role = _normalize_role(rol_requerido)
        if usuario_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requiere rol: {rol_requerido}",
            )
        return usuario

    return role_checker
