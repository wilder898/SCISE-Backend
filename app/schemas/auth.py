from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str


class UserInToken(BaseModel):
    id: int
    nombre: str
    correo: str
    rol: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UserInToken        # tipado fuerte en lugar de dict
