from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import oauth2_scheme
from app.schemas.auth import LoginRequest, TokenResponse
from app.controllers import auth_controller

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse)
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    """Endpoint de inicio de sesión. Body validado por Pydantic antes de llegar aquí."""
    return auth_controller.login(datos, db)


@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Endpoint de cierre de sesión. Requiere token JWT válido."""
    return auth_controller.logout(token, db)