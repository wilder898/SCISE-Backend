from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.controllers import auth_controller
from app.core.deps import oauth2_scheme
from app.db.session import get_db
from app.schemas.auth import AccessTokenResponse, LoginRequest, TokenResponse

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticacion"])


@router.post("/login", response_model=TokenResponse)
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    """Login principal para frontend.
    Recibe JSON: { correo, contrasena }.
    """
    return auth_controller.login(datos, db)


@router.post("/token", response_model=AccessTokenResponse)
def oauth2_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Endpoint OAuth2 compatible con Swagger Authorize.
    Recibe username/password y devuelve access_token/token_type.
    """
    datos = LoginRequest(
        correo=form_data.username,
        contrasena=form_data.password,
    )
    token_data = auth_controller.login(datos, db)
    return {
        "access_token": token_data["access_token"],
        "token_type": token_data["token_type"],
    }


@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Cierre de sesion. Requiere token JWT valido."""
    return auth_controller.logout(token, db)