# SCISE-Backend

API de SCISE construida con FastAPI, SQLAlchemy y Alembic para autenticacion, gestion de estudiantes y equipos, movimientos de ingreso y salida, reportes, usuarios del sistema y auditoria.

## Modulos

- Auth para frontend y Swagger
- Estudiantes
- Equipos
- Movimientos
- Dashboard
- Reportes
- Usuarios del sistema
- Auditoria

Adicionalmente:

- CORS habilitado via `ALLOWED_ORIGINS`
- logging middleware activo
- migraciones Alembic incluidas

## Arquitectura por capas

```text
app/
  api/v1/          # Rutas HTTP
  controllers/     # Orquestacion de casos de uso
  services/        # Reglas de negocio
  repositories/    # Acceso a datos con SQLAlchemy
  models/          # Modelos ORM
  schemas/         # Contratos request/response
  core/            # Configuracion, seguridad, dependencias, logger
  db/              # Session, base, seed, registro de modelos
  middlewares/     # Middleware HTTP
  utils/           # JWT, password y utilidades
```

## Tecnologias

- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic v2
- PostgreSQL
- `python-jose` para JWT
- `passlib` y `bcrypt` para contrasenas
- `openpyxl` para exportacion XLSX
- `pytest` para pruebas

## Requisitos

- Python 3.12 recomendado
- PostgreSQL 14+
- Entorno virtual `.venv`

## Configuracion local

1. Crear y activar entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3. Copiar `.env.example` o usar el `.env.backend.example` de la raiz del proyecto y renombrarlo a `.env`

Variables principales:

| Variable | Descripcion |
| --- | --- |
| `DATABASE_URL` | Conexion PostgreSQL |
| `SECRET_KEY` | Clave JWT |
| `ALGORITHM` | Algoritmo JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Minutos de expiracion del token |
| `APP_HOST` / `APP_PORT` | Host y puerto del servidor |
| `DEBUG` | Modo debug |
| `ALLOWED_ORIGINS` | Origenes CORS separados por coma |
| `ADMIN_NOMBRE` / `ADMIN_CORREO` / `ADMIN_DOCUMENTO` / `ADMIN_PASSWORD` | Datos del admin inicial |
| `ENVIRONMENT` | `development`, `testing`, `production` |

4. Ejecutar migraciones:

```powershell
alembic upgrade head
```

5. Ejecutar seed inicial:

```powershell
python -m app.db.seed
```

## Ejecucion

Levantar API en desarrollo:

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Documentacion interactiva:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health: `http://localhost:8000/health`

## Endpoints principales

### Auth

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/token`
- `POST /api/v1/auth/logout`

### Estudiantes

- `GET /api/v1/estudiantes`
- `GET /api/v1/estudiantes/by-documento/{documento}`
- `GET /api/v1/estudiantes/{estudiante_id}/equipos`
- `POST /api/v1/estudiantes`
- `PATCH /api/v1/estudiantes/{estudiante_id}`
- `PATCH /api/v1/estudiantes/{estudiante_id}/estado` (Administrador)

### Equipos

- `GET /api/v1/equipos`
- `POST /api/v1/equipos`
- `PATCH /api/v1/equipos/{equipo_id}`
- `DELETE /api/v1/equipos/{equipo_id}`

### Movimientos

- `GET /api/v1/movimientos`
- `POST /api/v1/movimientos/ingresos`
- `GET /api/v1/movimientos/activos/estudiante/{estudiante_id}`
- `POST /api/v1/movimientos/salidas`
- `GET /api/v1/movimientos/{movimiento_id}`

### Reportes y Dashboard

- `GET /api/v1/reportes/movimientos/resumen` (Administrador)
- `GET /api/v1/reportes/movimientos/historial` (Administrador)
- `GET /api/v1/reportes/movimientos/export.csv` (Administrador)
- `GET /api/v1/reportes/movimientos/export.pdf` (Administrador)
- `GET /api/v1/reportes/movimientos/export.xlsx` (Administrador)
- `GET /api/v1/dashboard/resumen`
- `GET /api/v1/dashboard/historial-reciente`

### Usuarios del sistema

- `GET /api/v1/usuarios` (Administrador)
- `POST /api/v1/usuarios` (Administrador)
- `PATCH /api/v1/usuarios/{usuario_id}` (Administrador)
- `PATCH /api/v1/usuarios/{usuario_id}/estado` (Administrador)
- `PATCH /api/v1/usuarios/{usuario_id}/password` (Administrador)
- `DELETE /api/v1/usuarios/{usuario_id}` (Administrador)

### Auditoria

- `GET /api/v1/auditoria` (Administrador)

## Contratos minimos que usa el frontend

### Login frontend

`POST /api/v1/auth/login`

```json
{
  "correo": "admin@scise.sena.edu.co",
  "contrasena": "CambiarEstoInmediatamente123!"
}
```

Respuesta esperada:

```json
{
  "access_token": "jwt",
  "token_type": "bearer",
  "usuario": {
    "id": 1,
    "nombre": "Administrador SCISE",
    "correo": "admin@scise.sena.edu.co",
    "rol": "Administrador"
  }
}
```

### Registro de ingresos

`POST /api/v1/movimientos/ingresos`

```json
{
  "estudiante_id": 10,
  "equipos": [101, 102],
  "observacion": "opcional"
}
```

### Registro de salidas

`POST /api/v1/movimientos/salidas`

```json
{
  "estudiante_id": 10,
  "equipos": [101]
}
```

## Pruebas

Ejecutar tests:

```powershell
python -m pytest -q
```

## Notas operativas

- Si aparece error SQL por columnas nuevas, ejecutar `alembic upgrade head`.
- `ALLOWED_ORIGINS` debe ir como string separado por comas para que `main.py` lo procese con `split(",")`.
- Swagger `Authorize` usa OAuth2 Password con `tokenUrl=/api/v1/auth/token`.
- El endpoint `POST /api/v1/estudiantes` ya permite crear estudiantes a cualquier usuario autenticado, no solo al administrador.
