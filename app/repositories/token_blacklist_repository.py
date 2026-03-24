from typing import Optional
from sqlalchemy.orm import Session
from app.models.token_blacklist import TokenBlacklist


def is_token_revoked(db: Session, jti: Optional[str]) -> bool:
    """Retorna True si el JTI ya está en la blacklist (token revocado)."""
    if not jti:
        return True
    return db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first() is not None


def add_to_blacklist(db: Session, jti: str, usuario_id: int) -> None:
    """Agrega el JTI a la blacklist y hace commit."""
    entry = TokenBlacklist(jti=jti, usuario_id=usuario_id)
    db.add(entry)
    db.commit()
