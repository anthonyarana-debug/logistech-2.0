# Continuar LogisTech 2.0 en otra computadora

Estado: [anthonyarana-debug/logistech-2.0](https://github.com/anthonyarana-debug/logistech-2.0) **publicado como PRIVATE**, con main predeterminada y F0–F5, tras autorización expresa el 27/10/2026. Clonación HTTPS autenticada comprobada. Ver [registro de publicación](PUBLICACION_GITHUB.md). Requiere iniciar sesión con una cuenta que tenga acceso privado. No usar el repositorio Android como remoto de este proyecto.

Git conservará código, documentación, migraciones, resultados saneados e historial de F0–F5. No transporta `.env`, contraseñas/cuentas DEMO, contenedores, imágenes, bases o volúmenes Docker. La otra computadora inicia con una base nueva; generar datos DEMO nuevos. Si se necesitan datos existentes, planificar un respaldo cifrado fuera de Git y una restauración separada; no se ha exportado ni eliminado la base actual.

## Requisitos

Para el arranque básico en Windows: Git for Windows con Git Credential Manager, Docker Desktop con virtualización/WSL2 y motor **Linux**, y Python 3.13 para scripts de configuración (solo biblioteca estándar). Python/Django/DRF/PostgreSQL de la aplicación están fijados y aislados en Docker; no instalarlos globalmente.

Compose debe soportar `!override` para el entorno opcional F5 (2.24.4 o posterior); comprobar `docker compose version`. Node no hace falta para el arranque básico: Docker fija Node 24.19.0. Para unitarias/E2E en el host, usar Node 24.19.x (>=24.19.0 y <25) y dependencias locales mediante npm ci. Necesitarás espacio para imágenes/volúmenes y red para descargar dependencias. No se deduce capacidad de hardware a partir de las métricas del equipo anterior.

## Clonar y arrancar (Windows / PowerShell)

Desde una carpeta de trabajo vacía o que no contenga otra copia del proyecto:

```powershell
git clone https://github.com/anthonyarana-debug/logistech-2.0.git
Set-Location logistech-2.0
git status --short --branch
git remote -v
git branch -r
git log -8 --oneline
git config --local core.hooksPath .githooks
```

Autenticarse con la cuenta autorizada mediante el flujo de Git Credential Manager. No pegar un PAT en la URL, en documentos o en el chat. Si GitHub responde Repository not found, comprobar que el remoto existe y que la cuenta tiene acceso privado. El hook es local: cada clon debe activarlo, y no protege comandos que lo omitan.

Configurar secretos nuevos sin copiarlos del repositorio:

```powershell
py -3.13 scripts/configurar_entorno.py
$localOwner = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
icacls .env /inheritance:r /grant:r "${localOwner}:(F)"
docker info --format '{{.OSType}} {{.ServerVersion}}'
docker compose config --quiet
docker compose build
docker compose up -d --wait db
docker compose run --rm --no-deps backend python manage.py migrate --noinput
docker compose up -d --wait --wait-timeout 180
docker compose ps
```

Si .env ya existe, el generador se niega a sobrescribirlo: conservarlo y revisarlo localmente, sin imprimir sus valores. No usar docker compose config sin `--quiet` en salidas compartidas: expande secretos. No confundir una CLI Docker instalada con un motor funcionando; docker info debe mostrar linux. Si falla, iniciar Docker Desktop y habilitar WSL2/Linux containers; reinicios/virtualización pueden requerir intervención local.

Abrir `http://127.0.0.1:5173` y `http://127.0.0.1:5173/estado`. Readiness: `http://127.0.0.1:8000/api/v1/health/` debe devolver 200. Web/API solo loopback; PostgreSQL no publica 5432. Este entorno es de desarrollo local, no despliegue cloud.

En Linux/macOS, usar python3 (3.13) en lugar de py, y `chmod 600 .env` en lugar de icacls. El resto de los comandos Compose es equivalente. No reutilizar el lock Windows de Locust para instalar herramientas del backend Linux.

## Datos y cuentas locales nuevos

Crear una demostración con namespace nuevo; nunca reutilizar valores de contraseñas compartidos:

```powershell
docker compose exec -T backend python manage.py create_demo --namespace nueva-pc-demo --output /tmp/nueva-pc-demo.json
docker compose cp backend:/tmp/nueva-pc-demo.json .env.demo.json
icacls .env.demo.json /inheritance:r /grant:r "${localOwner}:(F)"
```

Consultar las cuentas/contraseñas únicamente en un editor local, antes de compartir pantalla. El comando crea claves aleatorias, dos empresas DEMO y usuarios root/admin/operator/pending; rehúsa sobrescribir el archivo o namespace. Estos usuarios y sus UUID serán diferentes a los del equipo anterior; las capturas históricas no representan esa nueva base.

Para una cuenta administrativa distinta puede usarse `docker compose exec backend python manage.py createsuperuser` mediante prompt privado. No es necesario transferir el archivo de credenciales DEMO original ni el volumen PostgreSQL para continuar programando.

## Comprobaciones y navegador

```powershell
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py migrate --check
docker compose exec -T backend python manage.py makemigrations --check --dry-run
docker compose exec -T backend python -m pytest --ds=config.settings.testing -q -o cache_dir=/tmp/pytest-nueva-pc
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm run build
py -3.13 scripts/auditar_publicacion.py
```

Para pruebas frontend desde el host:

```powershell
Set-Location frontend
npm ci
npm run test:unit
npx playwright install chromium
Set-Location ..
```

Los E2E/Locust modifican solo DEMO y consumen límites reales. Usar el proyecto aislado F5 del README y sus variables PW_BASE_URL/PW_DEMO_FILE; no apuntarlos al Android ni a producción. El caso de expiración espera cinco minutos; el registro permite 3/hora/IP y refresh 30/hora/IP. No repetir ejecuciones para forzar resultados ni sobreescribir evidencia histórica. Para una ejecución nueva elegir nombres/reportes nuevos.

Los informes de F5 son evidencia histórica, no garantía del nuevo equipo. El verificador F5 consulta los reportes crudos disponibles y conserva los históricos ausentes; distinguir la fecha y entorno de cada resultado. Las métricas anteriores no acreditan cloud activo.

## Mantener ambos equipos sincronizados

Una vez publicado main y configurado su seguimiento:

```powershell
git switch main
git pull --ff-only
git switch -c codex/mi-siguiente-tarea
# Editar, comprobar y revisar el diff.
git diff --check
py -3.13 scripts/auditar_publicacion.py
git add <archivos-revisados>
git diff --cached
git commit -m "Describe el cambio"
git push -u origin codex/mi-siguiente-tarea
```

El primer push fue autorizado y realizado el 27/10/2026. Los push futuros deben dirigirse al remoto privado confirmado. Verificar estado antes de cambiar de equipo; Git no transporta modificaciones sin commit. Resolver conflictos conservando ambos trabajos; no usar force push, reset --hard, borrado de volúmenes o mirror como rutina. Publicar ramas de trabajo y revisarlas antes de integrar a main.

En otro equipo: `git fetch origin` y `git switch --track origin/codex/mi-siguiente-tarea` para continuar una rama ya publicada. No trabajar simultáneamente sobre la misma rama sin coordinar. Mantener copias privadas de datos necesarios fuera de Git; recrear la configuración local desde la plantilla.
