from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title="SCISE API",
    version="1.0.0",
    description="Sistema de Control de Ingreso y Salida de Equipos"
)

# Configurar CORS para frontend Astro
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """Endpoint de verificación de disponibilidad"""
    return {
        "status": "ok",
        "system": "SCISE",
        "environment": settings.environment
    }