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


class EquipoActivoResponse(BaseModel):
    id: int
    serial: str
    tipo: Optional[str] = None
    descripcion: Optional[str] = None
    estado: str
    timestamp_ingreso: datetime


class MovimientoSalidaBatchRequest(BaseModel):
    estudiante_id: int = Field(..., gt=0)
    equipos: list[int] = Field(..., min_length=1)
    observacion: Optional[str] = None


class MovimientoSalidaItemResponse(BaseModel):
    movimiento_id: int
    equipo_id: int
    serial: str
    fecha_registro: datetime
    tipo_movimiento: str


class MovimientoSalidaBatchResponse(BaseModel):
    estudiante_id: int
    total_registrados: int
    movimientos: list[MovimientoSalidaItemResponse]
    detail: str


class MovimientosPaginationMeta(BaseModel):
    total: int
    skip: int
    limit: int
    has_next: bool


class MovimientoListItemResponse(BaseModel):
    id: int
    tipo_movimiento: str
    fecha_registro: datetime
    usuario_id: int
    equipo_id: int
    estudiante_id: int
    serial: Optional[str] = None


class PaginatedMovimientoResponse(BaseModel):
    data: list[MovimientoListItemResponse]
    meta: MovimientosPaginationMeta
    total: int
    page: int
    total_pages: int


class MovimientoDetalleResponse(BaseModel):
    id: int
    tipo_movimiento: str
    fecha_registro: datetime
    usuario_id: int
    equipo_id: int
    estudiante_id: int
    serial: Optional[str] = None
    equipo_nombre: Optional[str] = None
    estudiante_nombre: Optional[str] = None
    estudiante_documento: Optional[str] = None
