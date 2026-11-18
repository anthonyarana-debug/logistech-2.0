# Ejecuta load/nube.js con k6 en Docker contra el servidor en la nube.
# Ejemplos:
#   .\scripts\run_cloud_load.ps1 -Scenario register -Iterations 200 -VUs 10 -Duration 60s
#   .\scripts\run_cloud_load.ps1 -Scenario get -Iterations 10000 -VUs 10 -Duration 30s -Email admin@... -Password ...
#   .\scripts\run_cloud_load.ps1 -Ladder register      (50, 100, 200, 500, 1000)
#   .\scripts\run_cloud_load.ps1 -Ladder get           (100, 1000, 5000, 10000, 25000, 50000)
param(
  [ValidateSet('register', 'login', 'get', 'mixed')] [string]$Scenario = 'register',
  [int]$Iterations = 100,
  [int]$VUs = 10,
  [string]$Duration = '60s',
  [string]$BaseUrl = 'https://logistech.stackpe.online',
  [string]$Email = $env:K6_EMAIL,
  [string]$Password = $env:K6_PASSWORD,
  [ValidateSet('', 'register', 'get', 'mixed')] [string]$Ladder = '',
  [string]$K6Image = 'grafana/k6:1.5.0',
  [int]$PauseSeconds = 20,
  [string]$Network = '',      # red Docker opcional (prueba local con scripts/test_cloud_load_local.ps1)
  [string]$ResultsDir = ''    # por defecto docs/evidencias/semana13-nube
)
# Continue: en PowerShell 5.1 el stderr de docker/k6 no debe cortar la escalera.
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
$results = if ($ResultsDir) { $ResultsDir } else { Join-Path $root 'docs/evidencias/semana13-nube' }
New-Item -ItemType Directory -Force $results | Out-Null
$runId = Get-Date -Format 'MMddHHmmss'

function Invoke-K6([string]$scenario, [int]$iterations, [int]$vus, [string]$duration) {
  $vus = [Math]::Min($vus, $iterations)
  $tag = "$scenario-$iterations-${vus}vu"
  $stepId = "${runId}s$iterations"   # correos únicos por escalón: k6-<stepId>-<n>@example.test
  Write-Host "`n>>> $tag  (tiempo max $duration, RUN_ID $runId)" -ForegroundColor Cyan
  $envArgs = @('-e', "BASE_URL=$BaseUrl", '-e', "SCENARIO=$scenario", '-e', "ITERATIONS=$iterations",
    '-e', "VUS=$vus", '-e', "DURATION=$duration", '-e', "RUN_ID=$stepId", '-e', "TAG=$tag")
  if ($Email) { $envArgs += @('-e', "EMAIL=$Email", '-e', "PASSWORD=$Password") }
  $netArgs = if ($Network) { @('--network', $Network) } else { @() }
  docker run --rm @netArgs -v "${root}/load:/scripts:ro" -v "${results}:/results" @envArgs $K6Image run --quiet /scripts/nube.js
  # k6 devuelve 99 cuando un umbral falla: se registra igual, no se detiene la escalera.
  if ($LASTEXITCODE -notin 0, 99) { Write-Warning "k6 terminó con código $LASTEXITCODE en $tag" }
}

if ($Ladder -eq 'register') {
  foreach ($n in 50, 100, 200, 500, 1000) { Invoke-K6 'register' $n 10 '300s'; Start-Sleep $PauseSeconds }
} elseif ($Ladder -eq 'get') {
  foreach ($n in 100, 1000, 5000, 10000, 25000, 50000) { Invoke-K6 'get' $n 20 '600s'; Start-Sleep $PauseSeconds }
} elseif ($Ladder -eq 'mixed') {
  foreach ($n in 100, 1000, 5000) { Invoke-K6 'mixed' $n 20 '600s'; Start-Sleep $PauseSeconds }
} else {
  Invoke-K6 $Scenario $Iterations $VUs $Duration
}

python (Join-Path $PSScriptRoot 'summarize_cloud_load.py') $results
Write-Host "`nRUN_ID=$runId  -> en el servidor: python manage.py load_test_users --prefix k6-$runId" -ForegroundColor Green
