from pydantic import BaseModel, Field
from datetime import datetime


class MovimientoRequest(BaseModel):
    codigo_barras_estudiante: str = Field(..., description="Código de barras del estudiante")
    codigo_barras_equipo: str = Field(..., description="Código de barras del equipo")


class MovimientoResponse(BaseModel):
    id: int
    tipo_movimiento: str
    fecha_registro: datetime
    usuario_id: int
    equipo_id: int
    estudiante_id: int

    model_config = {"from_attributes": True}
