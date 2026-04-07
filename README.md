# SCISE-Backend

API de SCISE construida con FastAPI + SQLAlchemy + Alembic para autenticación, gestión de estudiantes/equipos, movimientos de ingreso/salida, reportes, usuarios del sistema y auditoría.

## Estado actual

- Auth operativa para frontend:
  - `POST /api/v1/auth/login` con JSON `{ correo, contrasena }`
  - `POST /api/v1/auth/logout` con JWT
  - `POST /api/v1/auth/token` para Swagger OAuth2
- Endpoints de `ingreso`, `salida`, `usuarios`, `equipos`, `reportes`, `dashboard`, `configuración` y `auditoría` activos en `api/v1`.
- CORS habilitado vía `ALLOWED_ORIGINS`.
- Logging middleware activo en cada request.
- Migraciones Alembic incluidas para sincronización de esquema.  
  Incluye `fecha_registro` en estudiantes.

## Arquitectura por capas

```text
app/
  api/v1/          # Rutas HTTP (FastAPI routers)
  controllers/     # Orquestación de casos de uso por módulo
  services/        # Reglas de negocio
  repositories/    # Acceso a datos (SQLAlchemy)
  models/          # Modelos ORM
  schemas/         # Contratos request/response (Pydantic)
  core/            # Configuración, seguridad, dependencias, logger
  db/              # Session, base, registro de modelos, seed
  middlewares/     # Middleware HTTP
  utils/           # Utilidades (JWT, password)
```

## Tecnologías

- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic v2
- PostgreSQL (`psycopg2-binary`)
- JWT (`python-jose`)
- Password hashing (`passlib`, `bcrypt`)
- Exportes XLSX (`openpyxl`)
- Testing (`pytest`)

## Requisitos

- Python 3.12 recomendado
- PostgreSQL 14+
- Entorno virtual (`.venv`)

## Configuración local

1. Crear y activar entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3. Crear `.env` a partir de `.env.example` y completar valores reales.

Variables principales:

| Variable | Descripción |
| --- | --- |
| `DATABASE_URL` | Conexión PostgreSQL |
| `SECRET_KEY` | Clave JWT |
| `ALGORITHM` | Algoritmo JWT, por defecto `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Minutos de expiración del token |
| `APP_HOST` / `APP_PORT` | Host/puerto del servidor |
| `DEBUG` | Modo debug |
| `ALLOWED_ORIGINS` | Orígenes CORS separados por coma |
| `ADMIN_NOMBRE` / `ADMIN_CORREO` / `ADMIN_DOCUMENTO` / `ADMIN_PASSWORD` | Datos del admin inicial |
| `ENVIRONMENT` | `development`, `testing`, `production` |

4. Ejecutar migraciones:

```powershell
alembic upgrade head
```

5. Opcional, recomendado la primera vez: seed de roles + admin:

```powershell
python -m app.db.seed
```

## Ejecución

Levantar API en desarrollo:

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Documentación interactiva:

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
  Nota: internamente busca por documento o código de barras.
- `GET /api/v1/estudiantes/{estudiante_id}/equipos`
- `POST /api/v1/estudiantes` (Administrador)
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

### Usuarios del sistema (Configuración)

- `GET /api/v1/usuarios` (Administrador)
- `POST /api/v1/usuarios` (Administrador)
- `PATCH /api/v1/usuarios/{usuario_id}` (Administrador)
- `PATCH /api/v1/usuarios/{usuario_id}/estado` (Administrador)
- `PATCH /api/v1/usuarios/{usuario_id}/password` (Administrador)
- `DELETE /api/v1/usuarios/{usuario_id}` (Administrador)

### Auditoría

- `GET /api/v1/auditoria` (Administrador)

## Contratos mínimos que usa el frontend

### Login frontend

`POST /api/v1/auth/login`

```json
{
  "correo": "admin@scise.sena.edu.co",
  "contrasena": "tu_password"
}
```

Respuesta:

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

### Registro de ingresos (batch)

`POST /api/v1/movimientos/ingresos`

```json
{
  "estudiante_id": 10,
  "equipos": [101, 102],
  "observacion": "opcional"
}
```

### Registro de salidas (batch)

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

En el estado actual del entorno local, la suite pasa casi completa, pero puede aparecer 1 prueba fallando (`tests/test_auth.py::test_login_success`) por credenciales o estado del admin en la base de datos.

## Notas operativas

- Si aparece error SQL por columnas nuevas, por ejemplo `fecha_registro` en `estudiantes`, ejecutar:
  - `alembic upgrade head`
- `ALLOWED_ORIGINS` debe estar en formato string separado por comas para que `main.py` lo procese con `split(",")`.
- Swagger `Authorize` usa OAuth2 Password con `tokenUrl=/api/v1/auth/token`.
