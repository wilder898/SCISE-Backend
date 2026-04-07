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


class PaginationMeta(BaseModel):
    total: int
    skip: int
    limit: int
    has_next: bool


class UsuarioSistemaListItem(BaseModel):
    id: int
    documento: str
    nombre: str
    correo: Optional[EmailStr] = None
    area: Optional[str] = None
    estado: str
    rol_id: int
    rol: Optional[str] = None


class PaginatedUsuarioSistemaResponse(BaseModel):
    data: list[UsuarioSistemaListItem]
    meta: PaginationMeta


class UsuarioSistemaCreate(BaseModel):
    documento: str = Field(..., min_length=1, max_length=50)
    nombre: str = Field(..., min_length=1, max_length=150)
    correo: Optional[EmailStr] = None
    area: Optional[str] = Field(None, max_length=100)
    contrasena: str = Field(..., min_length=6, max_length=128)
    rol_id: int = Field(..., gt=0)
    estado: str = Field(default="ACTIVO", max_length=20)
    model_config = {"extra": "forbid"}


class UsuarioSistemaPatch(BaseModel):
    documento: Optional[str] = Field(default=None, min_length=1, max_length=50)
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=150)
    correo: Optional[EmailStr] = None
    area: Optional[str] = Field(default=None, max_length=100)
    rol_id: Optional[int] = Field(default=None, gt=0)
    model_config = {"extra": "forbid"}


class UsuarioSistemaEstadoUpdate(BaseModel):
    estado: str = Field(..., min_length=1, max_length=20)
    model_config = {"extra": "forbid"}


class UsuarioSistemaPasswordUpdate(BaseModel):
    nueva_password: str = Field(..., min_length=6, max_length=128)
    confirmacion: str = Field(..., min_length=6, max_length=128)
    model_config = {"extra": "forbid"}


class MessageResponse(BaseModel):
    detail: str


class UsuarioSistemaResponse(BaseModel):
    id: int
    documento: str
    nombre: str
    correo: Optional[EmailStr] = None
    area: Optional[str] = None
    estado: str
    rol_id: int
    rol: Optional[str] = None
