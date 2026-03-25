from fastapi import Response
from sqlalchemy.orm import Session
from app.services import auth_service
from app.schemas.auth import LoginRequest


def login(datos: LoginRequest, db: Session) -> dict:
    """Coordina la solicitud de login: delega al service y retorna la respuesta."""
    return auth_service.login(datos, db)


def logout(token: str, db: Session) -> dict:
    """Coordina el cierre de sesión: delega al service y retorna la respuesta."""
    return auth_service.logout(token, db)
