from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UsuarioBase(BaseModel):
    documento: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=150)
    correo: Optional[EmailStr] = None
    area: Optional[str] = Field(None, max_length=100)


class UsuarioCreate(UsuarioBase):
    contrasena: str = Field(..., min_length=6)
    rol_id: int


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=150)
    correo: Optional[EmailStr] = None
    area: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = None


class UsuarioResponse(UsuarioBase):
    id: int
    estado: str
    rol_id: int

    model_config = {"from_attributes": True}
