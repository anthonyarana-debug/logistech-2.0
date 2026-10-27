# LogisTech 2.0

Proyecto académico de Desarrollo de Soluciones en la Nube — TECSUP. **Fase 2: modelos y autenticación local implementados.** La web sigue mostrando el estado del entorno de F1; formularios web y CRUD REST se construirán en F4 y F3 respectivamente, previa aprobación.

## Iniciar localmente

Requiere Docker Desktop con motor Linux y Compose. Desde la raíz:

```powershell
docker info --format '{{.OSType}} {{.ServerVersion}}'
python scripts/configurar_entorno.py
docker compose build
docker compose up -d --wait db
docker compose run --rm --no-deps backend python manage.py migrate --noinput
docker compose up -d --wait --wait-timeout 180
```

Si `.env` ya existe, el generador se niega a sobrescribirlo: conservarlo y continuar. Genera secretos aleatorios sin imprimirlos; `.env.example` tiene marcadores ficticios. No copiar esos marcadores como secretos reales. No publicar `.env` ni la salida de `docker compose config` sin `--quiet`, porque expande credenciales.

- [Web de estado](http://127.0.0.1:5173).
- [Readiness con PostgreSQL](http://127.0.0.1:8000/api/v1/health/) y [liveness](http://127.0.0.1:8000/api/v1/health/live/).
- API de autenticación: `/api/v1/auth/`; ver [ENDPOINTS.md](docs/ENDPOINTS.md).
- [Admin restringido](http://127.0.0.1:8000/admin/): superadministrador creado mediante prompt seguro, nunca con credenciales fijas.

Solo web/API publican puertos, enlazados a 127.0.0.1. PostgreSQL no publica 5432 y usa red interna; procesos web sin root. Este Compose utiliza servidores de desarrollo y **no representa un despliegue de producción**.

Si Docker no responde: abrir Docker Desktop, habilitar Settings → General → Use the WSL 2 based engine y usar Linux containers. `docker desktop start`, `docker desktop status` y `wsl --status` ayudan al diagnóstico. Confirmar que docker info muestra `linux`, no solo la versión de la CLI. La habilitación de virtualización/WSL o un reinicio, si fueran necesarios, requieren intervención del usuario.

## Verificar Fase 2

```powershell
python scripts/verificar_fase2.py
```

Registra comandos/códigos/salidas en `docs/evidencias/fase2-verificacion.json`, sin contraseñas, tokens o cookies. Incluye PostgreSQL, estado de migraciones, pytest, lint/build y flujo HTTP real. El smoke HTTP crea una cuenta técnica por ejecución y al finalizar la deja inactiva, sin empresa y con contraseña inutilizable. No genera datos de inventario.

Comprobaciones individuales:

```powershell
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py migrate --check
docker compose exec -T backend python manage.py makemigrations --check --dry-run
docker compose exec -T backend python -m pytest --ds=config.settings.testing -q -o cache_dir=/tmp/pytest-f2
docker compose exec -T backend python -m tools.verificar_http_auth
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm run build
```

pytest crea una base PostgreSQL test_ desde cero y la elimina al terminar. No usar esta configuración contra producción. La evidencia de F1 se conserva como histórica, reproducible desde su commit; su verificador ya no se ejecuta sobre el esquema de F2.

## Usuario y administración

`accounts.User` existe desde `accounts/0001_initial.py`, con `AUTH_USER_MODEL=accounts.User` configurado antes de migrar. No se creó auth_user; el check E001 previene habilitarlo por accidente. Los grupos/permisos de auth no conceden por sí solos acceso global de negocio.

```powershell
docker compose exec backend python manage.py createsuperuser
```

Introducir correo y contraseña directamente en el prompt. Solo SUPERADMIN activo con flags coherentes entra al Admin. Allí puede crear empresas/sucursales/productos mínimos y asignar empresa/rol a operadores. No enviar credenciales al chat. No se creó un superadministrador automáticamente.

Registro público: solo operador sin empresa; rechaza campos privilegiados. Access JWT dura 5 minutos; refresh de un día en cookie HttpOnly, rotado y revocado al cerrar sesión. POST de autenticación exige CSRF; el contrato web inicia con GET `/auth/csrf/`. El access se conservará en memoria al conectar la web en F4; no se implementaron todavía sus formularios.

## Entornos y versiones

Python 3.13.17 aislado; Django 5.2.18, DRF 3.16.1, Simple JWT 5.5.1, PyJWT 2.15.1 y psycopg 3.3.6; PostgreSQL 17.11. Node 24.19.0, React 19.3.1, Vite 8.3.5, Tailwind 4.3.3 y Router DOM 7.18.4. Dependencias directas/transitivas fijadas en requirements*.txt y package-lock.json; sin nuevas dependencias en F2.

Para lint Python fuera de Docker:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements-dev.txt
.\.venv\Scripts\ruff.exe check --config backend/pyproject.toml backend scripts
```

Django local no carga .env automáticamente; Compose sí inyecta sus variables. Las pruebas con DB se ejecutan en Docker para evitar publicar PostgreSQL. Frontend: `npm ci`, `npm run lint` y `npm run build` desde frontend. Si se ejecuta Vite fuera del contenedor, definir `$env:API_PROXY_TARGET='http://127.0.0.1:8000'` antes de npm run dev; el proxy de Docker utiliza backend:8000. Ninguna variable VITE_ contiene secretos.

## Detener y reconstruir

`docker compose stop` conserva contenedores/volumen; `docker compose up -d --wait` vuelve a iniciarlos. Tras cambiar fuentes, reconstruir con `docker compose up -d --build --wait`. Aplicar explícitamente las nuevas migraciones antes de iniciar flujos que las necesiten; no hay migración automática oculta al arrancar. No usar `down -v` como rutina: destruye datos.

## Documentos y límites

- [Informe F2](docs/INFORME_FASE_2.md), [pruebas](docs/PRUEBAS.md), [base de datos](docs/BASE_DE_DATOS.md), [seguridad](docs/SEGURIDAD.md), [roles](docs/ROLES_PERMISOS.md) y [despliegue pendiente](docs/DESPLIEGUE.md).
- [Industrial Precision: diseño A/B y brief Stitch](docs/DISENO_UI_UX.md), con [boceto A](docs/diseno/alternativa-a.svg) y [boceto B](docs/diseno/alternativa-b.svg). Son propuestas documentales; no rediseño implementado.
- [Plan](docs/PLAN.md), [matriz](docs/MATRIZ_ENTREGABLES.md), [decisiones](docs/DECISIONES_TECNICAS.md) y [diagrama actual editable](docs/MODELO_DATOS.mmd).

No hay despliegue cloud, pruebas de carga, recepción, QR con cámara ni estadísticas operativas. Rate limiting actual por proceso; HSTS de subdominios/preload sigue pendiente. Android no está disponible en el repositorio y no se modificó el original ni se contactó al VPS. F3 requiere aprobación nueva; F6–F8 siguen sin autorización.
