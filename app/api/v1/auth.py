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
    usuario = db.query(Usuario).filter(Usuario.correo == datos.correo).first()

    if not usuario or not verify_password(datos.contrasena, usuario.contrasena):
        # ↑ usuario.contrasena, no usuario.contrasena_hash
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    if usuario.estado != "ACTIVO":          # ← STRING, no False
        raise HTTPException(status_code=403, detail="Usuario inactivo")

    jti = str(uuid.uuid4())
    token = create_access_token({
        "user_id": usuario.id,
        "rol": usuario.rol.nombre,
        "jti": jti
    })
    return {
        "access_token": token,
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
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    db.add(TokenBlacklist(jti=payload.get("jti"), usuario_id=payload.get("user_id")))
    db.commit()
    return {"message": "Sesión cerrada exitosamente"}