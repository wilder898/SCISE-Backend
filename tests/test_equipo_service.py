from datetime import datetime
import pytest
from fastapi import HTTPException

from app.services import equipo_service


class EstudianteFake:
    def __init__(self, estudiante_id: int, nombre: str, documento: str):
        self.id = estudiante_id
        self.nombre = nombre
        self.documento = documento


class EquipoFake:
    def __init__(
        self,
        equipo_id: int,
        serial: str,
        nombre: str,
        estado: str,
        tipo_equipo: str | None,
        estudiante: EstudianteFake,
    ):
        self.id = equipo_id
        self.codigo_barras_equipo = serial
        self.serial = serial
        self.nombre = nombre
        self.descripcion = "Equipo de prueba"
        self.tipo_equipo = tipo_equipo
        self.estado = estado
        self.fecha_registro = datetime(2026, 4, 2, 10, 0, 0)
        self.estudiante_id = estudiante.id
        self.estudiante = estudiante


def test_listar_equipos_sistema_construye_data_y_meta(monkeypatch):
    captured = {}
    estudiante = EstudianteFake(
        estudiante_id=7,
        nombre="Aprendiz SENA",
        documento="123456789",
    )
    equipos = [
        EquipoFake(
            equipo_id=15,
            serial="LAP-001",
            nombre="Lenovo T14",
            estado="DISPONIBLE",
            tipo_equipo="Portátil",
            estudiante=estudiante,
        )
    ]

    def fake_list_equipos_filtrados(db, q, tipo, estado, skip, limit):
        captured["db"] = db
        captured["q"] = q
        captured["tipo"] = tipo
        captured["estado"] = estado
        captured["skip"] = skip
        captured["limit"] = limit
        return equipos, 3

    monkeypatch.setattr(
        equipo_service,
        "list_equipos_filtrados",
        fake_list_equipos_filtrados,
    )

    resultado = equipo_service.listar_equipos_sistema(
        db=object(),
        q=" lenovo ",
        tipo=" Portátil ",
        estado="disponible",
        skip=0,
        limit=1,
    )

    assert captured["q"] == "lenovo"
    assert captured["tipo"] == "Portátil"
    assert captured["estado"] == "DISPONIBLE"
    assert captured["skip"] == 0
    assert captured["limit"] == 1
    assert resultado["data"][0]["serial"] == "LAP-001"
    assert resultado["data"][0]["estudiante_nombre"] == "Aprendiz SENA"
    assert resultado["data"][0]["estudiante_documento"] == "123456789"
    assert resultado["meta"] == {
        "total": 3,
        "skip": 0,
        "limit": 1,
        "has_next": True,
    }


def test_listar_equipos_sistema_estado_invalido_lanza_400():
    with pytest.raises(HTTPException) as exc_info:
        equipo_service.listar_equipos_sistema(
            db=object(),
            estado="EN_MANTENIMIENTO",
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Estado inválido. Use DISPONIBLE, INGRESADO o RETIRADO"
