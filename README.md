# LogisTech 2.0

Proyecto académico de Desarrollo de Soluciones en la Nube — TECSUP. Plataforma logística en construcción. **Fase 1: configuración local**, sin registro, login, CRUD ni inventario todavía.

## Inicio con Docker Desktop

Requiere Docker Desktop con motor Linux y Docker Compose. Ejecutar desde la raíz:

```powershell
docker info --format '{{.OSType}} {{.ServerVersion}}'
python scripts/configurar_entorno.py
docker compose config --quiet
docker compose up -d --build --wait --wait-timeout 180
docker compose ps
```

El generador solo usa la biblioteca estándar de Python, crea `.env` con secretos aleatorios, no los imprime y se niega a sobrescribir un archivo existente. `.env.example` contiene únicamente valores ficticios. No copies sus marcadores como contraseñas reales. No compartas `.env` ni ejecutes `docker compose config` sin `--quiet` en salidas que vayas a publicar: la configuración expandida incluye secretos.

- Web: [http://127.0.0.1:5173](http://127.0.0.1:5173).
- API preparada: [health con PostgreSQL](http://127.0.0.1:8000/api/v1/health/) y [proceso vivo](http://127.0.0.1:8000/api/v1/health/live/).
- PostgreSQL no tiene puerto publicado en el equipo. Las consultas se realizan desde la red interna de Compose.

Frontend y backend se ejecutan como usuarios no privilegiados. Sus puertos se enlazan exclusivamente a `127.0.0.1`. La web consulta `/api/v1` mediante el proxy de desarrollo Vite; no necesita abrir CORS. Esta configuración usa servidores de desarrollo y **no es un despliegue de producción**.

## Si Docker no responde

Abre Docker Desktop y espera a que el motor esté funcionando. En Settings → General activa **Use the WSL 2 based engine**. Si el menú ofrece **Switch to Linux containers**, selecciónalo. Si falta WSL 2 o virtualización, sigue el diagnóstico de Docker Desktop y sus instrucciones de Windows; puede requerir habilitación por el usuario y reinicio. No modificar BIOS ni características del sistema sin revisar ese diagnóstico.

```powershell
docker desktop start
docker desktop status
wsl --status
docker info --format '{{.OSType}} {{.ServerVersion}}'
```

Debe responder `linux` y una versión del servidor. Una versión correcta de la CLI no demuestra que el motor esté disponible. En esta sesión el arranque mediante CLI resolvió el problema inicial.

## Verificaciones reproducibles

Con los contenedores saludables:

```powershell
python scripts/verificar_fase1.py
```

Guarda resultados y salidas en `docs/evidencias/fase1-verificacion.json`; no guarda la configuración expandida ni secretos. Ejecuta comprobaciones Django, conexión PostgreSQL, migraciones iniciales, ocho pruebas, Ruff, build/lint frontend, HTTP y restricciones de puertos. Las dos advertencias HSTS de producción se conservan en la evidencia. Para una comprobación individual:

```powershell
docker compose exec -T backend python manage.py check
docker compose exec -T backend python -m pytest --ds=config.settings.testing -q -o cache_dir=/tmp/logistech-pytest-cache
docker compose exec -T frontend npm run build
```

Las pruebas de integración crean y eliminan una base `test_` separada; no usar esta configuración contra una base de producción. El usuario PostgreSQL creado por la imagen es administrador de la instancia local; separar un rol de aplicación sin privilegios de creación de bases antes de producción.

Para comprobaciones Python fuera de Docker, crear un entorno sin paquetes globales:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements-dev.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\ruff.exe check --config backend/pyproject.toml backend scripts
```

Desde `backend/`, `..\.venv\Scripts\python.exe -m pytest --ds=config.settings.testing -m 'not integration' -q` ejecuta solo pruebas sin PostgreSQL real. Esto no sustituye la integración en Docker. Django local no carga `.env` automáticamente: Compose sí inyecta las variables. No se añadió una dependencia dotenv al backend.

El frontend usa dependencias locales y `package-lock.json`: desde `frontend/`, `npm ci`, `npm run lint`, `npm run build`. Si se usa `npm run dev` fuera del contenedor, configurar previamente `$env:API_PROXY_TARGET='http://127.0.0.1:8000'`; dentro de Docker el destino es `backend:8000`.

## Migraciones y usuario personalizado

F1 no instala `django.contrib.auth`, Admin, sesiones ni contenttypes. `migrate` funciona y no tiene migraciones que aplicar; la base de la aplicación permanece sin tablas. No se creó `auth_user`.

En F2 crear `accounts.User`, fijar `AUTH_USER_MODEL='accounts.User'` y generar el usuario en `accounts/0001_initial.py` **antes** de habilitar/aplicar auth/admin y sus dependencias. Un system check (`logistech.E001`) rechaza habilitar auth con `auth.User`. No usar `--skip-checks` para omitirlo. La prueba JWT usa un proceso separado para importar la biblioteca; no conecta a la base ni ejecuta migraciones.

## Versiones verificadas

| Componente | Versión |
|---|---|
| Python, venv y contenedor | 3.13.17 |
| Django / DRF | 5.2.18 / 3.16.1 |
| Simple JWT / PyJWT | 5.5.1 / 2.15.1 |
| psycopg / PostgreSQL | 3.3.6 / 17.11 |
| Node / React / Vite | 24.19.0 / 19.3.1 / 8.3.5 |
| Tailwind / React Router DOM | 4.3.3 / 7.18.4 |

`requirements.in` y `requirements-dev.in` explicitan dependencias directas; los `.txt` fijan también transitivas. `requirements-dev.txt` incluye las de ejecución. Las imágenes usan etiquetas de versión; estas etiquetas pueden recibir actualizaciones del proveedor y no son digests inmutables. Consultar [decisiones técnicas](docs/DECISIONES_TECNICAS.md).

## Operación local y alcance

```powershell
docker compose stop
docker compose up -d --wait
```

`stop` conserva contenedores y volumen. No usar `down -v` como rutina: elimina los datos persistidos. Los archivos fuente están incorporados a las imágenes; después de cambiarlos ejecutar `docker compose up -d --build --wait`.

No hay auditoría Android corroborada: no se encontró el proyecto original en este repositorio y no se modificó ningún proyecto vecino. No se conectó al VPS anterior ni a infraestructura cloud.

Documentación: [informe de F1](docs/INFORME_FASE_1.md), [pruebas](docs/PRUEBAS.md), [despliegue pendiente](docs/DESPLIEGUE.md), [plan](docs/PLAN.md), [matriz](docs/MATRIZ_ENTREGABLES.md). La Fase 2 requiere aprobación del usuario.
