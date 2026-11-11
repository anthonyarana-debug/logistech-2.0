param(
    [ValidateSet('Paginacion','CRUD','Registro','Cajas','Historial','Salud')]
    [string]$Escenario = 'Paginacion',
    [ValidateSet(0,1,2,3,100,500,1000,2500,5000)]
    [int]$Cantidad = 0
)

$perfiles = @{
    100  = @{ VUs = 2; DurationSeconds = 70 }
    500  = @{ VUs = 5; DurationSeconds = 100 }
    1000 = @{ VUs = 10; DurationSeconds = 110 }
    2500 = @{ VUs = 10; DurationSeconds = 240 }
    5000 = @{ VUs = 20; DurationSeconds = 270; PaceSeconds = 0.97 }
}
$escenarios = @{
    CRUD = 'crud'; Registro = 'register'; Cajas = 'boxes'
    Historial = 'history'; Salud = 'recovery'
}

if ($Escenario -eq 'Paginacion') {
    if ($Cantidad -eq 0) { $Cantidad = 100 }
    if (-not $perfiles.ContainsKey($Cantidad)) {
        throw 'Use 100, 500, 1000, 2500 or 5000 for pagination.'
    }
    $parametros = $perfiles[$Cantidad].Clone()
    $parametros.Scenario = 'get'
    $parametros.Rows = 10000
    $parametros.Page = 400
} else {
    if ($Cantidad -eq 0) { $Cantidad = 2 }
    if ($Cantidad -gt 3) { throw 'Use 1, 2 or 3 for this demonstration.' }
    $parametros = @{ Scenario = $escenarios[$Escenario]; Rows = 0; VUs = 1; DurationSeconds = 45 }
}
$parametros.Iterations = $Cantidad

$motor = (Get-Process -Id $PID).Path
& $motor -NoProfile -File (Join-Path $PSScriptRoot 'run_week13_load.ps1') @(
    '-Scenario', $parametros.Scenario, '-Iterations', $parametros.Iterations,
    '-Rows', $parametros.Rows, '-VUs', $parametros.VUs,
    '-DurationSeconds', $parametros.DurationSeconds,
    '-Page', $(if ($parametros.Page) { $parametros.Page } else { 1 }),
    '-PaceSeconds', $(if ($parametros.PaceSeconds) { $parametros.PaceSeconds } else { 0.6 })
)
exit $LASTEXITCODE
