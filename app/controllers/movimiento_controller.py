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
