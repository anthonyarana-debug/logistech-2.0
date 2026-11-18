# Ejecuta load/nube.js con k6 en Docker contra el servidor en la nube.
#
# Secretos: se leen de variables de entorno y se pasan a Docker por nombre (-e VAR),
# nunca como valor en la línea de comandos.
#   $env:K6_LOAD_TEST_TOKEN = '<mismo LOAD_TEST_TOKEN del servidor>'
#   $env:K6_EMAIL = '...'; $env:K6_PASSWORD = '...'     # solo para get/login/mixed
#
# Ejemplos:
#   .\scripts\run_cloud_load.ps1 -Scenario register -Iterations 200 -VUs 10 -Duration 60s
#   .\scripts\run_cloud_load.ps1 -Scenario register -Iterations 10000 -VUs 10 -Duration 30s
#   .\scripts\run_cloud_load.ps1 -Ladder register      (50, 100, 200, 500, 1000)
#   .\scripts\run_cloud_load.ps1 -Ladder get           (100, 1000, 5000, 10000, 25000, 50000)
#
# La escalera se detiene en el primer escalón que no termine APROBADO (usa
# -ContinueOnFailure para seguir). k6 aborta solo si los errores superan
# -AbortErrorRate (por defecto 0.05 = 5 %) durante 10 s.
param(
  [ValidateSet('register', 'login', 'get', 'mixed')] [string]$Scenario = 'register',
  [int]$Iterations = 100,
  [int]$VUs = 10,
  [string]$Duration = '60s',
  [string]$BaseUrl = 'https://logistech.stackpe.online',
  [ValidateSet('', 'register', 'get', 'mixed')] [string]$Ladder = '',
  [string]$K6Image = 'grafana/k6:1.5.0',
  [int]$PauseSeconds = 20,
  [double]$AbortErrorRate = 0.05,
  [switch]$ContinueOnFailure,
  [string]$Network = '',      # red Docker opcional (prueba local con scripts/test_cloud_load_local.ps1)
  [string]$ResultsDir = ''    # por defecto docs/evidencias/semana13-nube
)
# Continue: en PowerShell 5.1 el stderr de docker/k6 no debe cortar el script.
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
$results = if ($ResultsDir) { $ResultsDir } else { Join-Path $root 'docs/evidencias/semana13-nube' }
New-Item -ItemType Directory -Force $results | Out-Null
$runId = Get-Date -Format 'MMddHHmmss'

# Secretos heredados por nombre: "docker run -e VAR" toma el valor de este proceso.
$env:LOAD_TEST_TOKEN = $env:K6_LOAD_TEST_TOKEN
$env:EMAIL = $env:K6_EMAIL
$env:PASSWORD = $env:K6_PASSWORD
if (-not $env:LOAD_TEST_TOKEN) {
  Write-Warning 'K6_LOAD_TEST_TOKEN no está definido: el servidor aplicará el rate limit (verás 429 como "cuota").'
}

function Invoke-K6([string]$scenario, [int]$iterations, [int]$vus, [string]$duration) {
  $vus = [Math]::Min($vus, $iterations)
  $tag = "$scenario-$iterations-${vus}vu"
  $stepId = "${runId}s$iterations"   # correos únicos por escalón: k6-<stepId>-<n>@example.test
  Write-Host "`n>>> $tag  (tiempo max $duration, RUN_ID $runId)" -ForegroundColor Cyan
  $netArgs = if ($Network) { @('--network', $Network) } else { @() }
  $envArgs = @('-e', "BASE_URL=$BaseUrl", '-e', "SCENARIO=$scenario", '-e', "ITERATIONS=$iterations",
    '-e', "VUS=$vus", '-e', "DURATION=$duration", '-e', "RUN_ID=$stepId", '-e', "TAG=$tag",
    '-e', "ABORT_ERROR_RATE=$AbortErrorRate", '-e', 'LOAD_TEST_TOKEN', '-e', 'EMAIL', '-e', 'PASSWORD')
  docker run --rm @netArgs -v "${root}/load:/scripts:ro" -v "${results}:/results" @envArgs $K6Image run --quiet /scripts/nube.js | Out-Host
  # 0 = umbrales cumplidos, 99 = umbral fallido o corte automático; ambos dejan resultados.
  if ($LASTEXITCODE -notin 0, 99) { Write-Warning "k6 terminó con código $LASTEXITCODE en $tag" }
  $rowFile = Join-Path $results "$tag-$stepId.row.json"
  if (-not (Test-Path $rowFile)) { return 'SIN RESULTADO' }
  return (Get-Content $rowFile -Raw -Encoding UTF8 | ConvertFrom-Json).resultado
}

function Invoke-Ladder([string]$scenario, [int[]]$steps, [int]$vus, [string]$duration) {
  foreach ($n in $steps) {
    $result = Invoke-K6 $scenario $n $vus $duration
    if ($result -ne 'APROBADO' -and -not $ContinueOnFailure) {
      Write-Warning "Escalera detenida en $scenario-$n ($result). Revisa el servidor antes de seguir."
      break
    }
    Start-Sleep $PauseSeconds
  }
}

if ($Ladder -eq 'register') {
  Invoke-Ladder 'register' @(50, 100, 200, 500, 1000) 10 '300s'
} elseif ($Ladder -eq 'get') {
  Invoke-Ladder 'get' @(100, 1000, 5000, 10000, 25000, 50000) 20 '600s'
} elseif ($Ladder -eq 'mixed') {
  Invoke-Ladder 'mixed' @(100, 1000, 5000) 20 '600s'
} else {
  Invoke-K6 $Scenario $Iterations $VUs $Duration | Out-Null
}

Remove-Item Env:LOAD_TEST_TOKEN, Env:EMAIL, Env:PASSWORD -ErrorAction SilentlyContinue
python (Join-Path $PSScriptRoot 'summarize_cloud_load.py') $results
Write-Host "`nRUN_ID=$runId  -> en el servidor: python manage.py load_test_users --prefix k6-$runId" -ForegroundColor Green
