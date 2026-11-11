param(
    [ValidateSet('get','crud','register','boxes','history','recovery')]
    [string]$Scenario = 'get',
    [ValidateSet(1,2,3,100,500,1000,2500,5000,10000,25000,50000)]
    [int]$Iterations = 100,
    [ValidateRange(1,20)][int]$VUs = 1,
    [ValidateRange(10,270)][int]$DurationSeconds = 240,
    [ValidateRange(0,20000)][int]$Rows = 10000,
    [ValidateRange(1,801)][int]$Page = 1,
    [ValidateRange(0.6,1.0)][double]$PaceSeconds = 0.6
)
$ErrorActionPreference = 'Continue'
$taskRoot = Split-Path $PSScriptRoot -Parent
if ($Iterations -gt 5000) { throw 'Profiles above 5000 require a separate capacity validation and token plan.' }
if ($Iterations % $VUs -ne 0) { throw 'Iterations must divide evenly across VUs.' }
$taskRequests = switch ($Scenario) { crud {4} boxes {3} register {2} default {1} }
if ($Scenario -eq 'register' -and $Iterations -gt 3) { throw 'Registration is limited to three attempts per IP and hour.' }
if ($Scenario -in @('crud','boxes') -and $Iterations -gt 100) { throw 'Local write budget is 100 iterations.' }
if (($Iterations / $VUs) * $taskRequests * ($PaceSeconds + 0.05) + 10 -gt $DurationSeconds) {
    throw 'The profile will not fit the rate limit and duration. Use more VUs or a longer duration.'
}
if ($Scenario -eq 'get' -and (($Page - 1) * 25 -ge ($Rows + 1))) { throw 'The requested page exceeds the seeded catalogue.' }
$taskDrive = Get-PSDrive -Name ([IO.Path]::GetPathRoot($taskRoot).Substring(0,1))
if ($taskDrive.Free -lt 3GB) { throw 'The workspace requires 3 GiB of free space.' }
$taskEngineMemory = docker info --format '{{.MemTotal}}'
if ($LASTEXITCODE -or [long]$taskEngineMemory -lt 2GB) { throw 'Docker Engine requires 2 GiB of memory.' }
$taskEncoding = New-Object System.Text.UTF8Encoding($false)
$taskCompose = $null
$taskK6Started = $false
$taskRun = [guid]::NewGuid().ToString('N').Substring(0,12)
$taskProject = "logistech-week13-load-$taskRun"
$taskProxy = "$taskProject-proxy-1"
$taskBackend = "$taskProject-backend-1"
$taskDB = "$taskProject-db-1"
$taskOutput = Join-Path $taskRoot "output/qa/semana13/k6/$Scenario-$taskRun"
New-Item -ItemType Directory -Path $taskOutput -Force | Out-Null
$taskFixture = Join-Path $taskOutput 'fixture.json'
$taskCA = Join-Path $taskOutput 'root.crt'
$taskK6 = "$taskProject-k6"
function Write-Utf8($Path, $Value) {
    [IO.File]::WriteAllText($Path, [string]$Value, $taskEncoding)
}
function Get-DatabaseStorage {
    $taskUsage = docker exec $taskDB sh -c 'du -sk "$PGDATA"; df -Pk "$PGDATA" | tail -1'
    if ($LASTEXITCODE -or $taskUsage.Count -ne 2) { throw 'Could not measure PostgreSQL storage.' }
    $taskParts = ($taskUsage[1].Trim() -split '\s+')
    [pscustomobject]@{
        timestamp = [DateTime]::UtcNow.ToString('o')
        usedKiB = [long](($taskUsage[0].Trim() -split '\s+')[0])
        freeKiB = [long]$taskParts[3]
    }
}
try {
    Push-Location $taskRoot
    $env:SOURCE_REF = 'week13-local'
    $env:PUBLIC_DOMAIN = 'localhost'
    $env:PUBLIC_ORIGIN = 'https://localhost'
    $env:POSTGRES_DB = 'logistech'
    $taskCompose = @('-p',$taskProject,'--env-file','.env.f7-candidate','-f','compose.production.yml',
        '-f','compose.production-rehearsal.yml','-f','compose.week13-load.yml')
    docker compose @taskCompose up --no-build --pull never -d --wait db *> (Join-Path $taskOutput 'startup.log')
    if ($LASTEXITCODE) { throw 'Could not initialize isolated database.' }
    docker compose @taskCompose --profile tools run --rm --no-deps migration *>> (Join-Path $taskOutput 'startup.log')
    if ($LASTEXITCODE) { throw 'Migration failed.' }
    docker compose @taskCompose up --no-build --pull never -d --wait backend proxy *>> (Join-Path $taskOutput 'startup.log')
    if ($LASTEXITCODE) { throw 'Could not start isolated backend and proxy.' }
    docker exec $taskBackend python manage.py create_demo --namespace week13-load --output /tmp/k6-demo.json *>> (Join-Path $taskOutput 'startup.log')
    if ($LASTEXITCODE) { throw 'Could not create test fixtures.' }
    $taskBaseline = Get-DatabaseStorage
    if ($taskBaseline.freeKiB -lt 2097152) { throw 'Docker storage requires 2 GiB free.' }
    $taskData = Get-Content -Raw scripts/week13_load_fixture.py | docker exec -i -e "QA_VUS=$VUs" -e "QA_ROWS=$Rows" $taskBackend python manage.py shell --no-imports -c 'import sys; exec(sys.stdin.read())'
    if ($LASTEXITCODE) { throw 'Fixture setup failed.' }
    $taskSeed = ($taskData | Select-Object -Last 1) | ConvertFrom-Json
    Write-Utf8 (Join-Path $taskOutput 'pagination-plans.json') ($taskSeed.plans | ConvertTo-Json -Depth 70)
    Write-Utf8 $taskFixture ($taskSeed | Select-Object access,product,branch | ConvertTo-Json -Compress)
    $taskStorage = Join-Path $taskOutput 'storage.jsonl'
    Write-Utf8 $taskStorage (($taskBaseline | ConvertTo-Json -Compress) + "`n")
    $taskLimit = $taskBaseline.usedKiB + 131072
    docker cp "${taskProxy}:/data/caddy/pki/authorities/local/root.crt" $taskCA
    if ($LASTEXITCODE) { throw 'Could not export the local CA.' }
    $taskSource = Join-Path $taskRoot 'load/week13.js'
    docker stats --no-stream --format '{{json .}}' $taskBackend $taskDB |
        Set-Content (Join-Path $taskOutput 'resources-before.jsonl')
    $taskArgs = @('run','-d','--name',$taskK6,'--network',"container:$taskProxy",'--memory','256m','--cpus','1',
        '-e',"SCENARIO=$Scenario",'-e',"ITERATIONS=$Iterations",'-e',"VUS=$VUs",
        '-e','SSL_CERT_FILE=/root.crt','-e','LARGE_RUN=isolated','-e',"DURATION_SECONDS=$DurationSeconds",'-e',"PAGE=$Page",
        '-e',('PACE_SECONDS=' + $PaceSeconds.ToString([Globalization.CultureInfo]::InvariantCulture)),
        '-v',"${taskFixture}:/fixture.json:ro",'-v',"${taskCA}:/root.crt:ro",
        '-v',"${taskSource}:/scenario.js:ro",'-v',"${taskOutput}:/results",
        'grafana/k6:1.5.0','run','--quiet','/scenario.js')
    docker @taskArgs *> (Join-Path $taskOutput 'runner.log')
    if ($LASTEXITCODE) { throw 'Could not start k6.' }
    $taskK6Started = $true
    $taskDeadline = [DateTime]::UtcNow.AddSeconds($DurationSeconds + 15)
    $taskStopReason = $null
    while ($true) {
        $taskSample = Get-DatabaseStorage
        [IO.File]::AppendAllText($taskStorage, (($taskSample | ConvertTo-Json -Compress) + "`n"), $taskEncoding)
        $taskRunning = docker inspect --format '{{.State.Running}}' $taskK6
        if ($LASTEXITCODE) { throw 'Could not inspect k6.' }
        if ($taskSample.usedKiB -gt $taskLimit -or $taskSample.freeKiB -lt 1048576) {
            $taskStopReason = 'PostgreSQL storage budget exceeded.'
        } elseif ([DateTime]::UtcNow -gt $taskDeadline) {
            $taskStopReason = 'Runner deadline exceeded.'
        } elseif (@(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' $taskDB $taskBackend $taskProxy |
            Where-Object { $_ -notin @('healthy', 'running') }).Count -gt 0 -or $LASTEXITCODE) {
            $taskStopReason = 'A rehearsal dependency became unhealthy.'
        }
        if ($taskStopReason) {
            Write-Utf8 (Join-Path $taskOutput 'aborted.txt') $taskStopReason
            if ($taskRunning -eq 'true') { docker stop -t 3 $taskK6 | Out-Null }
            break
        }
        if ($taskRunning -ne 'true') { break }
        Start-Sleep -Seconds 3
    }
    docker logs $taskK6 *> (Join-Path $taskOutput 'run.log')
    $taskExit = if ($taskStopReason) { 1 } else { [int](docker inspect --format '{{.State.ExitCode}}' $taskK6) }
    docker stats --no-stream --format '{{json .}}' $taskBackend $taskDB |
        Set-Content (Join-Path $taskOutput 'resources-after.jsonl')
    $taskCountScript = 'from apps.accounts.models import User; print(User.objects.filter(email__startswith="week13-", email__endswith="@example.test").count())'
    $taskCount = $taskCountScript | docker exec -i $taskBackend python manage.py shell --no-imports -c 'import sys; exec(sys.stdin.read())'
    if ($LASTEXITCODE) { throw 'Could not verify persisted registrations.' }
    Write-Utf8 (Join-Path $taskOutput 'registration-count.txt') ($taskCount | Select-Object -Last 1)
    docker exec $taskBackend python manage.py migrate --check *> (Join-Path $taskOutput 'post-check.log')
    if ($LASTEXITCODE) { $taskExit = 1 }
    Write-Output $taskOutput
    exit $taskExit
} finally {
    if ($taskK6Started) { docker rm -f $taskK6 | Out-Null }
    if (Test-Path -LiteralPath $taskFixture) { Remove-Item -LiteralPath $taskFixture }
    if ($taskCompose) { docker compose @taskCompose down *> (Join-Path $taskOutput 'stop.log') }
    Pop-Location
}
