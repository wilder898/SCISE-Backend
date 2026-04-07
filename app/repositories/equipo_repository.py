from typing import Optional
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload
from app.models.equipos import Equipo
from app.models.estudiantes import Estudiante


def get_equipo_by_id(db: Session, equipo_id: int) -> Optional[Equipo]:
    return db.query(Equipo).filter(Equipo.id == equipo_id).first()


def get_equipo_by_id_with_lock(db: Session, equipo_id: int) -> Optional[Equipo]:
    """Obtiene el equipo por ID con bloqueo de fila para operaciones concurrentes."""
    return db.execute(
        select(Equipo)
        .where(Equipo.id == equipo_id)
        .with_for_update()
    ).scalar_one_or_none()


def get_equipo_by_barcode(db: Session, codigo_barras: str) -> Optional[Equipo]:
    return (
        db.query(Equipo)
        .filter(Equipo.codigo_barras_equipo == codigo_barras)
        .first()
    )


def get_equipo_by_serial(db: Session, serial: str) -> Optional[Equipo]:
    return db.query(Equipo).filter(Equipo.serial == serial).first()


def get_equipo_by_barcode_with_lock(db: Session, codigo_barras: str) -> Optional[Equipo]:
    """Obtiene el equipo con bloqueo de fila para operaciones concurrentes."""
    return db.execute(
        select(Equipo)
        .where(Equipo.codigo_barras_equipo == codigo_barras)
        .with_for_update()
    ).scalar_one_or_none()


def list_equipos(db: Session, skip: int = 0, limit: int = 50) -> list[Equipo]:
    return db.query(Equipo).offset(skip).limit(limit).all()


def list_equipos_filtrados(
    db: Session,
    q: Optional[str] = None,
    tipo: Optional[str] = None,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Equipo], int]:
    query = db.query(Equipo).options(joinedload(Equipo.estudiante))

    if q:
        patron = f"%{q}%"
        query = query.join(Estudiante, Equipo.estudiante_id == Estudiante.id).filter(
            or_(
                Equipo.serial.ilike(patron),
                Equipo.nombre.ilike(patron),
                Equipo.descripcion.ilike(patron),
                Equipo.tipo_equipo.ilike(patron),
                Equipo.codigo_barras_equipo.ilike(patron),
                Estudiante.nombre.ilike(patron),
                Estudiante.documento.ilike(patron),
            )
        )

    if tipo:
        query = query.filter(func.lower(Equipo.tipo_equipo) == tipo.lower())

    if estado:
        query = query.filter(func.lower(Equipo.estado) == estado.lower())

    total = query.count()
    equipos = query.order_by(Equipo.fecha_registro.desc()).offset(skip).limit(limit).all()
    return equipos, total


def list_equipos_by_estudiante(
    db: Session,
    estudiante_id: int,
    solo_disponibles_ingreso: bool = True,
) -> list[Equipo]:
    query = db.query(Equipo).filter(Equipo.estudiante_id == estudiante_id)
    if solo_disponibles_ingreso:
        query = query.filter(Equipo.estado != "INGRESADO")

    return query.order_by(Equipo.nombre.asc()).all()


def list_equipos_ingresados_by_estudiante(db: Session, estudiante_id: int) -> list[Equipo]:
    return (
        db.query(Equipo)
        .filter(
            Equipo.estudiante_id == estudiante_id,
            Equipo.estado == "INGRESADO",
        )
        .order_by(Equipo.nombre.asc())
        .all()
    )


def create_equipo(db: Session, equipo: Equipo) -> Equipo:
    db.add(equipo)
    db.commit()
    db.refresh(equipo)
    return equipo


def update_equipo(db: Session, equipo: Equipo) -> Equipo:
    db.commit()
    db.refresh(equipo)
    return equipo


def delete_equipo(db: Session, equipo: Equipo) -> None:
    db.delete(equipo)
    db.commit()
