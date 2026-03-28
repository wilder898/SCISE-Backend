import pytest
from fastapi import HTTPException

from app.services import usuario_service
from app.schemas.usuario import (
    UsuarioSistemaCreate,
    UsuarioSistemaEstadoUpdate,
    UsuarioSistemaPatch,
)


class RolFake:
    def __init__(self, nombre: str):
        self.nombre = nombre


class UsuarioFake:
    def __init__(
        self,
        usuario_id: int,
        documento: str,
        nombre: str,
        correo: str,
        area: str,
        estado: str,
        rol_id: int,
        rol_nombre: str,
    ):
        self.id = usuario_id
        self.documento = documento
        self.nombre = nombre
        self.correo = correo
        self.area = area
        self.estado = estado
        self.rol_id = rol_id
        self.rol = RolFake(rol_nombre)


def test_listar_usuarios_sistema_construye_data_y_meta(monkeypatch):
    usuarios = [
        UsuarioFake(
            usuario_id=1,
            documento="1001",
            nombre="Admin SENA",
            correo="admin@sena.edu.co",
            area="Administracion",
            estado="ACTIVO",
            rol_id=1,
            rol_nombre="Administrador",
        ),
        UsuarioFake(
            usuario_id=2,
            documento="1002",
            nombre="Operador SCISE",
            correo="operador@sena.edu.co",
            area="Seguridad",
            estado="ACTIVO",
            rol_id=2,
            rol_nombre="Usuario",
        ),
    ]

    def fake_list_usuarios_filtrados(db, q, rol, estado, skip, limit):
        assert db is not None
        assert q == "sena"
        assert rol == "Administrador"
        assert estado == "ACTIVO"
        assert skip == 0
        assert limit == 2
        return usuarios, 3

    monkeypatch.setattr(
        usuario_service,
        "list_usuarios_filtrados",
        fake_list_usuarios_filtrados,
    )

    resultado = usuario_service.listar_usuarios_sistema(
        db=object(),
        q="  sena ",
        rol=" Administrador ",
        estado="activo",
        skip=0,
        limit=2,
    )

    assert len(resultado["data"]) == 2
    assert resultado["data"][0]["rol"] == "Administrador"
    assert resultado["meta"] == {
        "total": 3,
        "skip": 0,
        "limit": 2,
        "has_next": True,
    }


