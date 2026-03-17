from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
from datetime import datetime
from app.models.equipos import Equipo
from app.models.estudiantes import Estudiante
from app.models.movimientos import Movimiento
from app.models.auditoria import Auditoria
from app.models.usuarios import Usuario
from app.core.logger import get_logger

logger = get_logger("movimientos")


def _get_estudiante_activo(db: Session, codigo_barras: str) -> Estudiante:
    est = db.query(Estudiante).filter(
        Estudiante.codigo_barras == codigo_barras,
        Estudiante.estado == "ACTIVO"            # ← STRING, no True
    ).first()
    if not est:
        raise HTTPException(404, "Estudiante no encontrado o inactivo")
    return est


def _get_equipo_con_lock(db: Session, codigo_barras: str) -> Equipo:
    equipo = db.execute(
        select(Equipo)
        .where(Equipo.codigo_barras_equipo == codigo_barras)
        .with_for_update()
    ).scalar_one_or_none()
    if not equipo:
        raise HTTPException(404, "Equipo no encontrado")
    return equipo


def _registrar_auditoria(db, usuario_id, evento, tipo, tabla_id, anterior, nuevo, url):
    db.add(Auditoria(
        usuario_id=usuario_id,              # ← FK, no texto plano
        evento=evento,
        tipo_auditoria=tipo,
        tabla_id=tabla_id,
        valor_anterior=anterior,
        valor_nuevo=nuevo,
        url=url,
        fecha_novedad=datetime.utcnow()
    ))


def asociar_equipo(db: Session, codigo_barras_est: str,
                   codigo_barras_eq: str, usuario: Usuario) -> dict:
    estudiante = _get_estudiante_activo(db, codigo_barras_est)
    equipo = _get_equipo_con_lock(db, codigo_barras_eq)

    anterior = str(equipo.estudiante_id)
    equipo.estudiante_id = estudiante.id

    _registrar_auditoria(db, usuario.id, "ASOCIAR_EQUIPO", "UPDATE",
                         equipo.id, anterior, str(estudiante.id),
                         "/api/v1/equipos/asociar")
    db.commit()
    return {"mensaje": f"Equipo '{equipo.nombre}' asociado a '{estudiante.nombre}'"}


def registrar_ingreso(db: Session, codigo_barras_est: str,
                      codigo_barras_eq: str, usuario: Usuario) -> Movimiento:
    estudiante = _get_estudiante_activo(db, codigo_barras_est)
    equipo = _get_equipo_con_lock(db, codigo_barras_eq)

    # HU-07: Anti-duplicidad
    if equipo.estado == "INGRESADO":
        logger.warning(f"Ingreso duplicado | equipo={codigo_barras_eq} | usuario={usuario.id}")
        raise HTTPException(409, "El equipo ya está registrado como INGRESADO")

    if equipo.estudiante_id != estudiante.id:
        raise HTTPException(403, "El equipo no está asociado a este estudiante")

    movimiento = Movimiento(
        usuario_id=usuario.id, equipo_id=equipo.id,
        estudiante_id=estudiante.id, tipo_movimiento="INGRESO",
        fecha_registro=datetime.utcnow()
    )
    equipo.estado = "INGRESADO"             # ← nuevo valor de estado

    db.add(movimiento)
    _registrar_auditoria(db, usuario.id, "REGISTRAR_INGRESO", "INSERT",
                         equipo.id, "DISPONIBLE", "INGRESADO",
                         "/api/v1/movimientos/ingreso")
    db.commit()
    db.refresh(movimiento)
    return movimiento


def registrar_salida(db: Session, codigo_barras_est: str,
                     codigo_barras_eq: str, usuario: Usuario) -> Movimiento:
    estudiante = _get_estudiante_activo(db, codigo_barras_est)
    equipo = _get_equipo_con_lock(db, codigo_barras_eq)

    # HU-07: Anti-duplicidad
    if equipo.estado != "INGRESADO":
        logger.warning(f"Salida sin ingreso previo | equipo={codigo_barras_eq} | usuario={usuario.id}")
        raise HTTPException(409, "El equipo no está registrado como INGRESADO")

    if equipo.estudiante_id != estudiante.id:
        raise HTTPException(403, "El equipo no está asociado a este estudiante")

    movimiento = Movimiento(
        usuario_id=usuario.id, equipo_id=equipo.id,
        estudiante_id=estudiante.id, tipo_movimiento="SALIDA",
        fecha_registro=datetime.utcnow()
    )
    equipo.estado = "RETIRADO"              # ← nuevo valor de estado

    db.add(movimiento)
    _registrar_auditoria(db, usuario.id, "REGISTRAR_SALIDA", "INSERT",
                         equipo.id, "INGRESADO", "RETIRADO",
                         "/api/v1/movimientos/salida")
    db.commit()
    db.refresh(movimiento)
    return movimiento