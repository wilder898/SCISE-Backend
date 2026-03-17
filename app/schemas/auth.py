from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: dict

class UserInToken(BaseModel):
    id: int
    nombre: str
    correo: str
    rol: str
