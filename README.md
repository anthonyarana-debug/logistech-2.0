# LogisTech 2.0

Repositorio privado: [anthonyarana-debug/logistech-2.0](https://github.com/anthonyarana-debug/logistech-2.0), main predeterminada y F0–F5 publicados. Ver [publicación verificada](docs/PUBLICACION_GITHUB.md), [auditoría previa](docs/AUDITORIA_GITHUB.md) e [instrucciones para otra computadora](docs/NUEVA_COMPUTADORA.md). Las credenciales, bases y volúmenes locales se recrean o transfieren por un canal privado separado, nunca por Git. GitHub aloja el código; la aplicación no se desplegó en cloud.

Proyecto académico de Desarrollo de Soluciones en la Nube — TECSUP. **Fase 5: validación local aprobada, entrega global PARCIAL por cloud.** Industrial Precision, React, autenticación y CRUD sobre PostgreSQL. 156 pruebas backend, 5 JS y 9 E2E; Locust 50/100 con resultados reales. Sin despliegue externo. F6–F8 requieren nueva autorización.

Documentación de evaluación: [INFORME_FASE_5](docs/INFORME_FASE_5.md), [CHECKLIST_SEMANA_11](docs/CHECKLIST_SEMANA_11.md), [GUIA_DEMOSTRACION](docs/GUIA_DEMOSTRACION.md), [REPORTE_RENDIMIENTO](docs/REPORTE_RENDIMIENTO.md) y [DESPLIEGUE](docs/DESPLIEGUE.md).

## Validación F5 reproducible

El Compose principal sigue en 5173/8000. Para no consumir sus ventanas ni mezclar datos, usar proyecto separado; no omitir `-p logistech-f5`:

```powershell
docker compose -p logistech-f5 -f docker-compose.yml -f compose.validation.yml up -d --build --wait db
docker compose -p logistech-f5 -f docker-compose.yml -f compose.validation.yml run --rm --no-deps backend python manage.py migrate --noinput
docker compose -p logistech-f5 -f docker-compose.yml -f compose.validation.yml up -d --build --wait --wait-timeout 120
docker compose -p logistech-f5 -f docker-compose.yml -f compose.validation.yml exec -T backend python manage.py create_demo --namespace f5-validacion --output /tmp/f5-demo.json
docker compose -p logistech-f5 -f docker-compose.yml -f compose.validation.yml cp backend:/tmp/f5-demo.json .env.f5-demo.json
```

Si namespace/archivo ya existe, conservarlo; no repetir creación ni sustituir claves. Restringir ACL como se explica en la demostración F4. Validación publica solo puertos temporales loopback 8001/5174, PostgreSQL permanece privado. Mantiene los límites reales; no reiniciarlo repetidamente para obtener resultados mejores.

E2E (nombres de evidencias F5, sin sobrescribir F1–F4):

```powershell
Set-Location frontend
$env:PW_BASE_URL='http://127.0.0.1:5174'
$env:PW_DEMO_FILE='../.env.f5-demo.json'
$env:PW_EVIDENCE_PREFIX='fase5'
$env:PW_REPORT='../docs/evidencias/local/fase5-e2e-final.json'
npm run test:e2e
Set-Location ..
python scripts/verificar_fase5.py
```

El verificador espera los reportes E2E inicial/final conservados localmente en esta sesión; si no existen en un checkout nuevo, registrar primero la ejecución final y omitir la inicial histórica ausente, según el script. No inventar una regresión inicial aprobada. E2E de expiración tarda unos seis minutos; registros/límites requieren esperar ventanas entre ejecuciones. Para nuevas series usar nombres nuevos, no sobrescribir los resultados ya versionados.

Carga solo después del humo, con servicios de validación saludables y sin otras suites intensivas:

```powershell
.venv/Scripts/python.exe -m venv .venv-load
.venv-load/Scripts/python.exe -m pip install -r load-requirements.txt
.venv-load/Scripts/python.exe load/run.py --scenario smoke
.venv-load/Scripts/python.exe load/run.py --scenario a-50
.venv-load/Scripts/python.exe load/run.py --scenario b-100
python scripts/resumir_carga_fase5.py
```

load-requirements.txt fija el generador **Windows/Python 3.13**, separado de Django. No instalarlo como requirements del backend. Un login HTTP por escenario; demás JWT de fixtures, sin aumentar TTL o cambiar seguridad. Datos/cuentas limitados a su namespace; cuentas retiradas al terminar y manifiestos privados eliminados. CSV iniciales con incidencia de cierre conservados; exportador corregido probado en humo posterior. Ver reporte para qué mide y qué no.

Al terminar: `docker compose -p logistech-f5 -f docker-compose.yml -f compose.validation.yml stop`. Conserva volumen/evidencia para revisión, cierra puertos temporales y no afecta la demo principal. No usar down -v. Ninguno de estos comandos crea infraestructura cloud.

## Iniciar localmente

La landing presenta las funciones actuales y futuras; `/app` requiere sesión. El superadmin selecciona ámbito; administradores y operadores quedan en su empresa. El operador consulta categorías y registra/edita cajas, sin eliminarlas. Los estados finales son inmutables. Productos/sucursales se seleccionan por nombres y SKU desde `/api/v1/references/`; no se introducen UUID manualmente.

### Demostración F4 y comprobaciones

Después del arranque, crear datos **solo en una base local académica** con un namespace nuevo:

```powershell
docker compose exec -T backend python manage.py create_demo --namespace mi-demo-f4 --output /tmp/logistech-demo.json
docker compose cp backend:/tmp/logistech-demo.json .env.demo.json
$demoOwner = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
icacls .env.demo.json /inheritance:r /grant:r "${demoOwner}:(F)"
```

El comando crea dos empresas rotuladas DEMO, seis categorías, seis productos, cuatro sucursales, doce cajas y cuatro usuarios: root, administrador, operador asignado y operador pendiente. Genera claves aleatorias, hashes reales y archivo exclusivo 0600 dentro de Linux; rechaza namespace/archivo existentes. La copia Windows recibe ACL del usuario con el comando anterior. Abrir `.env.demo.json` únicamente en un editor local para consultar las credenciales, nunca pegarlas en chats o capturas. Está excluido de Git. La ejecución de esta fase usó `f4-20261027`; los E2E posteriores añadieron registros de prueba identificables.

Pruebas con servicios saludables:

```powershell
python scripts/verificar_fase4.py
Set-Location frontend
npm ci
npx playwright install chromium
npm run test:unit
npm run test:e2e
```

E2E necesita `.env.demo.json`, usa PostgreSQL real y modifica exclusivamente esos datos demo; el registro público crea cuentas `e2e-...@example.test` sin empresa. No ejecutar contra producción. Respeta límites activos: el login puede esperar Retry-After; el registro permite tres intentos/hora/IP y refresh treinta/hora/IP. No repetir toda la suite dentro de esa ventana sin esperar. El caso de expiración dura unos seis minutos. No hay trazas, vídeos ni storageState con secretos; los informes de ejecución permanecen ignorados. Evidencias saneadas y capturas en `docs/evidencias/`; resultados y límites en [INFORME_FASE_4.md](docs/INFORME_FASE_4.md).

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

- [Plataforma web](http://127.0.0.1:5173), [acceso](http://127.0.0.1:5173/login) y [estado](http://127.0.0.1:5173/estado).
- [Readiness con PostgreSQL](http://127.0.0.1:8000/api/v1/health/) y [liveness](http://127.0.0.1:8000/api/v1/health/live/).
- API de autenticación: `/api/v1/auth/`; ver [ENDPOINTS.md](docs/ENDPOINTS.md).
- CRUD JWT: `/api/v1/categories/` y `/api/v1/boxes/`, con detalle por UUID; filtros, permisos y ejemplos en ENDPOINTS.
- [Admin restringido](http://127.0.0.1:8000/admin/): superadministrador creado mediante prompt seguro, nunca con credenciales fijas.

Solo web/API publican puertos, enlazados a 127.0.0.1. PostgreSQL no publica 5432 y usa red interna; procesos web sin root. Este Compose utiliza servidores de desarrollo y **no representa un despliegue de producción**.

Si Docker no responde: abrir Docker Desktop, habilitar Settings → General → Use the WSL 2 based engine y usar Linux containers. `docker desktop start`, `docker desktop status` y `wsl --status` ayudan al diagnóstico. Confirmar que docker info muestra `linux`, no solo la versión de la CLI. La habilitación de virtualización/WSL o un reinicio, si fueran necesarios, requieren intervención del usuario.

## Verificar Fase 3

```powershell
python scripts/verificar_fase3.py
```

Registra comandos/códigos/salidas en `docs/evidencias/fase3-verificacion.json`, sin contraseñas, tokens o cookies. Incluye PostgreSQL, migraciones, suite, lint/build y comprobaciones HTTP. El CRUD por HTTP real se prueba en servidor efímero con DB test_ separada; no crea inventario permanente. Los verificadores F1/F2 conservan su evidencia histórica.

Comprobaciones individuales:

```powershell
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py migrate --check
docker compose exec -T backend python manage.py makemigrations --check --dry-run
docker compose exec -T backend python -m pytest --ds=config.settings.testing -q -o cache_dir=/tmp/pytest-f3
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm run build
```

pytest crea una base PostgreSQL test_ desde cero y la elimina al terminar. No usar esta configuración contra producción. F1/F2 son reproducibles desde sus commits históricos; los verificadores actuales no sobrescriben sus reportes.

## Usuario y administración

`accounts.User` existe desde `accounts/0001_initial.py`, con `AUTH_USER_MODEL=accounts.User` configurado antes de migrar. No se creó auth_user; el check E001 previene habilitarlo por accidente. Los grupos/permisos de auth no conceden por sí solos acceso global de negocio.

```powershell
docker compose exec backend python manage.py createsuperuser
```

Introducir correo y contraseña directamente en el prompt. Solo SUPERADMIN activo con flags coherentes entra al Admin. Allí puede crear empresas/sucursales/productos mínimos y asignar empresa/rol a operadores. No enviar credenciales al chat. No se creó un superadministrador automáticamente.

Registro público: solo operador sin empresa; rechaza campos privilegiados. Access JWT dura 5 minutos y vive en memoria; refresh de un día en cookie HttpOnly, rotado y revocado al cerrar sesión. POST de autenticación exige CSRF; la web inicia con GET `/auth/csrf/` y restaura la sesión al recargar. Sin empresa, muestra asignación pendiente sin consultar inventarios.

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

- [Informe F3](docs/INFORME_FASE_3.md), [pruebas](docs/PRUEBAS.md), [base de datos](docs/BASE_DE_DATOS.md), [seguridad](docs/SEGURIDAD.md), [roles](docs/ROLES_PERMISOS.md) y [despliegue pendiente](docs/DESPLIEGUE.md).
- [Industrial Precision y brief Stitch](docs/DISENO_UI_UX.md): A como base con recursos oscuros de B, sin segundo tema. Los bocetos son antecedentes documentales; no rediseño implementado.
- [Plan](docs/PLAN.md), [matriz](docs/MATRIZ_ENTREGABLES.md), [decisiones](docs/DECISIONES_TECNICAS.md) y [diagrama actual editable](docs/MODELO_DATOS.mmd).

No hay despliegue cloud, pruebas de carga, recepción, QR con cámara ni estadísticas operativas. Marcas iniciales de estado no equivalen a un módulo de recepción. Rate limiting por proceso; HSTS de subdominios/preload pendiente. Android no está disponible y no se modificó el original ni se contactó al VPS. F4/F5 requieren aprobación; F6–F8 siguen sin autorización.
