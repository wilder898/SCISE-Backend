# Plan de Despliegue SCISE (Tutorial Paso a Paso)

## 1) Objetivo de este documento

Este tutorial esta pensado para:

- Equipo de proyecto final de grado.
- Repositorio principal con submodulos:
  - `SCISE-Backend`
  - `SCISE-Frontend`
- Entorno `staging` usado como entorno final de entrega.
- Flujo donde ustedes siguen integrando cambios mientras preparan la entrega.

La meta es que puedas desplegar sin experiencia previa y con bajo riesgo.

---

## 2) Arquitectura recomendada (simple y suficiente)

Para este proyecto, usa una arquitectura facil de operar:

1. `Frontend (Astro)` en hosting estatico:
   - Cloudflare Pages o Vercel.
2. `Backend (FastAPI)` en servicio web:
   - Render, Railway o Fly.io.
3. `Base de datos PostgreSQL`:
   - Neon (si ya la estan usando, mantenerla).

## 3) Estrategia de ramas recomendada para ustedes

Como van a seguir integrando cambios, usen dos carriles:

1. `main`: desarrollo continuo del equipo.
2. `release/final-grado`: rama de estabilizacion y despliegue final.

Regla clave:

- El entorno final (su "staging final") se despliega solo desde `release/final-grado`.
- Todo lo nuevo entra primero por `main`.
- A `release/final-grado` solo pasan lo necesario para entregar.

---

## 4) Checklist previo (antes de tocar infraestructura)

Completa esto primero:

1. Backend local responde:
   - `GET /health`
2. Frontend local compila:
   - `npm run build`
3. Variables de entorno definidas y validadas.
4. No hay credenciales expuestas en repositorio publico.
5. El equipo acuerda una fecha de "congelacion" (24-48h antes de entregar).

---

## 5) Paso a paso de ramas (Backend, Frontend y repo principal)

> Ejecuta estos pasos en este orden.

### Paso 5.1 - Crear rama release en Backend

```bash
cd SCISE-Backend
git checkout main
git pull origin main
git checkout -b release/final-grado
git push -u origin release/final-grado
```

### Paso 5.2 - Crear rama release en Frontend

```bash
cd ../SCISE-Frontend
git checkout main
git pull origin main
git checkout -b release/final-grado
git push -u origin release/final-grado
```

### Paso 5.3 - Congelar submodulos en repo principal

```bash
cd ..
git checkout main
git pull origin main
git checkout -b release/final-grado

cd SCISE-Backend && git checkout release/final-grado && git pull && cd ..
cd SCISE-Frontend && git checkout release/final-grado && git pull && cd ..

git add SCISE-Backend SCISE-Frontend
git commit -m "chore(release): freeze submodules for final-grade"
git push -u origin release/final-grado
```

---

## 6) Seguridad minima obligatoria (haz esto antes de desplegar)

### Paso 6.1 - Revisar secretos

No dejes claves reales en git. Usa variables del proveedor.

Variables tipicas backend:

- `DATABASE_URL`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `ALLOWED_ORIGINS`
- `ENVIRONMENT`
- `DEBUG`
- `ADMIN_NOMBRE`
- `ADMIN_CORREO`
- `ADMIN_DOCUMENTO`
- `ADMIN_PASSWORD`

### Paso 6.2 - Valores recomendados para entorno final

- `ENVIRONMENT=staging` (si asi lo llamaran internamente)
- `DEBUG=false`
- `ALLOWED_ORIGINS=https://tu-frontend-final.example.com`

---

## 7) Despliegue del Backend (FastAPI)

Esta guia usa un flujo genericamente compatible con Render/Railway/Fly.

### Paso 7.1 - Crear servicio web

1. En tu proveedor, crea un nuevo servicio web.
2. Conecta el repo `SCISE-Backend`.
3. Selecciona rama: `release/final-grado`.

### Paso 7.2 - Configurar build y start

- Build command:
```bash
pip install -r requirements.txt
```

- Start command:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2
```

### Paso 7.3 - Configurar variables de entorno

Carga todas las variables del paso 6.1 en el panel del proveedor.

### Paso 7.4 - Health check

Configura health check con:

- Path: `/health`
- Metodo: `GET`

Debe responder `200`.

---

## 8) Migraciones de base de datos (Alembic)

Haz esto en cada despliegue que cambie esquema.

### Paso 8.1 - Backup rapido antes de migrar

En Neon, crea snapshot/branch antes de migrar.

### Paso 8.2 - Ejecutar migracion

Si el proveedor permite consola:

```bash
alembic upgrade head
```

Si no permite consola, ejecuta migracion desde una maquina con las mismas variables de entorno del backend.

### Paso 8.3 - Verificar

1. Backend sigue arriba.
2. `/health` responde `ok`.
3. Endpoints criticos funcionan.

---

## 9) Despliegue del Frontend (Astro)

### Paso 9.1 - Crear proyecto frontend

1. En Cloudflare Pages o Vercel, crea proyecto.
2. Conecta repo `SCISE-Frontend`.
3. Rama de deploy: `release/final-grado`.

### Paso 9.2 - Configurar build

- Build command:
```bash
npm ci && npm run build
```

- Output directory:
```bash
dist
```

### Paso 9.3 - Variable de entorno frontend

Define:

- `PUBLIC_API_BASE_URL=https://tu-backend-final.example.com/api/v1`

