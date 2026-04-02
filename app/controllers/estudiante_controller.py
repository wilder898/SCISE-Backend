from sqlalchemy.orm import Session
from app.models.usuarios import Usuario
from app.schemas.estudiante import EstudianteCreate, EstudianteEstadoUpdate, EstudianteUpdate
from app.services import estudiante_service


def listar_estudiantes(skip: int, limit: int, db: Session, _usuario_actual: Usuario):
    """Coordina el listado de estudiantes operativos."""
    return estudiante_service.listar_estudiantes_operativos(db=db, skip=skip, limit=limit)


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


def crear_estudiante(datos: EstudianteCreate, db: Session, usuario_actual: Usuario):
    """Coordina la creación de un estudiante operativo."""
    return estudiante_service.crear_estudiante_operativo(
        db=db,
        datos=datos,
        usuario_creador_id=usuario_actual.id,
    )


def actualizar_estudiante(
    estudiante_id: int,
    datos: EstudianteUpdate,
    db: Session,
    _usuario_actual: Usuario,
):
    """Coordina la actualización parcial de un estudiante operativo."""
    return estudiante_service.actualizar_estudiante_operativo(
        db=db,
        estudiante_id=estudiante_id,
        datos=datos,
    )


def actualizar_estado_estudiante(
    estudiante_id: int,
    datos: EstudianteEstadoUpdate,
    db: Session,
    _usuario_actual: Usuario,
):
    """Coordina la actualización de estado de un estudiante operativo."""
    return estudiante_service.actualizar_estado_estudiante(
        db=db,
        estudiante_id=estudiante_id,
        datos=datos,
    )
