from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ReportesResumenResponse(BaseModel):
    total_equipos: int
    equipos_en_instalacion: int
    equipos_fuera_instalacion: int
    movimientos_hoy: int
    inside_pct: int
    outside_pct: int


class ReporteMovimientoItemResponse(BaseModel):
    id: int
    movimiento_id: int
    tipo_movimiento: str
    fecha_registro: datetime
    equipo_id: int
    serial: Optional[str] = None
    equipo_nombre: Optional[str] = None
    equipo_descripcion: Optional[str] = None
    estado: Optional[str] = None
    usuario_nombre: Optional[str] = None
    estudiante_nombre: Optional[str] = None
    estudiante_documento: Optional[str] = None


class ReportesPaginationMeta(BaseModel):
    total: int
    skip: int
    limit: int
    has_next: bool


class PaginatedReporteMovimientosResponse(BaseModel):
    data: list[ReporteMovimientoItemResponse]
    meta: ReportesPaginationMeta
    total: int
    page: int
    total_pages: int
