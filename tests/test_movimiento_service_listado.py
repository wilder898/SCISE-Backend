from datetime import date, datetime
import pytest
from fastapi import HTTPException
from app.services import movimiento_service


class EquipoFake:
    def __init__(self, serial: str, nombre: str = "Equipo Demo"):
        self.serial = serial
        self.nombre = nombre


class EstudianteFake:
    def __init__(self, nombre: str, documento: str):
        self.nombre = nombre
        self.documento = documento


class MovimientoFake:
    def __init__(
        self,
        movimiento_id: int,
        tipo: str,
        fecha_registro: datetime,
        usuario_id: int,
        equipo_id: int,
        estudiante_id: int,
        serial: str,
    ):
        self.id = movimiento_id
        self.tipo_movimiento = tipo
        self.fecha_registro = fecha_registro
        self.usuario_id = usuario_id
        self.equipo_id = equipo_id
        self.estudiante_id = estudiante_id
        self.equipo = EquipoFake(serial=serial)
        self.estudiante = EstudianteFake(nombre="Aprendiz Uno", documento="123456789")


def test_listar_movimientos_ok(monkeypatch):
    captured = {}

    def fake_list_movimientos_filtrados(
        db,
        tipo,
        fecha,
        estudiante_id,
        serial,
        skip,
        limit,
    ):
        captured["tipo"] = tipo
        captured["fecha"] = fecha
        captured["estudiante_id"] = estudiante_id
        captured["serial"] = serial
        captured["skip"] = skip
        captured["limit"] = limit
        return (
            [
                MovimientoFake(
                    movimiento_id=10,
                    tipo="INGRESO",
                    fecha_registro=datetime(2026, 3, 28, 9, 30),
                    usuario_id=2,
                    equipo_id=5,
                    estudiante_id=7,
                    serial="SER-001",
                )
            ],
            3,
        )

    monkeypatch.setattr(
        movimiento_service,
        "list_movimientos_filtrados",
        fake_list_movimientos_filtrados,
    )

    resultado = movimiento_service.listar_movimientos(
        db=object(),
        tipo="ingreso",
        fecha=date(2026, 3, 28),
        estudiante_id=7,
        serial=" SER-001 ",
        skip=0,
        limit=2,
    )

    assert captured["tipo"] == "INGRESO"
    assert captured["fecha"] == date(2026, 3, 28)
    assert captured["estudiante_id"] == 7
    assert captured["serial"] == "SER-001"
    assert captured["skip"] == 0
    assert captured["limit"] == 2
    assert resultado["total"] == 3
    assert resultado["page"] == 1
    assert resultado["total_pages"] == 2
    assert resultado["meta"]["has_next"] is True
    assert resultado["data"][0]["serial"] == "SER-001"


def test_listar_movimientos_tipo_invalido_lanza_400():
    with pytest.raises(HTTPException) as exc_info:
        movimiento_service.listar_movimientos(
            db=object(),
            tipo="cualquier-cosa",
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "tipo debe ser INGRESO o SALIDA"


def test_obtener_movimiento_por_id_ok(monkeypatch):
    def fake_get_movimiento_by_id(db, movimiento_id):
        return MovimientoFake(
            movimiento_id=movimiento_id,
            tipo="SALIDA",
            fecha_registro=datetime(2026, 3, 28, 11, 0),
            usuario_id=3,
            equipo_id=8,
            estudiante_id=9,
            serial="SER-999",
        )

    monkeypatch.setattr(
        movimiento_service,
        "get_movimiento_by_id",
        fake_get_movimiento_by_id,
    )

    resultado = movimiento_service.obtener_movimiento_por_id(
        db=object(),
        movimiento_id=99,
    )

    assert resultado["id"] == 99
    assert resultado["tipo_movimiento"] == "SALIDA"
    assert resultado["serial"] == "SER-999"
    assert resultado["estudiante_nombre"] == "Aprendiz Uno"
    assert resultado["estudiante_documento"] == "123456789"


def test_obtener_movimiento_por_id_no_encontrado_lanza_404(monkeypatch):
    monkeypatch.setattr(
        movimiento_service,
        "get_movimiento_by_id",
        lambda db, movimiento_id: None,
    )

    with pytest.raises(HTTPException) as exc_info:
        movimiento_service.obtener_movimiento_por_id(
            db=object(),
            movimiento_id=111,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Movimiento no encontrado"
