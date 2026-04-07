from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.equipos import Equipo
from app.models.usuarios import Usuario
from app.repositories.estudiante_repository import get_estudiante_by_id
from app.repositories.equipo_repository import (
    create_equipo,
    delete_equipo,
    get_equipo_by_barcode,
    get_equipo_by_id,
    get_equipo_by_serial,
    list_equipos_filtrados,
    update_equipo,
)
from app.repositories.auditoria_repository import create_auditoria
from app.schemas.equipo import EquipoCreate, EquipoUpdate


ESTADOS_VALIDOS_EQUIPO = {"DISPONIBLE", "INGRESADO", "RETIRADO"}


def listar_equipos_sistema(
    db: Session,
    q: str | None = None,
    tipo: str | None = None,
    estado: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> dict:
    estado_normalizado = estado.strip().upper() if estado else None
    if estado_normalizado and estado_normalizado not in ESTADOS_VALIDOS_EQUIPO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado inválido. Use DISPONIBLE, INGRESADO o RETIRADO",
        )

    q_normalizado = q.strip() if q else None
    tipo_normalizado = tipo.strip() if tipo else None

    equipos, total = list_equipos_filtrados(
        db=db,
        q=q_normalizado,
        tipo=tipo_normalizado,
        estado=estado_normalizado,
        skip=skip,
        limit=limit,
    )

    data = [_map_equipo_list_item(equipo) for equipo in equipos]

    return {
        "data": data,
        "meta": {
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_next": skip + len(data) < total,
        },
    }


def crear_equipo(db: Session, datos: EquipoCreate, usuario_actual: Usuario) -> Equipo:
    estudiante = get_estudiante_by_id(db, datos.estudiante_id)
    if not estudiante or estudiante.estado != "ACTIVO":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado o inactivo",
        )

    equipo = Equipo(
        codigo_barras_equipo=datos.codigo_barras_equipo,
        serial=datos.serial.strip(),
        nombre=datos.nombre.strip(),
        descripcion=(datos.descripcion or "").strip() or None,
        tipo_equipo=(datos.tipo_equipo or "").strip() or None,
        estado="DISPONIBLE",
        usuario_registra=usuario_actual.id,
        estudiante_id=datos.estudiante_id,
    )

    try:
        equipo_creado = create_equipo(db, equipo)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No fue posible registrar el equipo. Verifica si el serial ya existe.",
        ) from exc

    create_auditoria(
        db,
        usuario_actual.id,
        "CREAR_EQUIPO",
        "INSERT",
        equipo_creado.id,
        "",
        equipo_creado.serial,
        "/api/v1/equipos",
    )
    db.commit()
    db.refresh(equipo_creado)
    return equipo_creado


def actualizar_equipo(
    db: Session,
    equipo_id: int,
    datos: EquipoUpdate,
    usuario_actual: Usuario,
) -> Equipo:
    equipo = get_equipo_by_id(db, equipo_id)
    if not equipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado",
        )

    if datos.serial is not None:
        serial = datos.serial.strip()
        if not serial:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El serial no puede estar vacío",
            )
        existente = get_equipo_by_serial(db, serial)
        if existente and existente.id != equipo.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un equipo con ese serial",
            )
        equipo.serial = serial

    if datos.nombre is not None:
        nombre = datos.nombre.strip()
        if not nombre:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El nombre no puede estar vacío",
            )
        equipo.nombre = nombre

    if datos.codigo_barras_equipo is not None:
        codigo_barras = datos.codigo_barras_equipo.strip() or None
        if codigo_barras:
            existente = get_equipo_by_barcode(db, codigo_barras)
            if existente and existente.id != equipo.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe un equipo con ese código de barras",
                )
        equipo.codigo_barras_equipo = codigo_barras

    if datos.descripcion is not None:
        equipo.descripcion = datos.descripcion.strip() or None

    if datos.tipo_equipo is not None:
        equipo.tipo_equipo = datos.tipo_equipo.strip() or None

    if datos.estado is not None:
        estado_normalizado = datos.estado.strip().upper()
        if estado_normalizado not in ESTADOS_VALIDOS_EQUIPO:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Estado inválido. Use DISPONIBLE, INGRESADO o RETIRADO",
            )
        equipo.estado = estado_normalizado

    if datos.estudiante_id is not None:
        estudiante = get_estudiante_by_id(db, datos.estudiante_id)
        if not estudiante or estudiante.estado != "ACTIVO":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado o inactivo",
            )
        equipo.estudiante_id = estudiante.id

    try:
        equipo_actualizado = update_equipo(db, equipo)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No fue posible actualizar el equipo. Verifica datos únicos.",
        ) from exc

    create_auditoria(
        db,
        usuario_actual.id,
        "ACTUALIZAR_EQUIPO",
        "UPDATE",
        equipo_actualizado.id,
        "",
        equipo_actualizado.serial,
        f"/api/v1/equipos/{equipo_actualizado.id}",
    )
    db.commit()
    db.refresh(equipo_actualizado)
    return equipo_actualizado


def eliminar_equipo(db: Session, equipo_id: int, usuario_actual: Usuario) -> None:
    equipo = get_equipo_by_id(db, equipo_id)
    if not equipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado",
        )

    if equipo.estado == "INGRESADO":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar un equipo con ingreso activo",
        )

    serial_equipo = equipo.serial
    try:
        delete_equipo(db, equipo)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar el equipo porque tiene movimientos asociados",
        ) from exc

    create_auditoria(
        db,
        usuario_actual.id,
        "ELIMINAR_EQUIPO",
        "DELETE",
        equipo_id,
        serial_equipo,
        "",
        f"/api/v1/equipos/{equipo_id}",
    )
    db.commit()


def _map_equipo_list_item(equipo: Equipo) -> dict:
    return {
        "id": equipo.id,
        "codigo_barras_equipo": equipo.codigo_barras_equipo,
        "serial": equipo.serial,
        "nombre": equipo.nombre,
        "descripcion": equipo.descripcion,
        "tipo_equipo": equipo.tipo_equipo,
        "estado": equipo.estado,
        "fecha_registro": equipo.fecha_registro,
        "estudiante_id": equipo.estudiante_id,
        "estudiante_nombre": equipo.estudiante.nombre if equipo.estudiante else None,
        "estudiante_documento": equipo.estudiante.documento if equipo.estudiante else None,
    }
