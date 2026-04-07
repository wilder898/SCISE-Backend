import logging
from passlib.context import CryptContext

logging.getLogger("passlib").setLevel(logging.ERROR)

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Genera el hash bcrypt de la contraseña en texto plano."""
    return _pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que la contraseña en texto plano coincida con el hash almacenado."""
    return _pwd_context.verify(plain_password, hashed_password)
