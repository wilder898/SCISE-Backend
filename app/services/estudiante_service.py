from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.estudiantes import Estudiante
from app.models.usuarios import Usuario
from app.repositories.estudiante_repository import (
    create_estudiante,
    get_estudiante_activo_by_documento_o_codigo_barras,
    get_estudiante_by_codigo_barras,
    get_estudiante_by_documento,
    get_estudiante_by_email,
    get_estudiante_by_id,
    list_estudiantes,
    update_estudiante,
)
from app.repositories.equipo_repository import list_equipos_by_estudiante
from app.schemas.estudiante import EstudianteCreate, EstudianteEstadoUpdate, EstudianteUpdate

ESTADOS_VALIDOS = {"ACTIVO", "INACTIVO"}


def _normalizar_estado(estado: str) -> str:
    estado_normalizado = estado.strip().upper()
    if estado_normalizado not in ESTADOS_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Estado inválido. Valores permitidos: ACTIVO, INACTIVO",
        )
    return estado_normalizado


def _normalizar_rol(rol: str) -> str:
    rol_normalizado = rol.strip()
    if not rol_normalizado:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El rol es obligatorio",
        )
    return rol_normalizado


def _es_administrador(usuario: Usuario | None) -> bool:
    if not usuario or not usuario.rol:
        return False
    return str(usuario.rol.nombre or "").strip().lower() == "administrador"


def buscar_estudiante_activo_por_documento(db: Session, documento: str) -> Estudiante:
    identificador_normalizado = documento.strip()
    if not identificador_normalizado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El identificador (documento o carnet) es obligatorio",
        )

    estudiante = get_estudiante_activo_by_documento_o_codigo_barras(
        db,
        identificador_normalizado,
    )
    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado o inactivo",
        )

    return estudiante


def listar_estudiantes_operativos(
    db: Session,
    skip: int = 0,
    limit: int = 200,
) -> list[Estudiante]:
    return list_estudiantes(db, skip=skip, limit=limit)


def crear_estudiante_operativo(
    db: Session,
    datos: EstudianteCreate,
    usuario_creador_id: int,
) -> Estudiante:
    documento = datos.documento.strip()
    codigo_barras = datos.codigo_barras.strip()
    nombre = datos.nombre.strip()
    email = str(datos.email).strip().lower() if datos.email else None
    rol = _normalizar_rol(datos.rol)
    celular = datos.celular.strip() if datos.celular else None
    estado = _normalizar_estado(datos.estado or "ACTIVO")

    if not documento or not codigo_barras or not nombre:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="documento, codigo_barras y nombre son obligatorios",
        )

    if get_estudiante_by_documento(db, documento):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un estudiante con ese documento",
        )
    if get_estudiante_by_codigo_barras(db, codigo_barras):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un estudiante con ese carnet/codigo de barras",
        )
    if email and get_estudiante_by_email(db, email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un estudiante con ese email",
        )

    estudiante = Estudiante(
        documento=documento,
        codigo_barras=codigo_barras,
        nombre=nombre,
        email=email,
        rol=rol,
        celular=celular,
        estado=estado,
        usuario_crea=usuario_creador_id,
    )
    return create_estudiante(db, estudiante)


def actualizar_estudiante_operativo(
    db: Session,
    estudiante_id: int,
    datos: EstudianteUpdate,
    usuario_actual: Usuario | None = None,
) -> Estudiante:
    estudiante = get_estudiante_by_id(db, estudiante_id)
    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado",
        )

    if datos.documento is not None:
        documento = datos.documento.strip()
        if not documento:
            raise HTTPException(status_code=422, detail="El documento no puede estar vacío")
        existente = get_estudiante_by_documento(db, documento)
        if existente and existente.id != estudiante.id:
            raise HTTPException(status_code=409, detail="Ya existe un estudiante con ese documento")
        estudiante.documento = documento

    if datos.codigo_barras is not None:
        codigo_barras = datos.codigo_barras.strip()
        if not codigo_barras:
            raise HTTPException(status_code=422, detail="El carnet no puede estar vacío")
        existente = get_estudiante_by_codigo_barras(db, codigo_barras)
        if existente and existente.id != estudiante.id:
            raise HTTPException(
                status_code=409,
                detail="Ya existe un estudiante con ese carnet/codigo de barras",
            )
        estudiante.codigo_barras = codigo_barras

    if datos.nombre is not None:
        nombre = datos.nombre.strip()
        if not nombre:
            raise HTTPException(status_code=422, detail="El nombre no puede estar vacío")
        estudiante.nombre = nombre

    if datos.email is not None:
        email = str(datos.email).strip().lower() if datos.email else None
        if email:
            existente = get_estudiante_by_email(db, email)
            if existente and existente.id != estudiante.id:
                raise HTTPException(status_code=409, detail="Ya existe un estudiante con ese email")
        estudiante.email = email

    puede_editar_avanzado = _es_administrador(usuario_actual)

    if datos.rol is not None and puede_editar_avanzado:
        estudiante.rol = _normalizar_rol(datos.rol)

    if datos.celular is not None:
        estudiante.celular = datos.celular.strip() if datos.celular else None

    if datos.estado is not None and puede_editar_avanzado:
        estudiante.estado = _normalizar_estado(datos.estado)

    return update_estudiante(db, estudiante)


def actualizar_estado_estudiante(
    db: Session,
    estudiante_id: int,
    datos: EstudianteEstadoUpdate,
) -> Estudiante:
    estudiante = get_estudiante_by_id(db, estudiante_id)
    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado",
        )

    estudiante.estado = _normalizar_estado(datos.estado)
    return update_estudiante(db, estudiante)


def listar_equipos_asociados_por_estudiante(
    db: Session,
    estudiante_id: int,
    solo_disponibles_ingreso: bool = True,
) -> list[dict]:
    estudiante = get_estudiante_by_id(db, estudiante_id)
    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado",
        )

    if solo_disponibles_ingreso and estudiante.estado != "ACTIVO":
        return []

    equipos = list_equipos_by_estudiante(
        db,
        estudiante_id=estudiante_id,
        solo_disponibles_ingreso=solo_disponibles_ingreso,
    )

    return [
        {
            "id": equipo.id,
            "nombre": equipo.nombre,
            "serial": equipo.serial,
            "tipo": equipo.tipo_equipo,
            "descripcion": equipo.descripcion,
            "estado": equipo.estado,
        }
        for equipo in equipos
    ]
