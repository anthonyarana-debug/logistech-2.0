param([string]$EnvFile = '.env.f7-candidate')
$ErrorActionPreference = 'Stop'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    $env:SOURCE_REF = 'week13-local'
    $env:PUBLIC_DOMAIN = 'localhost'
    $env:PUBLIC_ORIGIN = 'https://localhost:8453'
    $env:POSTGRES_DB = 'logistech'
    $env:F7_BACKUP_DIR = './backups/week13'
    New-Item -ItemType Directory -Force $env:F7_BACKUP_DIR | Out-Null
    $taskCompose = @('-p','logistech-week13','--env-file',$EnvFile,'-f','compose.production.yml',
        '-f','compose.production-rehearsal.yml','-f','compose.week13.yml')
    docker compose @taskCompose build db backend proxy
    if ($LASTEXITCODE) { throw 'Build failed.' }
    docker compose @taskCompose up -d --wait db
    if ($LASTEXITCODE) { throw 'Database startup failed.' }
    docker compose @taskCompose --profile tools run --rm --no-deps migration
    if ($LASTEXITCODE) { throw 'Migration failed.' }
    docker compose @taskCompose up -d --wait backend proxy
    if ($LASTEXITCODE) { throw 'Application startup failed.' }
    Write-Output 'Local rehearsal is available at https://localhost:8453'
} finally {
    Pop-Location
}
