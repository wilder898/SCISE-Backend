from pydantic import BaseModel, Field
from typing import Optional


class EstudianteBase(BaseModel):
    nombre: str = Field(..., max_length=150)
    codigo_barras: str = Field(..., max_length=100)
    documento: Optional[str] = Field(None, max_length=50)


class EstudianteCreate(EstudianteBase):
    pass


class EstudianteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=150)
    estado: Optional[str] = None


class EstudianteResponse(EstudianteBase):
    id: int
    estado: str

    model_config = {"from_attributes": True}


class EstudianteLookupResponse(BaseModel):
    id: int
    nombre: str
    documento: str
    estado: str

    model_config = {"from_attributes": True}
