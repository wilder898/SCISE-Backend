from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
import app.db.all_models  # noqa: F401 — registra todos los mappers de SQLAlchemy
from app.api.v1.router import api_router
from app.middlewares.logging_middleware import LoggingMiddleware

app = FastAPI(
    title="SCISE API",
    version="1.0.0",
    description="Sistema de Control de Ingreso y Salida de Equipos",
)

# --- Middlewares ---
# El orden importa en Starlette: el último añadido es el primero en ejecutarse.
# CORS debe estar antes que Logging para que las preflight requests también sean logeadas.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)

# --- Routers ---
app.include_router(api_router)


@app.get("/health", tags=["Sistema"])
def health_check():
    """Endpoint de verificación de disponibilidad."""
    return {
        "status": "ok",
        "system": "SCISE",
        "environment": settings.environment,
    }