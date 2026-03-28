from datetime import date, datetime, time
from typing import Optional
from sqlalchemy import case, func
from sqlalchemy.orm import Session
from app.models.equipos import Equipo
from app.models.estudiantes import Estudiante
from app.models.movimientos import Movimiento
from app.models.usuarios import Usuario


def create_movimiento(db: Session, movimiento: Movimiento) -> Movimiento:
    db.add(movimiento)
    db.commit()
    db.refresh(movimiento)
    return movimiento


def list_movimientos(db: Session, skip: int = 0, limit: int = 50) -> list[Movimiento]:
    return db.query(Movimiento).order_by(Movimiento.fecha_registro.desc()).offset(skip).limit(limit).all()


def list_movimientos_by_equipo(db: Session, equipo_id: int) -> list[Movimiento]:
    return (
        db.query(Movimiento)
        .filter(Movimiento.equipo_id == equipo_id)
        .order_by(Movimiento.fecha_registro.desc())
        .all()
    )


def list_movimientos_by_estudiante(db: Session, estudiante_id: int) -> list[Movimiento]:
    return (
        db.query(Movimiento)
        .filter(Movimiento.estudiante_id == estudiante_id)
        .order_by(Movimiento.fecha_registro.desc())
        .all()
    )


def get_latest_movimiento_by_equipo_and_tipo(
    db: Session,
    equipo_id: int,
    tipo_movimiento: str,
) -> Optional[Movimiento]:
    return (
        db.query(Movimiento)
        .filter(
            Movimiento.equipo_id == equipo_id,
            Movimiento.tipo_movimiento == tipo_movimiento,
        )
        .order_by(Movimiento.fecha_registro.desc())
        .first()
    )


def _build_historial_conditions(
    tipo: Optional[str] = None,
    fecha: Optional[date] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
) -> list:
    conditions = []
    if tipo:
        conditions.append(func.upper(Movimiento.tipo_movimiento) == tipo.upper())

    if fecha:
        fecha_inicio = datetime.combine(fecha, time.min)
        fecha_fin = datetime.combine(fecha, time.max)
        conditions.append(Movimiento.fecha_registro >= fecha_inicio)
        conditions.append(Movimiento.fecha_registro <= fecha_fin)

    if fecha_desde:
        conditions.append(Movimiento.fecha_registro >= datetime.combine(fecha_desde, time.min))

    if fecha_hasta:
        conditions.append(Movimiento.fecha_registro <= datetime.combine(fecha_hasta, time.max))

    return conditions


def _apply_historial_filters(
    query,
    tipo: Optional[str] = None,
    fecha: Optional[date] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
):
    conditions = _build_historial_conditions(
        tipo=tipo,
        fecha=fecha,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
    if not conditions:
        return query
    return query.filter(*conditions)


def _build_historial_query(
    db: Session,
):
    return (
        db.query(
            Movimiento.id.label("movimiento_id"),
            Movimiento.tipo_movimiento.label("tipo_movimiento"),
            Movimiento.fecha_registro.label("fecha_registro"),
            Movimiento.equipo_id.label("equipo_id"),
            Equipo.serial.label("serial"),
            Equipo.nombre.label("equipo_nombre"),
            Equipo.descripcion.label("equipo_descripcion"),
            Equipo.estado.label("estado"),
            Usuario.nombre.label("usuario_nombre"),
            Estudiante.nombre.label("estudiante_nombre"),
            Estudiante.documento.label("estudiante_documento"),
        )
        .join(Equipo, Equipo.id == Movimiento.equipo_id)
        .join(Estudiante, Estudiante.id == Movimiento.estudiante_id)
        .outerjoin(Usuario, Usuario.id == Movimiento.usuario_id)
    )


def list_movimientos_historial(
    db: Session,
    tipo: Optional[str] = None,
    fecha: Optional[date] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    skip: int = 0,
    limit: int = 20,
):
    conditions = _build_historial_conditions(
        tipo=tipo,
        fecha=fecha,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
    query = _build_historial_query(db=db).filter(*conditions)
    total = (
        db.query(func.count(Movimiento.id))
        .filter(*conditions)
        .scalar()
        or 0
    )
    rows = (
        query.order_by(Movimiento.fecha_registro.desc(), Movimiento.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return rows, total


def list_movimientos_historial_for_export(
    db: Session,
    tipo: Optional[str] = None,
    fecha: Optional[date] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
):
    conditions = _build_historial_conditions(
        tipo=tipo,
        fecha=fecha,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
    query = _build_historial_query(db=db).filter(*conditions)
    return query.order_by(Movimiento.fecha_registro.desc(), Movimiento.id.desc()).all()


def get_resumen_movimientos(
    db: Session,
    tipo: Optional[str] = None,
    fecha: Optional[date] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
) -> dict:
    total_equipos, equipos_en_instalacion, equipos_fuera_instalacion = (
        db.query(
            func.count(Equipo.id),
            func.coalesce(func.sum(case((Equipo.estado == "INGRESADO", 1), else_=0)), 0),
            func.coalesce(func.sum(case((Equipo.estado != "INGRESADO", 1), else_=0)), 0),
        ).one()
    )

    movimientos_query = db.query(func.count(Movimiento.id))
    if not fecha and not fecha_desde and not fecha_hasta:
        fecha = datetime.utcnow().date()
    movimientos_query = _apply_historial_filters(
        query=movimientos_query,
        tipo=tipo,
        fecha=fecha,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
    movimientos_hoy = int(movimientos_query.scalar() or 0)

    total_equipos = int(total_equipos or 0)
    equipos_en_instalacion = int(equipos_en_instalacion or 0)
    equipos_fuera_instalacion = int(equipos_fuera_instalacion or 0)
    inside_pct = round((equipos_en_instalacion / total_equipos) * 100) if total_equipos else 0
    outside_pct = round((equipos_fuera_instalacion / total_equipos) * 100) if total_equipos else 0

    return {
        "total_equipos": total_equipos,
        "equipos_en_instalacion": equipos_en_instalacion,
        "equipos_fuera_instalacion": equipos_fuera_instalacion,
        "movimientos_hoy": movimientos_hoy,
        "inside_pct": inside_pct,
        "outside_pct": outside_pct,
    }
