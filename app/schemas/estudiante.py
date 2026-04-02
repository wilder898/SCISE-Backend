from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class EstudianteBase(BaseModel):
    nombre: str = Field(..., max_length=150)
    documento: str = Field(..., max_length=50)
    codigo_barras: str = Field(..., max_length=100)
    email: Optional[EmailStr] = None
    rol: str = Field(..., max_length=50)
    celular: Optional[str] = Field(None, max_length=20)


class EstudianteCreate(EstudianteBase):
    estado: Optional[str] = "ACTIVO"


class EstudianteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=150)
    documento: Optional[str] = Field(None, max_length=50)
    codigo_barras: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    rol: Optional[str] = Field(None, max_length=50)
    celular: Optional[str] = Field(None, max_length=20)
    estado: Optional[str] = None


class EstudianteResponse(EstudianteBase):
    id: int
    estado: str

    model_config = {"from_attributes": True}


class EstudianteEstadoUpdate(BaseModel):
    estado: str


class EstudianteLookupResponse(BaseModel):
    id: int
    nombre: str
    documento: str
    rol: Optional[str] = None
    estado: str

    model_config = {"from_attributes": True}
