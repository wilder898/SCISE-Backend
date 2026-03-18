from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.usuarios import Usuario
from app.models.token_blacklist import TokenBlacklist
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    """Obtiene usuario actual desde token JWT"""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")

    # Verificar que token no esté revocado
    jti = payload.get("jti")
    revocado = db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first()
    if revocado:
        raise HTTPException(status_code=401, detail="Token revocado")

    user_id = payload.get("user_id")
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()

    if not usuario or usuario.estado != "ACTIVO":
        raise HTTPException(status_code=401, detail="Usuario inválido")

    return usuario

def require_role(rol_requerido: str):
    """Dependencia de orden superior para validar rol"""
    def role_checker(usuario: Usuario = Depends(get_current_user)):
        if usuario.rol.nombre != rol_requerido:
            raise HTTPException(
                status_code=403,
                detail=f"Requiere rol: {rol_requerido}"
            )
        return usuario
    return role_checker