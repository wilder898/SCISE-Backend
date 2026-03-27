from sqlalchemy.orm import Session
from app.models.usuarios import Usuario
from app.services import movimiento_service


def asociar_equipo(
    db: Session, codigo_barras_est: str, codigo_barras_eq: str, usuario: Usuario
) -> dict:
    """Coordina la solicitud de asociación equipo-estudiante."""
    return movimiento_service.asociar_equipo(db, codigo_barras_est, codigo_barras_eq, usuario)


def registrar_ingreso(
    db: Session, codigo_barras_est: str, codigo_barras_eq: str, usuario: Usuario
):
    """Coordina el registro de ingreso de un equipo."""
    return movimiento_service.registrar_ingreso(db, codigo_barras_est, codigo_barras_eq, usuario)


def registrar_salida(
    db: Session, codigo_barras_est: str, codigo_barras_eq: str, usuario: Usuario
):
    """Coordina el registro de salida de un equipo."""
    return movimiento_service.registrar_salida(db, codigo_barras_est, codigo_barras_eq, usuario)


def registrar_ingresos_batch(
    db: Session,
    estudiante_id: int,
    equipos_ids: list[int],
    usuario: Usuario,
):
    """Coordina el registro batch de ingresos por IDs de equipo."""
    return movimiento_service.registrar_ingresos_batch(db, estudiante_id, equipos_ids, usuario)


def listar_equipos_activos_por_estudiante(db: Session, estudiante_id: int, usuario: Usuario):
    """Coordina el listado de equipos activos de un estudiante."""
    return movimiento_service.listar_equipos_activos_por_estudiante(db, estudiante_id)


def registrar_salidas_batch(
    db: Session,
    estudiante_id: int,
    equipos_ids: list[int],
    usuario: Usuario,
):
    """Coordina el registro batch de salidas por IDs de equipo."""
    return movimiento_service.registrar_salidas_batch(db, estudiante_id, equipos_ids, usuario)