def test_listar_usuarios_sistema_estado_invalido_lanza_400():
    with pytest.raises(HTTPException) as exc_info:
        usuario_service.listar_usuarios_sistema(
            db=object(),
            estado="SUSPENDIDO",
            skip=0,
            limit=20,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Estado inválido. Use ACTIVO o INACTIVO"


def test_crear_usuario_sistema_ok(monkeypatch):
    datos = UsuarioSistemaCreate(
        documento=" 123456 ",
        nombre=" Nuevo Usuario ",
        correo="NUEVO@SENA.EDU.CO",
        area=" Seguridad ",
        contrasena="Secret123",
        rol_id=2,
        estado="activo",
    )

    class RolCreado:
        nombre = "Usuario"

    class UsuarioCreado:
        id = 10
        documento = "123456"
        nombre = "Nuevo Usuario"
        correo = "nuevo@sena.edu.co"
        area = "Seguridad"
        estado = "ACTIVO"
        rol_id = 2
        rol = RolCreado()

    monkeypatch.setattr(usuario_service, "get_usuario_by_documento", lambda _db, _d: None)
    monkeypatch.setattr(usuario_service, "get_usuario_by_correo", lambda _db, _c: None)
    monkeypatch.setattr(usuario_service, "get_rol_by_id", lambda _db, _id: RolCreado())
    monkeypatch.setattr(usuario_service, "hash_password", lambda raw: f"hashed:{raw}")

    captured = {}

    def fake_create_usuario(_db, usuario):
        captured["documento"] = usuario.documento
        captured["nombre"] = usuario.nombre
        captured["correo"] = usuario.correo
        captured["area"] = usuario.area
        captured["estado"] = usuario.estado
        captured["contrasena"] = usuario.contrasena
        captured["rol_id"] = usuario.rol_id
        return UsuarioCreado()

    monkeypatch.setattr(usuario_service, "create_usuario", fake_create_usuario)

    resultado = usuario_service.crear_usuario_sistema(db=object(), datos=datos)

    assert captured == {
        "documento": "123456",
        "nombre": "Nuevo Usuario",
        "correo": "nuevo@sena.edu.co",
        "area": "Seguridad",
        "estado": "ACTIVO",
        "contrasena": "hashed:Secret123",
        "rol_id": 2,
    }
    assert resultado["id"] == 10
    assert resultado["rol"] == "Usuario"


def test_crear_usuario_sistema_documento_duplicado_lanza_409(monkeypatch):
    datos = UsuarioSistemaCreate(
        documento="123456",
        nombre="Usuario Duplicado",
        correo="dup@sena.edu.co",
        area="Seguridad",
        contrasena="Secret123",
        rol_id=2,
        estado="ACTIVO",
    )

    monkeypatch.setattr(usuario_service, "get_usuario_by_documento", lambda _db, _d: object())

    with pytest.raises(HTTPException) as exc_info:
        usuario_service.crear_usuario_sistema(db=object(), datos=datos)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Ya existe un usuario con ese documento"


def test_crear_usuario_sistema_rol_invalido_lanza_400(monkeypatch):
    datos = UsuarioSistemaCreate(
        documento="123456",
        nombre="Usuario Sin Rol",
        correo="norol@sena.edu.co",
        area="Seguridad",
        contrasena="Secret123",
        rol_id=999,
        estado="ACTIVO",
    )

    monkeypatch.setattr(usuario_service, "get_usuario_by_documento", lambda _db, _d: None)
    monkeypatch.setattr(usuario_service, "get_usuario_by_correo", lambda _db, _c: None)
    monkeypatch.setattr(usuario_service, "get_rol_by_id", lambda _db, _id: None)

    with pytest.raises(HTTPException) as exc_info:
        usuario_service.crear_usuario_sistema(db=object(), datos=datos)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Rol inválido"


def test_actualizar_usuario_sistema_ok(monkeypatch):
    class UsuarioExistente:
        id = 15
        documento = "1010"
        nombre = "Usuario Antiguo"
        correo = "anterior@sena.edu.co"
        area = "Operaciones"
        estado = "ACTIVO"
        rol_id = 2
        rol = RolFake("Usuario")

    class RolAdmin:
        nombre = "Administrador"

    usuario_existente = UsuarioExistente()
    datos = UsuarioSistemaPatch(
        nombre=" Nuevo Nombre ",
        correo="NUEVO@SENA.EDU.CO",
        area=" Administracion ",
        rol_id=1,
    )

    monkeypatch.setattr(usuario_service, "get_usuario_by_id", lambda _db, _id: usuario_existente)
    monkeypatch.setattr(usuario_service, "get_usuario_by_correo", lambda _db, _c: None)
    monkeypatch.setattr(usuario_service, "get_rol_by_id", lambda _db, _id: RolAdmin())
    monkeypatch.setattr(usuario_service, "update_usuario", lambda _db, usuario: usuario)

    resultado = usuario_service.actualizar_usuario_sistema(
        db=object(),
        usuario_id=15,
        datos=datos,
    )

    assert usuario_existente.nombre == "Nuevo Nombre"
    assert usuario_existente.correo == "nuevo@sena.edu.co"
    assert usuario_existente.area == "Administracion"
    assert usuario_existente.rol_id == 1
    assert usuario_existente.rol.nombre == "Administrador"
    assert resultado["id"] == 15
    assert resultado["rol"] == "Administrador"


def test_actualizar_usuario_sistema_payload_vacio_lanza_400(monkeypatch):
    class UsuarioExistente:
        id = 1
        documento = "1001"
        nombre = "Admin"
        correo = "admin@sena.edu.co"
        area = "Admin"
        estado = "ACTIVO"
        rol_id = 1
        rol = RolFake("Administrador")

    monkeypatch.setattr(usuario_service, "get_usuario_by_id", lambda _db, _id: UsuarioExistente())

    with pytest.raises(HTTPException) as exc_info:
        usuario_service.actualizar_usuario_sistema(
            db=object(),
            usuario_id=1,
            datos=UsuarioSistemaPatch(),
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Debe enviar al menos un campo para actualizar"


def test_actualizar_usuario_sistema_no_encontrado_lanza_404(monkeypatch):
    monkeypatch.setattr(usuario_service, "get_usuario_by_id", lambda _db, _id: None)

    with pytest.raises(HTTPException) as exc_info:
        usuario_service.actualizar_usuario_sistema(
            db=object(),
            usuario_id=999,
            datos=UsuarioSistemaPatch(nombre="Nuevo"),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Usuario no encontrado"


def test_actualizar_usuario_sistema_correo_duplicado_lanza_409(monkeypatch):
    class UsuarioExistente:
        id = 15
        documento = "1010"
        nombre = "Usuario Antiguo"
        correo = "anterior@sena.edu.co"
        area = "Operaciones"
        estado = "ACTIVO"
        rol_id = 2
        rol = RolFake("Usuario")

    class UsuarioDuplicado:
        id = 16

    monkeypatch.setattr(usuario_service, "get_usuario_by_id", lambda _db, _id: UsuarioExistente())
    monkeypatch.setattr(
        usuario_service,
        "get_usuario_by_correo",
        lambda _db, _c: UsuarioDuplicado(),
    )

    with pytest.raises(HTTPException) as exc_info:
        usuario_service.actualizar_usuario_sistema(
            db=object(),
            usuario_id=15,
            datos=UsuarioSistemaPatch(correo="duplicado@sena.edu.co"),
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Ya existe un usuario con ese correo"


def test_actualizar_estado_usuario_sistema_ok(monkeypatch):
    usuario = UsuarioFake(
        usuario_id=20,
        documento="2001",
        nombre="Usuario Estado",
        correo="estado@sena.edu.co",
        area="Seguridad",
        estado="ACTIVO",
        rol_id=2,
        rol_nombre="Usuario",
    )

    monkeypatch.setattr(usuario_service, "get_usuario_by_id", lambda _db, _id: usuario)
    monkeypatch.setattr(usuario_service, "update_usuario", lambda _db, u: u)

    resultado = usuario_service.actualizar_estado_usuario_sistema(
        db=object(),
        usuario_id=20,
        datos=UsuarioSistemaEstadoUpdate(estado="inactivo"),
    )

    assert usuario.estado == "INACTIVO"
    assert resultado["estado"] == "INACTIVO"


def test_actualizar_estado_usuario_sistema_invalido_lanza_400(monkeypatch):
    usuario = UsuarioFake(
        usuario_id=20,
        documento="2001",
        nombre="Usuario Estado",
        correo="estado@sena.edu.co",
        area="Seguridad",
        estado="ACTIVO",
        rol_id=2,
        rol_nombre="Usuario",
    )
    monkeypatch.setattr(usuario_service, "get_usuario_by_id", lambda _db, _id: usuario)

    with pytest.raises(HTTPException) as exc_info:
        usuario_service.actualizar_estado_usuario_sistema(
            db=object(),
            usuario_id=20,
            datos=UsuarioSistemaEstadoUpdate(estado="SUSPENDIDO"),
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Estado inválido. Use ACTIVO o INACTIVO"


def test_actualizar_estado_usuario_sistema_no_encontrado_lanza_404(monkeypatch):
    monkeypatch.setattr(usuario_service, "get_usuario_by_id", lambda _db, _id: None)

    with pytest.raises(HTTPException) as exc_info:
        usuario_service.actualizar_estado_usuario_sistema(
            db=object(),
            usuario_id=999,
            datos=UsuarioSistemaEstadoUpdate(estado="ACTIVO"),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Usuario no encontrado"
