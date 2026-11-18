# Menú simple de pruebas de carga en la nube (LogisTech).
# La primera vez pide token, correo y contraseña y los guarda en
# %USERPROFILE%\.logistech-k6-env.ps1 (fuera del repositorio, solo en esta PC).
# Requisitos: Docker Desktop abierto e internet. Python es opcional (solo para el resumen).
$ErrorActionPreference = 'Continue'
# Primero busca los datos dentro de la carpeta del proyecto (viajan con la copia en USB;
# están en .gitignore), luego en el perfil del usuario.
$projectEnv = Join-Path (Split-Path -Parent $PSScriptRoot) '.logistech-k6-env.ps1'
$envFile = if (Test-Path $projectEnv) { $projectEnv } else { Join-Path $env:USERPROFILE '.logistech-k6-env.ps1' }
$runner = Join-Path $PSScriptRoot 'run_cloud_load.ps1'

function Save-Datos {
  $t = Read-Host 'Token de prueba (64 caracteres, del servidor)'
  $e = Read-Host 'Correo de la cuenta (superadmin o admin)'
  $p = Read-Host 'Contraseña'
  $lines = @("`$env:K6_LOAD_TEST_TOKEN = '$($t.Trim())'", "`$env:K6_EMAIL = '$($e.Trim())'",
    "`$env:K6_PASSWORD = '$($p -replace "'", "''")'")
  Set-Content -Path $envFile -Value $lines -Encoding UTF8
  Write-Host "Datos guardados en $envFile" -ForegroundColor Green
}

docker version --format '{{.Server.Version}}' *> $null
if ($LASTEXITCODE -ne 0) { Write-Host 'Docker Desktop no está abierto. Ábrelo y vuelve a intentar.' -ForegroundColor Red; Read-Host 'Enter para salir'; exit 1 }
if (-not (Test-Path $envFile)) { Save-Datos }

while ($true) {
  . $envFile
  Write-Host "`n=== LogisTech - pruebas en la nube (cuenta $($env:K6_EMAIL)) ===" -ForegroundColor Cyan
  Write-Host ' 1) Demo rápida: 200 registros en BD (para mostrar en pgAdmin)'
  Write-Host ' 2) Lecturas 1000 (rúbrica 1000-5000 en el servidor)'
  Write-Host ' 3) Caso del profesor: 10 000 registros en 30 s con 10 VUs'
  Write-Host ' 4) Escalera completa de lecturas (100 a 50 000, larga)'
  Write-Host ' 5) Escalera de registros (50, 100, 200, 500, 1000)'
  Write-Host ' 6) Prueba sin token (demuestra el rate limit 429)'
  Write-Host ' 7) Cambiar token / correo / contraseña'
  Write-Host ' 0) Salir'
  $op = Read-Host 'Opción'
  if ($env:K6_LOAD_TEST_TOKEN.Length -ne 64 -and $op -in '1', '2', '3', '4', '5') {
    Write-Host 'El token guardado no tiene 64 caracteres: usa la opción 7.' -ForegroundColor Yellow; continue
  }
  switch ($op) {
    '1' { & $runner -Scenario register -Iterations 200 -VUs 10 -Duration 300s }
    '2' { & $runner -Scenario get -Iterations 1000 -VUs 20 -Duration 300s }
    '3' { & $runner -Scenario register -Iterations 10000 -VUs 10 -Duration 30s }
    '4' { & $runner -Ladder get }
    '5' { & $runner -Ladder register }
    '6' { $keep = $env:K6_LOAD_TEST_TOKEN; $env:K6_LOAD_TEST_TOKEN = ''
          & $runner -Scenario register -Iterations 20 -VUs 2 -Duration 60s
          $env:K6_LOAD_TEST_TOKEN = $keep }
    '7' { Save-Datos }
    '0' { break }
    default { Write-Host 'Opción no válida.' }
  }
  if ($op -eq '0') { break }
}
