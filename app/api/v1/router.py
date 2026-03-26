"""
Agrupador de todos los sub-routers de la versión 1 de la API.
Para agregar un nuevo módulo: importar su router y llamar api_router.include_router().
"""
from fastapi import APIRouter
from app.api.v1 import auth, estudiantes

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(estudiantes.router)

# Aquí se agregarán los routers de los demás módulos cuando estén implementados:
# from app.api.v1 import usuarios, estudiantes, equipos, movimientos
# api_router.include_router(usuarios.router)
# api_router.include_router(equipos.router)
# api_router.include_router(movimientos.router)
