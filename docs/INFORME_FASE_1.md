# Informe de cierre — Fase 1

Fecha: 27 de octubre de 2026 (America/Lima).

FASE COMPLETADA: Configuración inicial de LogisTech 2.0.

ESTADO: **Completa para el alcance local de F1.** El entregable académico del 25 % sigue pendiente de F2–F5. Cloud no desplegado. No se implementó autenticación ni CRUD.

## FUNCIONALIDADES

- Django 5.2.18/DRF 3.16.1 y PostgreSQL 17.11 real en Compose.
- Python 3.13.17 aislado en venv y contenedor. Simple JWT 5.5.1 instalado y compatibilidad básica comprobada, sin endpoints de autenticación.
- React/Vite/JavaScript, Tailwind y Router con pantalla de estado conectada al health real.
- Health de db/backend/frontend, volumen PostgreSQL y puertos web en loopback.
- Variables requeridas y generador de secretos local que no imprime ni sobrescribe valores; plantilla ficticia y secretos ignorados por Git.
- Ajustes development/testing/production separados; JSON 404/500; liveness y readiness independientes.
- Auth/admin/sessions/contenttypes sin habilitar y sin tablas auth_user. Check E001 impide habilitar auth con el usuario estándar. Custom User y su 0001_initial se crearán en F2 antes de aplicar migraciones de autenticación.

## ARCHIVOS

| Ubicación | Archivos creados |
|---|---|
| Raíz | `.gitignore`, `.gitattributes`, `.env.example`, `docker-compose.yml`, `README.md` |
| Backend base | `manage.py`, `Dockerfile`, `.dockerignore`, `pyproject.toml`, requirements/requirements-dev tanto `.in` como `.txt` |
| Backend configuración | Paquetes config/settings y sus `__init__.py`; `base.py`, `development.py`, `testing.py`, `production.py`, `urls.py`, `wsgi.py`, `asgi.py` |
| Backend core | Paquetes apps/core y sus `__init__.py`; `apps.py`, `checks.py`, `views.py` |
| Backend verificación | `tests/test_infrastructure.py`, `tests/test_postgresql.py`, `tools/verificar_jwt.py`, `tools/verificar_base.py` |
| Frontend | `package.json`, `package-lock.json`, `Dockerfile`, `.dockerignore`, `index.html`, `vite.config.js`, `eslint.config.js`, `src/main.jsx`, `src/pages/EnvironmentPage.jsx`, `src/services/health.js`, `src/styles/index.css` |
| Scripts | `configurar_entorno.py`, `verificar_fase1.py` |
| Documentación | Este informe, PRUEBAS, DESPLIEGUE, DECISIONES_TECNICAS; estado actualizado en PLAN, ARQUITECTURA y MATRIZ_ENTREGABLES |
| Evidencias | `evidencias/fase1-verificacion.json`, `fase1-caida-postgresql.json` y dos capturas PNG reales |

Se generaron .env, .venv, node_modules, dist e imágenes/volumen local para ejecutar; fuera del código versionado según corresponda. No se crearon carpetas de negocio vacías. No se modificó Android: su código no está en el repositorio y los endpoints heredados siguen sin corroborarse. Se conserva historial local por fase, sin push ni remoto configurado.

## PRUEBAS EJECUTADAS

- docker desktop start resolvió la ausencia del motor; docker info confirmó linux 29.5.3.
- Construcción y arranque Compose completados, tres servicios saludables.
- Verificador final: **20 comprobaciones con código 0**, salidas reales en [evidencia](evidencias/fase1-verificacion.json).
- pytest Docker: **8 pruebas aprobadas**, incluida PostgreSQL real; Windows venv: siete unitarias aprobadas excluyendo integración.
- Django check sin problemas, Ruff y ESLint aprobados, build Vite completado, pip check sin dependencias rotas.
- migrate: **sin migraciones que aplicar**; introspección: **sin tablas de aplicación**. No se probaron todavía migraciones de modelos inexistentes.
- HTTP health/liveness/proxy 200; inexistencia API 404 JSON; web 200.
- Caída real PostgreSQL: readiness/proxy 503, liveness 200, interfaz mostró error. Reinicio conservó volumen y recuperó los servicios y la interfaz.
- check --deploy: dos advertencias HSTS W005/W021, no silenciadas.

Comandos completos, resultados y límites en [PRUEBAS.md](PRUEBAS.md).

## ERRORES Y PENDIENTES

Se corrigieron problemas iniciales de Docker, permisos Vite, imports JWT, configuración pytest, selección de @eslint/js, congelación de dependencias, formato y caché de Ruff; se repitieron las comprobaciones afectadas.

No quedan errores críticos conocidos en F1. Quedan W005/W021 sobre HSTS de subdominios/preload y aviso no fatal de caché pip. Pendientes de otras fases: modelos, migraciones de negocio, login/registro, permisos multiempresa, CRUD, móvil real, carga y cloud autorizado. No se verificaron TLS externo, backups o rendimiento.

## SEGURIDAD

PostgreSQL no publica puerto y usa red interna separada; frontend no está en esa red. Web/API solo 127.0.0.1. Procesos web sin root, capacidades eliminadas y no-new-privileges. Secretos aleatorios ignorados por Git y omitidos en evidencias. DEBUG=false por defecto; producción rechaza DEBUG=true y claves cortas. Fallos DB no revelan datos internos.

No se abrió CORS global ni se accedió al VPS. No se crearon recursos remotos o de pago. El usuario PostgreSQL inicial es administrador local para bootstrap/pruebas: separar un rol de aplicación restringido antes de producción.

## DOCUMENTACIÓN

README: inicio, Docker y preservación de datos. PRUEBAS: evidencia real. DESPLIEGUE: local verificado/cloud pendiente. DECISIONES_TECNICAS: versiones y secuencia Custom User. Capturas reales de conexión y fallo.

## CHECKLIST HUMANO

- Revisar la [web local](http://127.0.0.1:5173) y este informe. Los tres servicios quedan iniciados; `docker compose stop` los detiene conservando el volumen.
- Autorizar F2 cuando corresponda. Docker ya está funcionando; no se necesita configuración manual adicional para revisar F1.
- Si se dispone del original Android, facilitar su ubicación para auditoría de solo lectura; no bloquea la base web.
- Antes de F5, confirmar rúbrica cloud/cuenta académica y autorizar recursos externos por separado. Nunca enviar secretos al chat.

SIGUIENTE FASE: Fase 2 — modelos mínimos, Custom User desde su primera migración, roles y autenticación verificable.

AUTORIZACIÓN: **Esperando confirmación del usuario. No se inició Fase 2.**
