from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.controllers import reportes_controller
from app.core.deps import require_role
from app.db.session import get_db
from app.models.usuarios import Usuario
from app.schemas.reportes import (
    PaginatedReporteMovimientosResponse,
    ReportesResumenResponse,
)

router = APIRouter(prefix="/api/v1/reportes/movimientos", tags=["Reportes"])


@router.get(
    "/resumen",
    response_model=ReportesResumenResponse,
    summary="Resumen general de movimientos de equipos",
)
def obtener_resumen_movimientos(
    tipo: Optional[str] = Query(default=None),
    tipo_movimiento: Optional[str] = Query(default=None),
    fecha: Optional[date] = Query(default=None),
    fecha_desde: Optional[date] = Query(default=None),
    fecha_hasta: Optional[date] = Query(default=None),
    fecha_inicio: Optional[date] = Query(default=None),
    fecha_fin: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    _usuario_actual: Usuario = Depends(require_role("Administrador")),
):
    return reportes_controller.obtener_resumen_movimientos(
        db=db,
        tipo=tipo,
        tipo_movimiento=tipo_movimiento,
        fecha=fecha,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )


@router.get(
    "/historial",
    response_model=PaginatedReporteMovimientosResponse,
    summary="Historial de movimientos con paginacion y filtros",
)
def listar_historial_movimientos(
    tipo: Optional[str] = Query(default=None),
    tipo_movimiento: Optional[str] = Query(default=None),
    fecha: Optional[date] = Query(default=None),
    fecha_desde: Optional[date] = Query(default=None),
    fecha_hasta: Optional[date] = Query(default=None),
    fecha_inicio: Optional[date] = Query(default=None),
    fecha_fin: Optional[date] = Query(default=None),
    skip: Optional[int] = Query(default=None, ge=0),
    limit: Optional[int] = Query(default=None, ge=1, le=500),
    page: Optional[int] = Query(default=None, ge=1),
    page_size: Optional[int] = Query(default=None, ge=1, le=500),
    db: Session = Depends(get_db),
    _usuario_actual: Usuario = Depends(require_role("Administrador")),
):
    return reportes_controller.listar_historial_movimientos(
        db=db,
        tipo=tipo,
        tipo_movimiento=tipo_movimiento,
        fecha=fecha,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        skip=skip,
        limit=limit,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/export.csv",
    summary="Exportar historial de movimientos en CSV",
)
def exportar_historial_movimientos_csv(
    tipo: Optional[str] = Query(default=None),
    tipo_movimiento: Optional[str] = Query(default=None),
    fecha: Optional[date] = Query(default=None),
    fecha_desde: Optional[date] = Query(default=None),
    fecha_hasta: Optional[date] = Query(default=None),
    fecha_inicio: Optional[date] = Query(default=None),
    fecha_fin: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    _usuario_actual: Usuario = Depends(require_role("Administrador")),
):
    csv_content = reportes_controller.exportar_historial_movimientos_csv(
        db=db,
        tipo=tipo,
        tipo_movimiento=tipo_movimiento,
        fecha=fecha,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )
    return Response(
        content=csv_content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="reporte-movimientos.csv"'},
    )


@router.get(
    "/export.pdf",
    summary="Exportar historial de movimientos en PDF",
)
def exportar_historial_movimientos_pdf(
    tipo: Optional[str] = Query(default=None),
    tipo_movimiento: Optional[str] = Query(default=None),
    fecha: Optional[date] = Query(default=None),
    fecha_desde: Optional[date] = Query(default=None),
    fecha_hasta: Optional[date] = Query(default=None),
    fecha_inicio: Optional[date] = Query(default=None),
    fecha_fin: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    _usuario_actual: Usuario = Depends(require_role("Administrador")),
):
    filename, pdf_content = reportes_controller.exportar_historial_movimientos_pdf(
        db=db,
        tipo=tipo,
        tipo_movimiento=tipo_movimiento,
        fecha=fecha,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/export.xlsx",
    summary="Exportar historial de movimientos en Excel (.xlsx)",
)
def exportar_historial_movimientos_xlsx(
    tipo: Optional[str] = Query(default=None),
    tipo_movimiento: Optional[str] = Query(default=None),
    fecha: Optional[date] = Query(default=None),
    fecha_desde: Optional[date] = Query(default=None),
    fecha_hasta: Optional[date] = Query(default=None),
    fecha_inicio: Optional[date] = Query(default=None),
    fecha_fin: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    _usuario_actual: Usuario = Depends(require_role("Administrador")),
):
    filename, xlsx_content = reportes_controller.exportar_historial_movimientos_xlsx(
        db=db,
        tipo=tipo,
        tipo_movimiento=tipo_movimiento,
        fecha=fecha,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )
    return Response(
        content=xlsx_content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
