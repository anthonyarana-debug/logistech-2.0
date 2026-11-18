# Prueba local de las pruebas de carga ANTES de usarlas contra AWS.
# Levanta PostgreSQL + backend (con LOAD_TEST_MODE=true) en Docker, ejecuta k6
# con run_cloud_load.ps1, cuenta los usuarios creados y borra todo al final.
# No toca la nube ni tu base de datos local. Requiere Docker Desktop encendido.
#   .\scripts\test_cloud_load_local.ps1
#   .\scripts\test_cloud_load_local.ps1 -Iterations 1000 -VUs 10 -Duration 30s
#   .\scripts\test_cloud_load_local.ps1 -Scenario get -Iterations 5000
#   .\scripts\test_cloud_load_local.ps1 -Ladder register
#   .\scripts\test_cloud_load_local.ps1 -Ladder register -SinToken   (demuestra el corte por cuota)
param(
  [ValidateSet('register', 'login', 'get', 'mixed')] [string]$Scenario = 'register',
  [int]$Iterations = 200,
  [int]$VUs = 10,
  [string]$Duration = '60s',
  [ValidateSet('', 'register', 'get', 'mixed')] [string]$Ladder = '',
  [string]$TestImage = 'logistech-week13-tests:local',
  [switch]$KeepRunning,
  [switch]$SinToken   # simula olvidar el token: debe verse "cuota/429" y la escalera debe detenerse
)
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
$net = 'logistech-k6-local'
$results = Join-Path $env:TEMP 'logistech-k6-local'
$adminEmail = 'root-k6@example.test'
$adminPassword = 'RootK6!local_solo_pruebas_2026'
# Token aleatorio de esta corrida (equivale al LOAD_TEST_TOKEN del servidor).
$env:LOAD_TEST_TOKEN = -join ((1..48) | ForEach-Object { '{0:x}' -f (Get-Random -Maximum 16) })

function Remove-Stack {
  docker rm -f k6-backend k6-db 2>$null | Out-Null
  docker network rm $net 2>$null | Out-Null
}

docker info *> $null
if ($LASTEXITCODE -ne 0) { Write-Error 'Docker Desktop no está encendido.'; exit 1 }
docker image inspect $TestImage *> $null
if ($LASTEXITCODE -ne 0) { Write-Error "No existe la imagen $TestImage."; exit 1 }

Remove-Stack
Remove-Item -Recurse -Force $results -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $results | Out-Null
docker network create $net | Out-Null

Write-Host 'Levantando PostgreSQL...' -ForegroundColor Cyan
docker run -d --rm --name k6-db --network $net -e POSTGRES_DB=logistech -e POSTGRES_USER=logistech `
  -e POSTGRES_PASSWORD=solo-pruebas-no-es-un-secreto-real postgres:17-alpine | Out-Null
for ($i = 0; $i -lt 30; $i++) { docker exec k6-db pg_isready -U logistech *> $null; if ($LASTEXITCODE -eq 0) { break }; Start-Sleep 2 }
Start-Sleep 3

Write-Host 'Levantando backend con LOAD_TEST_MODE=true y token...' -ForegroundColor Cyan
docker run -d --rm --name k6-backend --network $net --network-alias backend -v "${root}/backend:/app:ro" -w /app --tmpfs /tmp `
  -e PYTHONDONTWRITEBYTECODE=1 -e DJANGO_SETTINGS_MODULE=config.settings.testing -e DB_HOST=k6-db `
  -e LOAD_TEST_MODE=true -e LOAD_TEST_TOKEN $TestImage sh -c 'python manage.py migrate -v0 && python manage.py runserver 0.0.0.0:8000 --noreload' | Out-Null
$ready = $false
for ($i = 0; $i -lt 60; $i++) {
  if ((docker logs k6-backend 2>&1 | Out-String) -match 'Starting development server') { $ready = $true; break }
  Start-Sleep 2
}
if (-not $ready) { docker logs k6-backend; Remove-Stack; Write-Error 'El backend no arrancó.'; exit 1 }

docker exec k6-backend python manage.py shell -c "from apps.accounts.models import User; User.objects.create_superuser('$adminEmail', '$adminPassword', role='SUPERADMIN')" 2>$null | Out-Null

# 'backend' está en ALLOWED_HOSTS de config.settings.testing.
$env:K6_LOAD_TEST_TOKEN = if ($SinToken) { '' } else { $env:LOAD_TEST_TOKEN }
$env:K6_EMAIL = $adminEmail
$env:K6_PASSWORD = $adminPassword
$params = @{ BaseUrl = 'http://backend:8000'; Network = $net; ResultsDir = $results; PauseSeconds = 2 }
if ($Ladder) { $params.Ladder = $Ladder } else {
  $params += @{ Scenario = $Scenario; Iterations = $Iterations; VUs = $VUs; Duration = $Duration } }
& (Join-Path $PSScriptRoot 'run_cloud_load.ps1') @params

Remove-Item Env:K6_LOAD_TEST_TOKEN, Env:K6_EMAIL, Env:K6_PASSWORD, Env:LOAD_TEST_TOKEN -ErrorAction SilentlyContinue

Write-Host "`nTráfico público SIN token durante la ventana (debe dar 429 al 4.º registro):" -ForegroundColor Cyan
$probe = @'
import http.cookiejar, json, urllib.error, urllib.request
jar = http.cookiejar.CookieJar(); op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
base = "http://backend:8000/api/v1"
token = json.load(op.open(base + "/auth/csrf/"))["csrfToken"]
codes = []
for n in range(4):
    req = urllib.request.Request(base + "/auth/register/", data=b"{}", method="POST",
        headers={"Content-Type": "application/json", "X-CSRFToken": token, "Origin": "http://backend:8000"})
    try: codes.append(op.open(req).status)
    except urllib.error.HTTPError as e: codes.append(e.code)
print("Codigos sin token:", codes, "-> OK, el publico sigue limitado" if codes[-1] == 429 else "-> ERROR: no se aplico el limite")
'@
$probe | docker exec -i k6-backend python -

Write-Host "`nUsuarios creados en PostgreSQL (verificación en la BD):" -ForegroundColor Cyan
docker exec k6-backend python manage.py load_test_users --prefix k6-
docker exec k6-db psql -U logistech -d logistech -c "SELECT count(*) AS usuarios_k6 FROM accounts_user WHERE email LIKE 'k6-%@example.test';"

Write-Host "`nGráficas: $results\resumen.html" -ForegroundColor Green
if ($KeepRunning) {
  Write-Host 'Entorno activo. Para borrarlo: docker rm -f k6-backend k6-db; docker network rm logistech-k6-local'
} else {
  Remove-Stack
  Write-Host 'Entorno local eliminado (los resultados se conservan).'
}
