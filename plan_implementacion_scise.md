# Plan Backend SCISE (Consolidado)

Documento consolidado a partir de las ultimas tres solicitudes de planeacion backend:

1. Lista de endpoints necesarios y orden por etapas.
2. Matriz endpoint -> request/response schema.
3. Checklist de implementacion para equipo de 4 integrantes (incluyendo especialista en PostgreSQL).

Base de referencia arquitectonica:
- `arquitectura_fastapi_scise.md.resolved`
- Frontend modular por cajas (`auth`, `ingreso`, `salida`, `reportes`, `usuarios`, `configuracion`)

---

## 1) Estructura de endpoints y orden por etapas

Prefijo API sugerido:
- `/api/v1`

### Etapa 1: Auth y sesion
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/refresh` (opcional recomendado)

### Etapa 2: Catalogo operativo (estudiantes y equipos)
- `GET /api/v1/estudiantes`
- `POST /api/v1/estudiantes`
- `GET /api/v1/estudiantes/{estudiante_id}`
- `GET /api/v1/estudiantes/by-documento/{documento}`
- `PATCH /api/v1/estudiantes/{estudiante_id}`
- `PATCH /api/v1/estudiantes/{estudiante_id}/estado`
- `DELETE /api/v1/estudiantes/{estudiante_id}`
- `GET /api/v1/equipos`
- `POST /api/v1/equipos`
- `GET /api/v1/equipos/{equipo_id}`
- `PATCH /api/v1/equipos/{equipo_id}`
- `PATCH /api/v1/equipos/{equipo_id}/estado`
- `DELETE /api/v1/equipos/{equipo_id}`
- `GET /api/v1/estudiantes/{estudiante_id}/equipos`
- `POST /api/v1/estudiantes/{estudiante_id}/equipos/{equipo_id}`
- `DELETE /api/v1/estudiantes/{estudiante_id}/equipos/{equipo_id}`

### Etapa 3: Flujo core ingreso/salida
- `POST /api/v1/movimientos/ingresos` (registro multiple)
- `POST /api/v1/movimientos/salidas` (registro multiple)
- `GET /api/v1/movimientos/activos/estudiante/{estudiante_id}`
- `GET /api/v1/movimientos/estado-equipos` (snapshot actual)

### Etapa 4: Historial y reportes
- `GET /api/v1/movimientos`
- `GET /api/v1/movimientos/{movimiento_id}`
- `GET /api/v1/reportes/movimientos/resumen`
- `GET /api/v1/reportes/movimientos/historial`
- `GET /api/v1/reportes/movimientos/export.csv`
- `GET /api/v1/reportes/movimientos/export.pdf`

### Etapa 5: Configuracion (usuarios del sistema)
- `GET /api/v1/usuarios`
- `POST /api/v1/usuarios`
- `GET /api/v1/usuarios/{usuario_id}`
- `PATCH /api/v1/usuarios/{usuario_id}`
- `PATCH /api/v1/usuarios/{usuario_id}/estado`
- `PATCH /api/v1/usuarios/{usuario_id}/password`
- `DELETE /api/v1/usuarios/{usuario_id}`
- `GET /api/v1/auditoria`

### Etapa 6: Hardening
- Estandar de errores global
- Paginacion y filtros consistentes
- Validaciones de permisos por rol
- Pruebas de integracion y performance

---

## 2) Matriz endpoint -> schemas

### Auth
- `POST /auth/login`
  - Request: `LoginRequest { username, password }`
  - Response: `TokenResponse { access_token, token_type, usuario }`
- `POST /auth/logout`
  - Request: `LogoutRequest` (o solo bearer token)
  - Response: `MessageResponse { detail }`
- `GET /auth/me`
  - Request: bearer token
  - Response: `UserSessionResponse { id, username, rol, estado }`

### Estudiantes (operativo)
- `GET /estudiantes`
  - Query: `q, rol, estado, fecha_desde, fecha_hasta, skip, limit`
  - Response: `PaginatedEstudianteResponse`
- `POST /estudiantes`
  - Request: `EstudianteCreate`
  - Response: `EstudianteResponse`
- `GET /estudiantes/{id}`
  - Response: `EstudianteDetailResponse`
- `GET /estudiantes/by-documento/{documento}`
  - Response: `EstudianteResponse`
- `PATCH /estudiantes/{id}`
  - Request: `EstudianteUpdate`
  - Response: `EstudianteResponse`
- `PATCH /estudiantes/{id}/estado`
  - Request: `EstudianteEstadoUpdate { estado }`
  - Response: `EstudianteResponse`
- `DELETE /estudiantes/{id}`
  - Response: `MessageResponse`

### Equipos
- `GET /equipos`
  - Query: `q, tipo, estado, skip, limit`
  - Response: `PaginatedEquipoResponse`
- `POST /equipos`
  - Request: `EquipoCreate`
  - Response: `EquipoResponse`
- `GET /equipos/{id}`
  - Response: `EquipoDetailResponse`
- `PATCH /equipos/{id}`
  - Request: `EquipoUpdate`
  - Response: `EquipoResponse`
- `PATCH /equipos/{id}/estado`
  - Request: `EquipoEstadoUpdate`
  - Response: `EquipoResponse`
- `DELETE /equipos/{id}`
  - Response: `MessageResponse`
- `GET /estudiantes/{id}/equipos`
  - Response: `EquipoListResponse`
- `POST /estudiantes/{id}/equipos/{equipo_id}`
  - Response: `EstudianteEquipoResponse`
- `DELETE /estudiantes/{id}/equipos/{equipo_id}`
  - Response: `MessageResponse`

### Movimientos
- `POST /movimientos/ingresos`
  - Request: `MovimientoIngresoBatchCreate { estudiante_id, equipos: [equipo_id], observacion? }`
  - Response: `MovimientoBatchResponse`
- `POST /movimientos/salidas`
  - Request: `MovimientoSalidaBatchCreate { estudiante_id, equipos: [equipo_id], observacion? }`
  - Response: `MovimientoBatchResponse`
- `GET /movimientos/activos/estudiante/{id}`
  - Response: `EquipoActivoListResponse`
- `GET /movimientos`
  - Query: `tipo, fecha, estudiante_id, serial, skip, limit`
  - Response: `PaginatedMovimientoResponse`
- `GET /movimientos/{id}`
  - Response: `MovimientoResponse`

### Reportes
- `GET /reportes/movimientos/resumen`
  - Query: `fecha_desde, fecha_hasta`
  - Response: `ReportesResumenResponse { en_instalacion, fuera_instalacion, movimientos_hoy, porcentajes }`
- `GET /reportes/movimientos/historial`
  - Query: `tipo, fecha, skip, limit`
  - Response: `PaginatedMovimientoResponse`
- `GET /reportes/movimientos/export.csv`
  - Query: filtros equivalentes a historial
  - Response: `text/csv`
- `GET /reportes/movimientos/export.pdf`
  - Query: filtros equivalentes a historial
  - Response: `application/pdf`

### Usuarios del sistema (configuracion)
- `GET /usuarios`
  - Query: `q, rol, estado, skip, limit`
  - Response: `PaginatedUsuarioSistemaResponse`
- `POST /usuarios`
  - Request: `UsuarioSistemaCreate`
  - Response: `UsuarioSistemaResponse`
- `GET /usuarios/{id}`
  - Response: `UsuarioSistemaDetailResponse`
- `PATCH /usuarios/{id}`
  - Request: `UsuarioSistemaUpdate`
  - Response: `UsuarioSistemaResponse`
- `PATCH /usuarios/{id}/estado`
  - Request: `UsuarioSistemaEstadoUpdate { estado }`
  - Response: `UsuarioSistemaResponse`
- `PATCH /usuarios/{id}/password`
  - Request: `UsuarioPasswordUpdate { nueva_password, confirmacion }`
  - Response: `MessageResponse`
- `DELETE /usuarios/{id}`
  - Response: `MessageResponse`

### Auditoria
- `GET /auditoria`
  - Query: `modulo, actor_id, fecha_desde, fecha_hasta, skip, limit`
  - Response: `PaginatedAuditoriaResponse`

### Schemas base transversales
- `MessageResponse { detail: str }`
- `PaginationMeta { total, skip, limit, has_next }`
- `Paginated<T> { data: list[T], meta: PaginationMeta }`
- `ErrorResponse { detail, code?, field_errors? }`

---

## 3) Checklist de implementacion (equipo de 4)

Roles del equipo:
1. Integrante A: Backend Auth/Seguridad
2. Integrante B: Backend Dominio (Estudiantes/Equipos/Movimientos/Reportes)
3. Integrante C: Integracion Frontend
4. Integrante D: Especialista Base de Datos PostgreSQL

### Bloque 1 - Infra + DB (A y D)
- [ ]  A Crear estructura por capas (`api`, `controllers`, `services`, `repositories`, `schemas`).
- [ ]  D Diseñar esquema PostgreSQL final y constraints.
- [ ]  D Crear migraciones Alembic iniciales.
- [ ]  D Crear indices clave:
  - [ ] `estudiantes(documento)` unique
  - [ ] `equipos(serial)` unique
  - [ ] `movimientos(estudiante_id, timestamp)`
  - [ ] `movimientos(equipo_id, timestamp)`
- [ ] D Crear seed minimo (rol admin y usuario admin).
- [ ] A+D Validar conexion y healthcheck.

### Bloque 2 - Auth (A + C + D)
- [ ] A Implementar `POST /auth/login`.
- [ ] A Implementar `GET /auth/me`.
- [ ] A Implementar `POST /auth/logout` con blacklist.
- [ ] A Integrar `Depends(get_current_user)` y `require_role`.
- [ ] C Conectar login del frontend a API real.
- [ ] D Validar hash de password y politicas de seguridad.

### Bloque 3 - Operacion ingreso/salida (B + C + D)
- [ ] B `GET /estudiantes/by-documento/{documento}`
- [ ] B`GET /estudiantes/{id}/equipos`
- [ ] B`POST /movimientos/ingresos` (batch)
- [ ] B`GET /movimientos/activos/estudiante/{id}`
- [ ] B`POST /movimientos/salidas` (batch)
- [ ] D Reglas transaccionales:
  - [ ] evitar doble ingreso activo por equipo
  - [ ] validar salida solo si existe ingreso activo
- [ ] C Conectar cajas de `Ingreso` y `Salida` al backend.
- [ ] C Eliminar dependencia de src/lib/movimientos.ts y src/lib/operacion.ts para flujo principal.

### Bloque 4 - Reportes (B + C + D)
- [ ] B `GET /reportes/movimientos/resumen`
- [ ] B `GET /reportes/movimientos/historial` con paginacion/filtros
- [ ] B `GET /reportes/movimientos/export.csv`
- [ ] B `GET /reportes/movimientos/export.pdf` (inicial o placeholder)
- [ ] D Optimizar consultas SQL para historico y resumen.
- [ ] C Conectar `CajaEstadisticas`, `CajaFiltros`, `CajaHistorialMovimientos`.

### Bloque 5 - Configuracion (A + C + D)
- [X] A `GET /usuarios`
- [X] A `POST /usuarios`
- [X] A `PATCH /usuarios/{id}`
- [X] A `PATCH /usuarios/{id}/estado`
- [X] A `PATCH /usuarios/{id}/password`
- [X] A `DELETE /usuarios/{id}`
- [X] A `GET /auditoria`
- [ ] D Conectar tabla, modales y caja auditoria a API real.

### Bloque 6 - Gestion usuarios operativos (B + C + D)
- [ ] B CRUD `estudiantes`
- [ ] B CRUD `equipos`
- [ ] C Asociar/desasociar equipo-estudiante
- [ ] D Conectar `UsuariosView`, `NewUserModal`, `UserEditModal`.

### QA y cierre (todos)
- [ ] A y B Tests unitarios (services/repositories)
- [ ] A, B, D Tests integracion API + DB
- [ ] C Tests E2E front para flujos criticos
- [ ] D Documentacion OpenAPI y coleccion Postman
- [ ] A y B Checklist de seguridad (roles, token revocado, password policy)

---

## 4) Mapeo cajas frontend -> endpoints

### Ingreso
- `CajaEscanearCarnet` -> `GET /estudiantes/by-documento/{documento}`
- `CajaSeleccionarEquipo` -> `GET /estudiantes/{id}/equipos`
- `CajaAcciones` -> `POST /movimientos/ingresos`

### Salida
- `CajaEscanearCarnet` -> `GET /estudiantes/by-documento/{documento}`
- `CajaSeleccionarEquipos` -> `GET /movimientos/activos/estudiante/{id}`
- `CajaAcciones` -> `POST /movimientos/salidas`

### Reportes
- `CajaEstadisticas` -> `GET /reportes/movimientos/resumen`
- `CajaHistorialMovimientos` -> `GET /reportes/movimientos/historial`
- `CajaFiltros` -> filtros de historial + export csv/pdf

### Gestionar Usuarios (operativo)
- Tabla/filtros -> `GET /estudiantes`
- Crear/editar/estado -> `POST/PATCH /estudiantes`
- Equipos asociados -> endpoints de asociacion estudiante-equipo

### Configuracion (usuarios del sistema)
- Tabla -> `GET /usuarios`
- Crear/editar/eliminar/estado -> `POST/PATCH/DELETE /usuarios`
- Cambio de contrasena -> `PATCH /usuarios/{id}/password`
- Auditoria -> `GET /auditoria`

---

## 5) Notas de implementacion

- No mezclar `usuarios del sistema` con `estudiantes operativos`.
- Mantener permisos predefinidos por rol del sistema:
  - `Administrador`
  - `Usuario`
- Unificar manejo de errores para que el frontend no tenga casos especiales por endpoint.
- En listados, incluir siempre paginacion (`skip`, `limit`) desde la primera version.
- Para `export.pdf`, iniciar con version minima y mejorar estilo en iteraciones.

