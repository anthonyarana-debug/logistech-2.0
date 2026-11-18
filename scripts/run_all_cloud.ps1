# Corre la tanda completa en la nube: lecturas, escalera de registro y caso 10 000 / 30 s.
# Lee el token y las credenciales de un archivo FUERA del repositorio (nunca se commitea):
#   %USERPROFILE%\.logistech-k6-env.ps1  con estas tres líneas:
#     $env:K6_LOAD_TEST_TOKEN = '...'
#     $env:K6_EMAIL = '...'
#     $env:K6_PASSWORD = '...'
param([switch]$SkipGet, [switch]$SkipRegister, [switch]$SkipTeacher)
$ErrorActionPreference = 'Continue'
$envFile = Join-Path $env:USERPROFILE '.logistech-k6-env.ps1'
if (-not (Test-Path $envFile)) { Write-Error "Falta $envFile"; exit 1 }
. $envFile
if ($env:K6_LOAD_TEST_TOKEN.Length -ne 64) { Write-Error 'El token debe tener 64 caracteres.'; exit 1 }
if (-not ($env:K6_EMAIL -and $env:K6_PASSWORD)) { Write-Error 'Faltan K6_EMAIL o K6_PASSWORD.'; exit 1 }
Write-Host "Token OK (64), cuenta $($env:K6_EMAIL)" -ForegroundColor Green

$runner = Join-Path $PSScriptRoot 'run_cloud_load.ps1'
if (-not $SkipGet) { & $runner -Ladder get }
if (-not $SkipRegister) { & $runner -Ladder register }
if (-not $SkipTeacher) { & $runner -Scenario register -Iterations 10000 -VUs 10 -Duration 30s }

Remove-Item Env:K6_LOAD_TEST_TOKEN, Env:K6_EMAIL, Env:K6_PASSWORD -ErrorAction SilentlyContinue
Write-Host "`n=== TANDA TERMINADA $(Get-Date -Format o) ===" -ForegroundColor Green
