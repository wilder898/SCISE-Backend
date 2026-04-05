from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from app.services import reportes_service


def obtener_resumen_movimientos(
    db: Session,
    tipo: Optional[str] = None,
    tipo_movimiento: Optional[str] = None,
    fecha: Optional[date] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
) -> dict:
    return reportes_service.obtener_resumen_movimientos(
        db=db,
        tipo=tipo,
        tipo_movimiento=tipo_movimiento,
        fecha=fecha,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )


def listar_historial_movimientos(
    db: Session,
    tipo: Optional[str] = None,
    tipo_movimiento: Optional[str] = None,
    fecha: Optional[date] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
) -> dict:
    return reportes_service.listar_historial_movimientos(
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


def exportar_historial_movimientos_csv(
    db: Session,
    tipo: Optional[str] = None,
    tipo_movimiento: Optional[str] = None,
    fecha: Optional[date] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
) -> str:
    return reportes_service.exportar_historial_movimientos_csv(
        db=db,
        tipo=tipo,
        tipo_movimiento=tipo_movimiento,
        fecha=fecha,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )


def exportar_historial_movimientos_xlsx(
    db: Session,
    tipo: Optional[str] = None,
    tipo_movimiento: Optional[str] = None,
    fecha: Optional[date] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
) -> tuple[str, bytes]:
    return reportes_service.exportar_historial_movimientos_xlsx(
        db=db,
        tipo=tipo,
        tipo_movimiento=tipo_movimiento,
        fecha=fecha,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )


def exportar_historial_movimientos_pdf(
    db: Session,
    tipo: Optional[str] = None,
    tipo_movimiento: Optional[str] = None,
    fecha: Optional[date] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
) -> tuple[str, bytes]:
    return reportes_service.exportar_historial_movimientos_pdf(
        db=db,
        tipo=tipo,
        tipo_movimiento=tipo_movimiento,
        fecha=fecha,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )


def obtener_resumen_dashboard(
    db: Session,
    tipo: Optional[str] = None,
    tipo_movimiento: Optional[str] = None,
    fecha: Optional[date] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
) -> dict:
    return reportes_service.obtener_resumen_dashboard(
        db=db,
        tipo=tipo,
        tipo_movimiento=tipo_movimiento,
        fecha=fecha,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )


def listar_historial_reciente_dashboard(
    db: Session,
    tipo: Optional[str] = None,
    tipo_movimiento: Optional[str] = None,
    fecha: Optional[date] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    page: int = 1,
    limit: int = 5,
) -> dict:
    return reportes_service.listar_historial_reciente_dashboard(
        db=db,
        tipo=tipo,
        tipo_movimiento=tipo_movimiento,
        fecha=fecha,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        page=page,
        limit=limit,
    )
