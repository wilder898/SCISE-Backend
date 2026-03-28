import csv
from datetime import date
from io import BytesIO, StringIO
from typing import Optional
from fastapi import HTTPException, status
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from sqlalchemy.orm import Session
from app.repositories.movimiento_repository import (
    get_resumen_movimientos,
    list_movimientos_historial,
    list_movimientos_historial_for_export,
)

EXPORT_HEADERS = [
    "Movimiento ID",
    "Tipo Movimiento",
    "Fecha Registro",
    "Equipo ID",
    "Serial",
    "Equipo Nombre",
    "Equipo Descripcion",
    "Estado",
    "Usuario Registro",
    "Estudiante",
    "Documento Estudiante",
]

EXPORT_COLUMN_WIDTHS = [16, 20, 22, 12, 22, 26, 36, 14, 24, 24, 22]


def _normalizar_tipo(tipo: Optional[str], tipo_movimiento: Optional[str]) -> Optional[str]:
    value = (tipo_movimiento or tipo or "").strip().upper()
    if not value:
        return None
    if value.startswith("INGRESO"):
        return "INGRESO"
    if value.startswith("SALIDA"):
        return "SALIDA"
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="tipo debe ser INGRESO o SALIDA",
    )


def _normalizar_fechas(
    fecha: Optional[date],
    fecha_desde: Optional[date],
    fecha_hasta: Optional[date],
    fecha_inicio: Optional[date],
    fecha_fin: Optional[date],
) -> tuple[Optional[date], Optional[date], Optional[date]]:
    fecha_desde_final = fecha_desde or fecha_inicio
    fecha_hasta_final = fecha_hasta or fecha_fin

    if fecha_desde_final and fecha_hasta_final and fecha_desde_final > fecha_hasta_final:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="fecha_desde no puede ser mayor que fecha_hasta",
        )

    return fecha, fecha_desde_final, fecha_hasta_final


def obtener_resumen_movimientos(
    db: Session,
    tipo: Optional[str] = None,
    tipo_movimiento: Optional[str] = None,
    fecha: Optional[date] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
) -> dict:
    tipo_normalizado = _normalizar_tipo(tipo=tipo, tipo_movimiento=tipo_movimiento)
    fecha_filtro, fecha_desde_filtro, fecha_hasta_filtro = _normalizar_fechas(
        fecha=fecha,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )

    return get_resumen_movimientos(
        db=db,
        tipo=tipo_normalizado,
        fecha=fecha_filtro,
        fecha_desde=fecha_desde_filtro,
        fecha_hasta=fecha_hasta_filtro,
    )


