from fastapi import HTTPException
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.movimientos import Movimiento
from app.models.usuarios import Usuario
from app.repositories.estudiante_repository import (
    get_estudiante_activo_by_barcode,
    get_estudiante_by_id,
)
from app.repositories.equipo_repository import (
    get_equipo_by_barcode_with_lock,
    get_equipo_by_id_with_lock,
    list_equipos_ingresados_by_estudiante,
)
from app.repositories.movimiento_repository import get_latest_movimiento_by_equipo_and_tipo
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


def registrar_ingresos_batch(
    db: Session,
    estudiante_id: int,
    equipos_ids: list[int],
    usuario: Usuario,
) -> dict:
    if len(set(equipos_ids)) != len(equipos_ids):
        raise HTTPException(400, "La lista de equipos contiene duplicados")

    estudiante = get_estudiante_by_id(db, estudiante_id)
    if not estudiante or estudiante.estado != "ACTIVO":
        raise HTTPException(404, "Estudiante no encontrado o inactivo")

    movimientos_creados: list[tuple[Movimiento, str]] = []

    try:
        for equipo_id in equipos_ids:
            equipo = get_equipo_by_id_with_lock(db, equipo_id)
            if not equipo:
                raise HTTPException(404, f"Equipo no encontrado: {equipo_id}")

            if equipo.estado == "INGRESADO":
                logger.warning(
                    "Ingreso duplicado batch | equipo_id=%s | usuario=%s",
                    equipo_id,
                    usuario.id,
                )
                raise HTTPException(409, f"El equipo {equipo_id} ya está INGRESADO")

            if equipo.estudiante_id != estudiante.id:
                raise HTTPException(
                    403,
                    f"El equipo {equipo_id} no está asociado al estudiante {estudiante.id}",
                )

            estado_anterior = equipo.estado
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
                db,
                usuario.id,
                "REGISTRAR_INGRESO_BATCH",
                "INSERT",
                equipo.id,
                estado_anterior,
                "INGRESADO",
                "/api/v1/movimientos/ingresos",
            )
            movimientos_creados.append((movimiento, equipo.serial))

        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        logger.exception("Fallo registrando ingresos batch")
        raise HTTPException(500, "Error interno al registrar ingresos")

    movimientos_respuesta = []
    for movimiento, serial in movimientos_creados:
        db.refresh(movimiento)
        movimientos_respuesta.append(
            {
                "movimiento_id": movimiento.id,
                "equipo_id": movimiento.equipo_id,
                "serial": serial,
                "fecha_registro": movimiento.fecha_registro,
                "tipo_movimiento": movimiento.tipo_movimiento,
            }
        )

    return {
        "estudiante_id": estudiante.id,
        "total_registrados": len(movimientos_respuesta),
        "movimientos": movimientos_respuesta,
        "detail": "Ingresos registrados correctamente",
    }


def listar_equipos_activos_por_estudiante(db: Session, estudiante_id: int) -> list[dict]:
    estudiante = get_estudiante_by_id(db, estudiante_id)
    if not estudiante or estudiante.estado != "ACTIVO":
        raise HTTPException(404, "Estudiante no encontrado o inactivo")

    equipos = list_equipos_ingresados_by_estudiante(db, estudiante_id)
    respuesta = []

    for equipo in equipos:
        ultimo_ingreso = get_latest_movimiento_by_equipo_and_tipo(
            db,
            equipo_id=equipo.id,
            tipo_movimiento="INGRESO",
        )
        timestamp_ingreso = (
            ultimo_ingreso.fecha_registro if ultimo_ingreso else equipo.fecha_registro
        )
        respuesta.append(
            {
                "id": equipo.id,
                "serial": equipo.serial,
                "tipo": equipo.tipo_equipo,
                "descripcion": equipo.descripcion,
                "estado": equipo.estado,
                "timestamp_ingreso": timestamp_ingreso,
            }
        )

    return respuesta


def registrar_salidas_batch(
    db: Session,
    estudiante_id: int,
    equipos_ids: list[int],
    usuario: Usuario,
) -> dict:
    if len(set(equipos_ids)) != len(equipos_ids):
        raise HTTPException(400, "La lista de equipos contiene duplicados")

    estudiante = get_estudiante_by_id(db, estudiante_id)
    if not estudiante or estudiante.estado != "ACTIVO":
        raise HTTPException(404, "Estudiante no encontrado o inactivo")

    movimientos_creados: list[tuple[Movimiento, str]] = []

    try:
        for equipo_id in equipos_ids:
            equipo = get_equipo_by_id_with_lock(db, equipo_id)
            if not equipo:
                raise HTTPException(404, f"Equipo no encontrado: {equipo_id}")

            if equipo.estado != "INGRESADO":
                logger.warning(
                    "Salida inválida batch | equipo_id=%s | estado=%s | usuario=%s",
                    equipo_id,
                    equipo.estado,
                    usuario.id,
                )
                raise HTTPException(409, f"El equipo {equipo_id} no está INGRESADO")

            if equipo.estudiante_id != estudiante.id:
                raise HTTPException(
                    403,
                    f"El equipo {equipo_id} no está asociado al estudiante {estudiante.id}",
                )

            estado_anterior = equipo.estado
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
                db,
                usuario.id,
                "REGISTRAR_SALIDA_BATCH",
                "INSERT",
                equipo.id,
                estado_anterior,
                "RETIRADO",
                "/api/v1/movimientos/salidas",
            )
            movimientos_creados.append((movimiento, equipo.serial))

        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        logger.exception("Fallo registrando salidas batch")
        raise HTTPException(500, "Error interno al registrar salidas")

    movimientos_respuesta = []
    for movimiento, serial in movimientos_creados:
        db.refresh(movimiento)
        movimientos_respuesta.append(
            {
                "movimiento_id": movimiento.id,
                "equipo_id": movimiento.equipo_id,
                "serial": serial,
                "fecha_registro": movimiento.fecha_registro,
                "tipo_movimiento": movimiento.tipo_movimiento,
            }
        )

    return {
        "estudiante_id": estudiante.id,
        "total_registrados": len(movimientos_respuesta),
        "movimientos": movimientos_respuesta,
        "detail": "Salidas registradas correctamente",
    }
