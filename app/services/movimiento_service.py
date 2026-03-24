from fastapi import HTTPException
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.movimientos import Movimiento
from app.models.usuarios import Usuario
from app.repositories.estudiante_repository import get_estudiante_activo_by_barcode
from app.repositories.equipo_repository import get_equipo_by_barcode_with_lock
from app.repositories.movimiento_repository import create_movimiento
from app.repositories.auditoria_repository import create_auditoria
from app.core.logger import get_logger

logger = get_logger("movimientos")


def asociar_equipo(
    db: Session, codigo_barras_est: str, codigo_barras_eq: str, usuario: Usuario
) -> dict:
    estudiante = get_estudiante_activo_by_barcode(db, codigo_barras_est)
    if not estudiante:
        raise HTTPException(404, "Estudiante no encontrado o inactivo")

    equipo = get_equipo_by_barcode_with_lock(db, codigo_barras_eq)
    if not equipo:
        raise HTTPException(404, "Equipo no encontrado")

    anterior = str(equipo.estudiante_id)
    equipo.estudiante_id = estudiante.id

    create_auditoria(
        db, usuario.id, "ASOCIAR_EQUIPO", "UPDATE",
        equipo.id, anterior, str(estudiante.id),
        "/api/v1/equipos/asociar",
    )
    db.commit()
    return {"mensaje": f"Equipo '{equipo.nombre}' asociado a '{estudiante.nombre}'"}


def registrar_ingreso(
    db: Session, codigo_barras_est: str, codigo_barras_eq: str, usuario: Usuario
) -> Movimiento:
    estudiante = get_estudiante_activo_by_barcode(db, codigo_barras_est)
    if not estudiante:
        raise HTTPException(404, "Estudiante no encontrado o inactivo")

    equipo = get_equipo_by_barcode_with_lock(db, codigo_barras_eq)
    if not equipo:
        raise HTTPException(404, "Equipo no encontrado")

    if equipo.estado == "INGRESADO":
        logger.warning(
            "Ingreso duplicado | equipo=%s | usuario=%s", codigo_barras_eq, usuario.id
        )
        raise HTTPException(409, "El equipo ya está registrado como INGRESADO")

    if equipo.estudiante_id != estudiante.id:
        raise HTTPException(403, "El equipo no está asociado a este estudiante")

    movimiento = Movimiento(
        usuario_id=usuario.id,
        equipo_id=equipo.id,
        estudiante_id=estudiante.id,
        tipo_movimiento="INGRESO",
        fecha_registro=datetime.utcnow(),
    )
    equipo.estado = "INGRESADO"

    db.add(movimiento)
    create_auditoria(
        db, usuario.id, "REGISTRAR_INGRESO", "INSERT",
        equipo.id, "DISPONIBLE", "INGRESADO",
        "/api/v1/movimientos/ingreso",
    )
    db.commit()
    db.refresh(movimiento)
    return movimiento


def registrar_salida(
    db: Session, codigo_barras_est: str, codigo_barras_eq: str, usuario: Usuario
) -> Movimiento:
    estudiante = get_estudiante_activo_by_barcode(db, codigo_barras_est)
    if not estudiante:
        raise HTTPException(404, "Estudiante no encontrado o inactivo")

    equipo = get_equipo_by_barcode_with_lock(db, codigo_barras_eq)
    if not equipo:
        raise HTTPException(404, "Equipo no encontrado")

    if equipo.estado != "INGRESADO":
        logger.warning(
            "Salida sin ingreso previo | equipo=%s | usuario=%s", codigo_barras_eq, usuario.id
        )
        raise HTTPException(409, "El equipo no está registrado como INGRESADO")

    if equipo.estudiante_id != estudiante.id:
        raise HTTPException(403, "El equipo no está asociado a este estudiante")

    movimiento = Movimiento(
        usuario_id=usuario.id,
        equipo_id=equipo.id,
        estudiante_id=estudiante.id,
        tipo_movimiento="SALIDA",
        fecha_registro=datetime.utcnow(),
    )
    equipo.estado = "RETIRADO"

    db.add(movimiento)
    create_auditoria(
        db, usuario.id, "REGISTRAR_SALIDA", "INSERT",
        equipo.id, "INGRESADO", "RETIRADO",
        "/api/v1/movimientos/salida",
    )
    db.commit()
    db.refresh(movimiento)
    return movimiento