def listar_historial_movimientos(
    db: Session,
    tipo: Optional[str] = None,
    tipo_movimiento: Optional[str] = None,
    fecha: Optional[date] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
) -> dict:
    tipo_normalizado = _normalizar_tipo(tipo=tipo, tipo_movimiento=tipo_movimiento)
    fecha_filtro, fecha_desde_filtro, fecha_hasta_filtro = _normalizar_fechas(
        fecha=fecha,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )

    effective_limit = limit if limit is not None else (page_size if page_size is not None else 20)
    effective_limit = max(1, min(int(effective_limit), 500))

    if skip is None:
        effective_page = max(1, int(page or 1))
        effective_skip = (effective_page - 1) * effective_limit
    else:
        effective_skip = max(0, int(skip))
        effective_page = (effective_skip // effective_limit) + 1

    registros, total = list_movimientos_historial(
        db=db,
        tipo=tipo_normalizado,
        fecha=fecha_filtro,
        fecha_desde=fecha_desde_filtro,
        fecha_hasta=fecha_hasta_filtro,
        skip=effective_skip,
        limit=effective_limit,
    )

    data = [
        {
            "id": int(registro.movimiento_id),
            "movimiento_id": int(registro.movimiento_id),
            "tipo_movimiento": registro.tipo_movimiento,
            "fecha_registro": registro.fecha_registro,
            "equipo_id": int(registro.equipo_id),
            "serial": registro.serial,
            "equipo_nombre": registro.equipo_nombre,
            "equipo_descripcion": registro.equipo_descripcion,
            "estado": registro.estado,
            "usuario_nombre": registro.usuario_nombre,
            "estudiante_nombre": registro.estudiante_nombre,
            "estudiante_documento": registro.estudiante_documento,
        }
        for registro in registros
    ]

    total_pages = max(1, (total + effective_limit - 1) // effective_limit)
    return {
        "data": data,
        "meta": {
            "total": total,
            "skip": effective_skip,
            "limit": effective_limit,
            "has_next": effective_skip + len(data) < total,
        },
        "total": total,
        "page": effective_page,
        "total_pages": total_pages,
    }


def exportar_historial_movimientos_csv(
    db: Session,
    tipo: Optional[str] = None,
    tipo_movimiento: Optional[str] = None,
    fecha: Optional[date] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
) -> str:
    tipo_normalizado = _normalizar_tipo(tipo=tipo, tipo_movimiento=tipo_movimiento)
    fecha_filtro, fecha_desde_filtro, fecha_hasta_filtro = _normalizar_fechas(
        fecha=fecha,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )

    registros = list_movimientos_historial_for_export(
        db=db,
        tipo=tipo_normalizado,
        fecha=fecha_filtro,
        fecha_desde=fecha_desde_filtro,
        fecha_hasta=fecha_hasta_filtro,
    )

    output = StringIO(newline="")
    writer = csv.writer(output, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(EXPORT_HEADERS)
    for registro in registros:
        writer.writerow(_serialize_registro_for_export(registro))

    # Excel en configuraciones regionales es-CO suele usar ';' como separador.
    # 'sep=;' fuerza la separacion por columnas al abrir el archivo.
    csv_content = output.getvalue()
    return "\ufeffsep=;\n" + csv_content


def exportar_historial_movimientos_xlsx(
    db: Session,
    tipo: Optional[str] = None,
    tipo_movimiento: Optional[str] = None,
    fecha: Optional[date] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
) -> tuple[str, bytes]:
    tipo_normalizado = _normalizar_tipo(tipo=tipo, tipo_movimiento=tipo_movimiento)
    fecha_filtro, fecha_desde_filtro, fecha_hasta_filtro = _normalizar_fechas(
        fecha=fecha,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )

    registros = list_movimientos_historial_for_export(
        db=db,
        tipo=tipo_normalizado,
        fecha=fecha_filtro,
        fecha_desde=fecha_desde_filtro,
        fecha_hasta=fecha_hasta_filtro,
    )

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Historial Movimientos"
    worksheet.append(EXPORT_HEADERS)

    for registro in registros:
        worksheet.append(_serialize_registro_for_export(registro))

    header_fill = PatternFill(fill_type="solid", fgColor="166534")
    header_font = Font(color="FFFFFF", bold=True)
    for column_index, _ in enumerate(EXPORT_HEADERS, start=1):
        cell = worksheet.cell(row=1, column=column_index)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        worksheet.column_dimensions[get_column_letter(column_index)].width = EXPORT_COLUMN_WIDTHS[column_index - 1]

    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = f"A1:{get_column_letter(len(EXPORT_HEADERS))}{max(1, worksheet.max_row)}"
    worksheet.sheet_view.zoomScale = 110

    for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row):
        for cell in row:
            cell.alignment = Alignment(vertical="center", wrap_text=False)

    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return "reporte-movimientos.xlsx", output.read()


def _serialize_registro_for_export(registro) -> list[str | int]:
    return [
        int(registro.movimiento_id),
        registro.tipo_movimiento,
        registro.fecha_registro.strftime("%Y-%m-%d %H:%M:%S") if registro.fecha_registro else "",
        int(registro.equipo_id),
        registro.serial or "",
        registro.equipo_nombre or "",
        registro.equipo_descripcion or "",
        registro.estado or "",
        registro.usuario_nombre or "",
        registro.estudiante_nombre or "",
        registro.estudiante_documento or "",
    ]
