from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.usuarios import Usuario
from app.models.token_blacklist import TokenBlacklist
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.security import verify_password, create_access_token, decode_access_token
import uuid

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticación"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/login", response_model=TokenResponse)
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    """Endpoint de inicio de sesión"""
    usuario = db.query(Usuario).filter(Usuario.correo == datos.correo).first()

    if not usuario or not verify_password(datos.contrasena, usuario.contrasena_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    if not usuario.estado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )

    # Generar token con JTI único
    jti = str(uuid.uuid4())
    token_data = {
        "user_id": usuario.id,
        "rol": usuario.rol.nombre,
        "jti": jti
    }
    access_token = create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "correo": usuario.correo,
            "rol": usuario.rol.nombre
        }
    }

@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Endpoint de cierre de sesión"""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")

    # Agregar token a blacklist
    blacklist_entry = TokenBlacklist(
        jti=payload.get("jti"),
        usuario_id=payload.get("user_id")
    )
    db.add(blacklist_entry)
    db.commit()

    return {"message": "Sesión cerrada exitosamente"}