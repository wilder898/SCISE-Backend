from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EquipoBase(BaseModel):
    nombre: str = Field(..., max_length=150)
    serial: str = Field(..., max_length=150)
    descripcion: Optional[str] = None
    tipo_equipo: Optional[str] = Field(None, max_length=100)


class EquipoCreate(EquipoBase):
    codigo_barras_equipo: Optional[str] = Field(None, max_length=100)
    estudiante_id: int


class EquipoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=150)
    descripcion: Optional[str] = None
    tipo_equipo: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = None
    estudiante_id: Optional[int] = None


class EquipoResponse(EquipoBase):
    id: int
    codigo_barras_equipo: Optional[str]
    estado: str
    fecha_registro: datetime
    estudiante_id: int

    model_config = {"from_attributes": True}


class EquipoAsociadoResponse(BaseModel):
    id: int
    nombre: str
    serial: str
    tipo: Optional[str] = None
    descripcion: Optional[str] = None
    estado: str
