param(
    [ValidateSet('get','crud','register','boxes','history','recovery')]
    [string]$Scenario = 'get',
    [ValidateSet(1,2,3,100,500,1000,2500,5000,10000,25000,50000)]
    [int]$Iterations = 100,
    [ValidateRange(1,20)][int]$VUs = 1
)
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path $PSScriptRoot -Parent
if ($Iterations -gt 100) { throw 'Larger profiles require an isolated runner with a verified storage quota.' }
$taskRun = [guid]::NewGuid().ToString('N').Substring(0,12)
$taskProject = "logistech-week13-load-$taskRun"
$taskProxy = "$taskProject-proxy-1"
$taskBackend = "$taskProject-backend-1"
$taskDB = "$taskProject-db-1"
$taskOutput = Join-Path $taskRoot "output/qa/semana13/k6/$Scenario-$taskRun"
New-Item -ItemType Directory -Path $taskOutput -Force | Out-Null
$taskFixture = Join-Path $taskOutput 'fixture.json'
$taskCA = Join-Path $taskOutput 'root.crt'
$taskPython = @'
import json
from apps.accounts.models import User
from apps.catalog.models import Product
from apps.organizations.models import Branch
from rest_framework_simplejwt.tokens import AccessToken
user = User.objects.get(email="admin.week13-load@example.test")
print(json.dumps({"access": str(AccessToken.for_user(user)), "product": str(Product.objects.filter(company=user.company).first().pk), "branch": str(Branch.objects.filter(company=user.company).first().pk)}))
'@
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
    docker exec $taskBackend python manage.py shell -c $taskPython | Select-Object -Last 1 | Set-Content -Encoding utf8NoBOM $taskFixture
    if ($LASTEXITCODE) { throw 'Create the week13-load fixtures using create_demo.' }
    docker cp "${taskProxy}:/data/caddy/pki/authorities/local/root.crt" $taskCA
    if ($LASTEXITCODE) { throw 'Could not export the local CA.' }
    $taskSource = Join-Path $taskRoot 'load/week13.js'
    docker stats --no-stream --format '{{json .}}' $taskBackend $taskDB |
        Set-Content (Join-Path $taskOutput 'resources-before.jsonl')
    $taskArgs = @('run','--rm','--network',"container:$taskProxy",'--memory','256m','--cpus','1',
        '-e',"SCENARIO=$Scenario",'-e',"ITERATIONS=$Iterations",'-e',"VUS=$VUs",
        '-e','SSL_CERT_FILE=/root.crt',
        '-v',"${taskFixture}:/fixture.json:ro",'-v',"${taskCA}:/root.crt:ro",
        '-v',"${taskSource}:/scenario.js:ro",'-v',"${taskOutput}:/results",
        'grafana/k6:1.5.0','run','--quiet','/scenario.js')
    docker @taskArgs *> (Join-Path $taskOutput 'run.log')
    $taskExit = $LASTEXITCODE
    docker stats --no-stream --format '{{json .}}' $taskBackend $taskDB |
        Set-Content (Join-Path $taskOutput 'resources-after.jsonl')
    docker exec $taskBackend python manage.py shell -c 'from apps.accounts.models import User; print(User.objects.filter(email__startswith="week13-", email__endswith="@example.test").count())' |
        Select-Object -Last 1 | Set-Content (Join-Path $taskOutput 'registration-count.txt')
    Write-Output $taskOutput
    exit $taskExit
} finally {
    if (Test-Path -LiteralPath $taskFixture) { Remove-Item -LiteralPath $taskFixture }
    if ($taskCompose) { docker compose @taskCompose down *> (Join-Path $taskOutput 'stop.log') }
    Pop-Location
}
