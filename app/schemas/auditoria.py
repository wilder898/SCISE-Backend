from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PaginationMeta(BaseModel):
    total: int
    skip: int
    limit: int
    has_next: bool


class AuditoriaItemResponse(BaseModel):
    id: int
    usuario_id: int
    actor_nombre: Optional[str] = None
    evento: str
    tipo_auditoria: Optional[str] = None
    tabla_id: Optional[int] = None
    valor_anterior: Optional[str] = None
    valor_nuevo: Optional[str] = None
    url: Optional[str] = None
    fecha_novedad: datetime


class PaginatedAuditoriaResponse(BaseModel):
    data: list[AuditoriaItemResponse]
    meta: PaginationMeta