Sin slash final extra.

### Paso 9.4 - Redeploy y prueba

1. Forzar deploy.
2. Abrir URL final del frontend.
3. Probar login.

---

## 10) Smoke test funcional (checklist de entrega)

Ejecuta este checklist completo en entorno final:

1. Login con admin.
2. Logout y relogin.
3. Modulo Ingreso:
   - Buscar estudiante por documento.
   - Cargar equipos.
   - Registrar ingreso.
4. Modulo Salida:
   - Listar activos por estudiante.
   - Registrar salida.
5. Modulo Reportes:
   - Resumen.
   - Historial.
   - Export CSV/PDF/XLSX.
6. Modulo Usuarios:
   - Listado de usuarios.
   - Crear usuario.
   - Editar usuario.
   - Cambiar estado.
7. Tabla de Equipos:
   - `GET /api/v1/equipos` trae datos reales.
   - Filtros (`q`, `tipo`, `estado`) funcionan.
8. Modulo Configuracion:
   - CRUD usuarios del sistema.
   - Auditoria visible para admin.

Si algo falla, no etiquetar version final todavia.

---

## 11) Flujo mientras tus companeros siguen subiendo cambios

Este es el proceso correcto:

1. Companeros trabajan normal en `main`.
2. Ustedes estabilizan `release/final-grado`.
3. Si necesitan un fix que ya existe en `main`, lo pasan a release:

```bash
git checkout release/final-grado
git cherry-pick <sha-del-fix>
git push
```

4. Deploy final siempre sale desde `release/final-grado`.

---

## 12) Congelacion final (24-48h antes de entrega)

Reglas en congelacion:

1. No entran features nuevas.
2. Solo bugfix critico.
3. Todo cambio requiere prueba manual del flujo afectado.
4. Deploy pequeno y frecuente (evitar mega deploy final).

---

## 13) Etiquetar version final de entrega

Cuando todo este aprobado:

### Backend
```bash
cd SCISE-Backend
git checkout release/final-grado
git pull
git tag -a v-final-grado-backend -m "Entrega final backend"
git push origin v-final-grado-backend
```

### Frontend
```bash
cd ../SCISE-Frontend
git checkout release/final-grado
git pull
git tag -a v-final-grado-frontend -m "Entrega final frontend"
git push origin v-final-grado-frontend
```

### Repo principal
```bash
cd ..
git checkout release/final-grado
git pull
git add SCISE-Backend SCISE-Frontend
git commit -m "chore(release): final pointers for grade delivery"
git tag -a v-final-grado -m "Entrega final SCISE"
git push origin release/final-grado
git push origin v-final-grado
```

---

## 14) Rollback rapido (por si algo falla en demo)

Ten siempre un rollback listo:

1. Identifica ultimo commit estable en `release/final-grado`.
2. Re-deploy apuntando a ese commit/tag estable.
3. Verifica:
   - login
   - ingreso
   - salida
   - reportes

Opciones seguras (sin reescribir historia):

```bash
git checkout release/final-grado
git revert --no-edit <sha-del-commit-problematico>
git push
```

Si usas plataforma con "Redeploy from previous commit", esa es la opcion mas facil y segura.

---

## 15) Errores comunes y como evitarlos

1. Backend arriba pero frontend falla por CORS:
   - Revisar `ALLOWED_ORIGINS`.
2. Frontend no pega al backend correcto:
   - Revisar `PUBLIC_API_BASE_URL`.
3. Login falla despues de deploy:
   - Revisar `SECRET_KEY`, `DATABASE_URL`, migraciones.
4. Endpoint responde 401 en pantallas internas:
   - Revisar token en `localStorage` y expiracion.
5. Datos no aparecen despues de cambios DB:
   - Revisar `alembic upgrade head`.

---

## 16) Plan sugerido por dias (simple)

### Dia 1
- Crear `release/final-grado`.
- Configurar servicios y variables.

### Dia 2
- Deploy backend + migraciones.
- Deploy frontend.
- Smoke test completo.

### Dia 3
- Corregir bugs criticos.
- Repetir smoke test.
- Congelacion.

### Dia 4
- Tag final.
- Demo/entrega.

---

## 17) Definicion de "Listo para entregar"

Solo consideren "listo" si se cumple todo:

1. Entorno final accesible por URL.
2. Login y modulos core operativos.
3. Sin errores bloqueantes en flujo principal.
4. Version etiquetada (`v-final-grado`).
5. Checklist de smoke test firmado por el equipo.

---

## 18) Nota final para su contexto academico

Como este proyecto no tendra mantenimiento largo post-entrega:

- Prioricen estabilidad funcional sobre perfeccion tecnica.
- No metan cambios grandes al final.
- Versionen bien lo entregado para tener evidencia clara.

Eso les reduce riesgo y les da una entrega solida.
