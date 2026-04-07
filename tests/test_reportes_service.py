from datetime import date, datetime
from io import BytesIO
import pytest
from fastapi import HTTPException
from openpyxl import load_workbook
from app.services import reportes_service


class RegistroReporteFake:
    def __init__(
        self,
        movimiento_id: int,
        tipo_movimiento: str = "INGRESO",
        serial: str = "SER-001",
    ):
        self.movimiento_id = movimiento_id
        self.tipo_movimiento = tipo_movimiento
        self.fecha_registro = datetime(2026, 3, 28, 9, 45, 0)
        self.equipo_id = 5
        self.serial = serial
        self.equipo_nombre = "Portatil Lenovo"
        self.equipo_descripcion = "ThinkPad T14"
        self.estado = "INGRESADO"
        self.usuario_nombre = "Administrador SCISE"
        self.estudiante_nombre = "Aprendiz Uno"
        self.estudiante_documento = "10000001"


def test_obtener_resumen_movimientos_ok(monkeypatch):
    captured = {}

    def fake_get_resumen_movimientos(db, tipo, fecha, fecha_desde, fecha_hasta):
        captured["tipo"] = tipo
        captured["fecha"] = fecha
        captured["fecha_desde"] = fecha_desde
        captured["fecha_hasta"] = fecha_hasta
        return {
            "total_equipos": 10,
            "equipos_en_instalacion": 7,
            "equipos_fuera_instalacion": 3,
            "movimientos_hoy": 4,
            "inside_pct": 70,
            "outside_pct": 30,
        }

    monkeypatch.setattr(
        reportes_service,
        "get_resumen_movimientos",
        fake_get_resumen_movimientos,
    )

    resultado = reportes_service.obtener_resumen_movimientos(
        db=object(),
        tipo=" ingreso ",
        fecha_desde=date(2026, 3, 1),
        fecha_hasta=date(2026, 3, 31),
    )

    assert captured["tipo"] == "INGRESO"
    assert captured["fecha"] is None
    assert captured["fecha_desde"] == date(2026, 3, 1)
    assert captured["fecha_hasta"] == date(2026, 3, 31)
    assert resultado["inside_pct"] == 70


def test_listar_historial_movimientos_ok(monkeypatch):
    captured = {}

    def fake_list_movimientos_historial(
        db,
        tipo,
        fecha,
        fecha_desde,
        fecha_hasta,
        skip,
        limit,
    ):
        captured["tipo"] = tipo
        captured["fecha"] = fecha
        captured["fecha_desde"] = fecha_desde
        captured["fecha_hasta"] = fecha_hasta
        captured["skip"] = skip
        captured["limit"] = limit
        return [RegistroReporteFake(movimiento_id=20)], 3

    monkeypatch.setattr(
        reportes_service,
        "list_movimientos_historial",
        fake_list_movimientos_historial,
    )

    resultado = reportes_service.listar_historial_movimientos(
        db=object(),
        tipo="salida",
        fecha=date(2026, 3, 28),
        page=2,
        page_size=1,
    )

    assert captured["tipo"] == "SALIDA"
    assert captured["fecha"] == date(2026, 3, 28)
    assert captured["skip"] == 1
    assert captured["limit"] == 1
    assert resultado["total"] == 3
    assert resultado["page"] == 2
    assert resultado["meta"]["has_next"] is True
    assert resultado["data"][0]["movimiento_id"] == 20


def test_listar_historial_movimientos_fechas_invalidas_lanza_400():
    with pytest.raises(HTTPException) as exc_info:
        reportes_service.listar_historial_movimientos(
            db=object(),
            fecha_desde=date(2026, 4, 1),
            fecha_hasta=date(2026, 3, 1),
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "fecha_desde no puede ser mayor que fecha_hasta"


def test_exportar_historial_movimientos_csv_formato_excel(monkeypatch):
    monkeypatch.setattr(
        reportes_service,
        "list_movimientos_historial_for_export",
        lambda **kwargs: [RegistroReporteFake(movimiento_id=30, tipo_movimiento="SALIDA")],
    )

    csv_content = reportes_service.exportar_historial_movimientos_csv(
        db=object(),
        tipo="SALIDA",
    )

    assert csv_content.startswith("\ufeffsep=;\n")
    assert "Movimiento ID;Tipo Movimiento;Fecha Registro" in csv_content
    assert "30;SALIDA;" in csv_content


def test_exportar_historial_movimientos_xlsx_ok(monkeypatch):
    monkeypatch.setattr(
        reportes_service,
        "list_movimientos_historial_for_export",
        lambda **kwargs: [RegistroReporteFake(movimiento_id=40, tipo_movimiento="INGRESO")],
    )

    filename, xlsx_bytes = reportes_service.exportar_historial_movimientos_xlsx(
        db=object(),
        tipo="INGRESO",
    )

    assert filename.endswith(".xlsx")
    assert isinstance(xlsx_bytes, bytes)
    assert len(xlsx_bytes) > 0

    workbook = load_workbook(BytesIO(xlsx_bytes))
    sheet = workbook["Historial Movimientos"]
    assert sheet["A1"].value == "Movimiento ID"
    assert sheet["B1"].value == "Tipo Movimiento"
    assert sheet["A2"].value == 40
    assert sheet["B2"].value == "INGRESO"
