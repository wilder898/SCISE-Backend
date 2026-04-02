import pytest
from fastapi import HTTPException

from app.core.deps import require_role


class RolFake:
    def __init__(self, nombre: str):
        self.nombre = nombre


class UsuarioFake:
    def __init__(self, rol_nombre: str):
        self.rol = RolFake(rol_nombre)


def test_require_role_acepta_mismo_rol_con_diferente_case_y_tildes():
    checker = require_role("Administrador")
    usuario = UsuarioFake("ADMINISTRADOR")

    resultado = checker(usuario=usuario)

    assert resultado is usuario


def test_require_role_rechaza_rol_distinto():
    checker = require_role("Administrador")
    usuario = UsuarioFake("Seguridad")

    with pytest.raises(HTTPException) as exc_info:
        checker(usuario=usuario)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Requiere rol: Administrador"
