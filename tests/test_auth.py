import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_login_success():
    """Test login con credenciales correctas"""
    response = client.post("/api/v1/auth/login", json={
        "correo": "admin@scise.sena.edu.co",
        "contrasena": "CambiarEstoInmediatamente123!"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password():
    """Test login con contraseña incorrecta"""
    response = client.post("/api/v1/auth/login", json={
        "correo": "admin@scise.sena.edu.co",
        "contrasena": "incorrecta"
    })
    assert response.status_code == 401

def test_protected_route_without_token():
    """Test acceso sin token a ruta protegida"""
    response = client.get("/api/v1/movimientos")
    assert response.status_code == 401
