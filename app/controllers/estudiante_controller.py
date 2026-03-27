from sqlalchemy.orm import Session
from app.models.usuarios import Usuario
from app.services import estudiante_service


def buscar_por_documento(documento: str, db: Session, _usuario_actual: Usuario):
    """Coordina la búsqueda de un estudiante activo por documento."""
    return estudiante_service.buscar_estudiante_activo_por_documento(db, documento)


def listar_equipos_asociados(
    estudiante_id: int,
    solo_disponibles_ingreso: bool,
    db: Session,
    _usuario_actual: Usuario,
):
    """Coordina el listado de equipos asociados a un estudiante."""
    return estudiante_service.listar_equipos_asociados_por_estudiante(
        db=db,
        estudiante_id=estudiante_id,
        solo_disponibles_ingreso=solo_disponibles_ingreso,
    )
