from datetime import datetime, timedelta
from typing import Optional
import uuid
from jose import jwt, JWTError
from app.core.config import settings


def build_token_payload(user_id: int, rol: str) -> dict:
    """Construye el payload estándar del token con JTI único."""
    return {
        "user_id": user_id,
        "rol": rol,
        "jti": str(uuid.uuid4()),
    }


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Codifica y firma el JWT con expiración."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> Optional[dict]:
    """Decodifica el JWT. Retorna None si el token es inválido o expirado."""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None


def extract_jti(payload: dict) -> Optional[str]:
    """Extrae el JTI (JWT ID) del payload decodificado."""
    return payload.get("jti")


def extract_user_id(payload: dict) -> Optional[int]:
    """Extrae el user_id del payload decodificado."""
    return payload.get("user_id")


def extract_rol(payload: dict) -> Optional[str]:
    """Extrae el rol del payload decodificado."""
    return payload.get("rol")
