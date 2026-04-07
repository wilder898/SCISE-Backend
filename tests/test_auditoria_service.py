from datetime import date
import pytest
from fastapi import HTTPException
from app.services import auditoria_service


class UsuarioFake:
    def __init__(self, nombre: str):
        self.nombre = nombre


class RegistroAuditoriaFake:
    def __init__(self):
        from datetime import datetime

        self.id = 1
        self.usuario_id = 7
        self.usuario = UsuarioFake("Admin SENA")
        self.evento = "REGISTRAR_SALIDA_BATCH"
        self.tipo_auditoria = "INSERT"
        self.tabla_id = 99
        self.valor_anterior = "INGRESADO"
        self.valor_nuevo = "RETIRADO"
        self.url = "/api/v1/movimientos/salidas"
        self.fecha_novedad = datetime(2026, 3, 28, 10, 15, 0)


def test_listar_auditoria_ok(monkeypatch):
    captured = {}

    def fake_list_auditoria_filtrada(
        db,
        modulo,
        actor_id,
        fecha_desde,
        fecha_hasta,
        skip,
        limit,
    ):
        captured["db"] = db
        captured["modulo"] = modulo
        captured["actor_id"] = actor_id
        captured["fecha_desde"] = fecha_desde
        captured["fecha_hasta"] = fecha_hasta
        captured["skip"] = skip
        captured["limit"] = limit
        return [RegistroAuditoriaFake()], 3

    monkeypatch.setattr(
        auditoria_service,
        "list_auditoria_filtrada",
        fake_list_auditoria_filtrada,
    )

    resultado = auditoria_service.listar_auditoria(
        db=object(),
        modulo=" movimientos ",
        actor_id=7,
        fecha_desde=date(2026, 3, 1),
        fecha_hasta=date(2026, 3, 31),
        skip=0,
        limit=1,
    )

    assert captured["modulo"] == "movimientos"
    assert captured["actor_id"] == 7
    assert captured["fecha_desde"].hour == 0
    assert captured["fecha_hasta"].hour == 23
    assert captured["skip"] == 0
    assert captured["limit"] == 1
    assert resultado["data"][0]["actor_nombre"] == "Admin SENA"
    assert resultado["meta"] == {
        "total": 3,
        "skip": 0,
        "limit": 1,
        "has_next": True,
    }


def test_listar_auditoria_fechas_invalidas_lanza_400():
    with pytest.raises(HTTPException) as exc_info:
        auditoria_service.listar_auditoria(
            db=object(),
            fecha_desde=date(2026, 4, 1),
            fecha_hasta=date(2026, 3, 1),
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "fecha_desde no puede ser mayor que fecha_hasta"
