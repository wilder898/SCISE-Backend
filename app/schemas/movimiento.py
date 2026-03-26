from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


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


class MovimientoIngresoBatchRequest(BaseModel):
    estudiante_id: int = Field(..., gt=0)
    equipos: list[int] = Field(..., min_length=1)
    observacion: Optional[str] = None


class MovimientoIngresoItemResponse(BaseModel):
    movimiento_id: int
    equipo_id: int
    serial: str
    fecha_registro: datetime
    tipo_movimiento: str


class MovimientoIngresoBatchResponse(BaseModel):
    estudiante_id: int
    total_registrados: int
    movimientos: list[MovimientoIngresoItemResponse]
    detail: str
