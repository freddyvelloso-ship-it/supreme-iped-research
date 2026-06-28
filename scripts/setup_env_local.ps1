# setup_env_local.ps1
# Generates local environment files for Docker Compose tests.
# Do not use generated values in production.

$ErrorActionPreference = "Stop"

function New-Secret {
    param([int]$Bytes = 32)
    $buffer = New-Object byte[] $Bytes
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $rng.GetBytes($buffer)
    } finally {
        $rng.Dispose()
    }
    return [Convert]::ToBase64String($buffer).Replace("+", "A").Replace("/", "B").Replace("=", "C")
}

function Write-Utf8NoBom {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string]$Content
    )

    $fullPath = Join-Path (Get-Location) $Path
    $directory = Split-Path $fullPath -Parent

    if (!(Test-Path $directory)) {
        New-Item -ItemType Directory -Force $directory | Out-Null
    }

    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($fullPath, $Content, $utf8NoBom)
}

$PostgresPassword = New-Secret
$SentinelaPostgresPassword = New-Secret
$RedisPassword = New-Secret
$GrafanaPassword = New-Secret
$ApiSecretKey = New-Secret
$SecretKey = New-Secret
$ApiIngestToken = New-Secret
$SupremeSalt = New-Secret
$SentinelaApiKey = New-Secret
$BootstrapToken = New-Secret
$BackupPassphrase = New-Secret
$AlertmanagerPassword = New-Secret

$RootEnv = @"
# Local test environment. Do not use in production.

ENV_PROFILE=local
POSTGRES_PASSWORD=$PostgresPassword
SENTINELA_POSTGRES_PASSWORD=$SentinelaPostgresPassword
REDIS_PASSWORD=$RedisPassword
SENTINELA_API_KEY=$SentinelaApiKey

GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=$GrafanaPassword
GRAFANA_ROOT_URL=https://localhost/grafana/

SUPREME_API_WORKERS=1
SUPREME_WORKER_REPLICAS=1

BACKUP_PASSPHRASE=$BackupPassphrase

API_SECRET_KEY=$ApiSecretKey
SECRET_KEY=$SecretKey
API_INGEST_TOKEN=$ApiIngestToken
SUPREME_SALT=$SupremeSalt

IPED_AUDIT_DIR=./tmp/iped-audit

ALERTMANAGER_SMTP_HOST=mailpit:1025
ALERTMANAGER_SMTP_FROM=SUPREME Alerts <alerts@localhost>
ALERTMANAGER_SMTP_USERNAME=alerts@localhost
ALERTMANAGER_SMTP_PASSWORD=$AlertmanagerPassword
ALERTMANAGER_SMTP_REQUIRE_TLS=false
ALERTMANAGER_EMAIL_TO=operacao@localhost
"@

$SupremeEnv = @"
# SUPREME Backend - local test environment. Do not use in production.

ENVIRONMENT=production
ENABLE_DOCS=false
ENABLE_METRICS=true
LOG_LEVEL=INFO
API_DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000

POSTGRES_PASSWORD=$PostgresPassword
REDIS_PASSWORD=$RedisPassword

DATABASE_URL=postgresql+asyncpg://supreme:$PostgresPassword@supreme-db:5432/supreme
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
REDIS_URL=redis://:$RedisPassword@supreme-redis:6379/0
RQ_QUEUE_ANALYTICS=analytics
RQ_QUEUE_EVENTS=events
RQ_QUEUE_DEAD_LETTER=dead_letter
RQ_MAX_RETRIES=3
RQ_RETRY_DELAY_S=10

API_SECRET_KEY=$ApiSecretKey
API_INGEST_TOKEN=$ApiIngestToken
SUPREME_SALT=$SupremeSalt

ALLOWED_ORIGINS=https://localhost,http://localhost
SENTINELA_URL=http://sentinela:8001
SENTINELA_API_KEY=$SentinelaApiKey

STUDY_START_DATE=2026-01-01
WINDOW_DAYS=14
MIN_BASELINE_WINDOWS=4
MAX_BASELINE_WINDOWS=8
DQ_MIN_THRESHOLD=0.5
ALGORITHM_VERSION=SUPREME-ANALYTICS-1.0.0
"@

$SentinelaEnv = @"
# SENTINELA - local test environment. Do not use in production.

ENVIRONMENT=production
ENABLE_DOCS=false
AUTO_INIT_DB=false
ACCESS_TOKEN_EXPIRE_MINUTES=480

POSTGRES_PASSWORD=$SentinelaPostgresPassword
DATABASE_URL=postgresql+asyncpg://sentinela:$SentinelaPostgresPassword@sentinela-db:5432/sentinela

SECRET_KEY=$SecretKey
SUPREME_API_KEY=$SentinelaApiKey
BOOTSTRAP_TOKEN=$BootstrapToken
ALGORITHM=HS256

ALLOWED_ORIGINS=https://localhost,http://localhost
"@

Write-Utf8NoBom ".env" $RootEnv
Write-Utf8NoBom "supreme-backend\.env.production" $SupremeEnv
Write-Utf8NoBom "sentinela\.env.production" $SentinelaEnv
Write-Utf8NoBom "infra\prometheus\supreme-api-token.local" $ApiSecretKey

& ".\scripts\render_alertmanager_config.ps1" -EnvFile ".env" -Output ".\infra\alertmanager\alertmanager.yml"

New-Item -ItemType Directory -Force ".\tmp\iped-audit" | Out-Null

Write-Host "Local files generated:"
Write-Host " - .env"
Write-Host " - supreme-backend\.env.production"
Write-Host " - sentinela\.env.production"
Write-Host " - infra\prometheus\supreme-api-token.local"
Write-Host " - infra\alertmanager\alertmanager.yml"
Write-Host ""
Write-Host "Warning: these files are ignored and must not be shipped in a release."
