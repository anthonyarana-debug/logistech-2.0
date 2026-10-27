# Comprobaciones de Fase 1

Fecha: 27 de octubre de 2026 (America/Lima). Windows y contenedores Linux locales. No se ejecutaron pruebas cloud ni de carga.

## Resultados y reproducción

Ejecutar `python scripts/verificar_fase1.py` con Compose saludable. [fase1-verificacion.json](evidencias/fase1-verificacion.json) conserva comandos, códigos, stdout/stderr y respuestas HTTP. La ejecución final sobre PostgreSQL 17.11 registró **20 comprobaciones con código 0**. Las advertencias no se ocultan: código 0 no significa ausencia de advertencias de producción.

| Comando/comprobación | Resultado real |
|---|---|
| `docker info --format '{{.OSType}} {{.ServerVersion}}'` | `linux 29.5.3` |
| `docker compose config --quiet` | Código 0 |
| `docker compose up -d --build --wait --wait-timeout 180` | Construcción y arranque completados, tres servicios saludables |
| `docker compose ps` | db/backend/frontend saludables; puertos web solo 127.0.0.1 |
| `docker compose exec -T backend python -m pip check` | No broken requirements found; aviso no fatal de caché pip sin permiso de escritura |
| `docker compose exec -T backend python manage.py check` | Sin problemas, 0 silenciados |
| `docker compose exec -T backend python manage.py makemigrations --check --dry-run` | No changes detected |
| `docker compose exec -T backend python manage.py migrate --noinput` | No migrations to apply; auth deshabilitado |
| `docker compose exec -T backend python manage.py showmigrations` | Sin migraciones listadas, código 0 |
| `docker compose exec -T backend python -m tools.verificar_base` | PostgreSQL 17.11, tablas vacías, autenticación no migrada |
| `docker compose exec -T backend python -m pytest --ds=config.settings.testing -q -o cache_dir=/tmp/logistech-pytest-cache` | **8 passed**, 0.77 s en la ejecución final registrada |
| `docker compose exec -T backend ruff check --no-cache .` | All checks passed |
| `docker compose exec -T frontend npm run lint` | Código 0 |
| `docker compose exec -T frontend npm run build` | Build Vite completado |
| `docker compose exec -T backend python manage.py check --deploy --settings=config.settings.production` | Código 0, advertencias HSTS W005 y W021 |
| GET API `/api/v1/health/` | 200 JSON, consulta SELECT 1 real |
| GET API `/api/v1/health/live/` | 200 JSON, sin DB |
| GET API `/api/v1/no-existe/` | 404 JSON en español |
| GET frontend `/` | 200 HTML |
| GET frontend `/api/v1/health/` | 200 JSON mediante proxy |
| Inspección de red sin guardar configuración expandida | PostgreSQL privado, sin host port; frontend/backend en loopback |

También se ejecutaron Ruff sobre backend/scripts y pip check en el venv Windows. npm install inicial y npm ci del contenedor informaron 0 vulnerabilidades en la auditoría npm en ese momento; no equivale a una auditoría completa. No se ejecutó escáner de vulnerabilidades Python/contenedores.

## Ocho pruebas

- Liveness sin consulta DB.
- Readiness ejecuta SELECT 1 con cursor controlado.
- Fallo DB devuelve 503 sin revelar la excepción.
- Ruta API inexistente devuelve JSON 404.
- Auth/admin/sesiones no instalados y motor PostgreSQL configurado.
- Check E001 rechaza habilitar auth.User.
- Simple JWT firma/verifica y rechaza token expirado o con clave ajena en subproceso sin DB.
- Integración PostgreSQL real y readiness 200 en una base de prueba separada.

En Windows se ejecutaron las siete primeras con venv: `7 passed, 1 deselected` al excluir integración. No se utilizó SQLite. El smoke JWT no demuestra registro, login, refresh ni permisos de negocio: son de F2/F3.

## Caída y recuperación

Se detuvo PostgreSQL con `docker compose stop db`. Readiness directo y mediante proxy devolvieron **503**; liveness siguió en **200**. [Evidencia HTTP](evidencias/fase1-caida-postgresql.json). En navegador, «Volver a comprobar» mostró «Servicio no disponible»: [captura real](evidencias/fase1-servicio-no-disponible.png).

Se restauró con `docker compose up -d --wait --wait-timeout 120`, conservando volumen y datos. Tres servicios saludables y web «Entorno conectado» después de volver a comprobar. La ejecución final del verificador se hizo tras la recuperación.

## Interfaz y límites

Revisión en navegador de escritorio de conectado/carga/error. [Captura del entorno conectado](evidencias/fase1-entorno-conectado.png). No se verificó dispositivo móvil real, cámara, accesibilidad completa o flujos de negocio.

No hay migraciones de modelos todavía: migrate/showmigrations solo comprobaron un grafo vacío. No afirmar que se aplicaron migraciones de negocio. Cloud, TLS, backups, carga y roles permanecen sin probar.

## Errores corregidos

| Error inicial | Corrección y repetición |
|---|---|
| Motor Docker inaccesible | docker desktop start; Linux y servicios saludables |
| Congelación de dependencias fallaba por nombre guion/underscore | Consultar importlib.metadata.version; .txt generados, instalación Linux y pip check |
| pytest configuraba Django antes del conftest y faltaba SECRET_KEY | Settings testing separado con valores ficticios; suite aprobada |
| Importación JWT requería auth/contenttypes | Smoke en proceso aislado sin DB; aplicación mantiene auth deshabilitado |
| @eslint/js 10.13.0 inexistente | Consultar registro y fijar 10.0.1, independiente de eslint 10.13.0; instalación/build/lint aprobados |
| Vite EACCES al escribir en /app | Propiedad del directorio para usuario node; mantiene ejecución sin root |
| Ruff no podía escribir caché del contenedor | --no-cache; check aprobado sin ampliar privilegios |
| Formato/imports y salida UTF-8 mal decodificada | Ruff/ESLint y encoding UTF-8 explícito de subprocess |

Pendientes no críticos: W005/W021 (HSTS subdominios/preload) y aviso de caché pip del usuario no root. Los detalles de dominio/producción se resolverán antes de desplegar, sin silenciar advertencias.

## CHECKLIST HUMANO

- Revisar informe y web local; no es necesario repetir manualmente pruebas ya registradas.
- Autorizar F2 para modelos y autenticación.
