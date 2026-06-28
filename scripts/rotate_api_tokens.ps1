param(
  [switch]$RotateAdminToken,
  [switch]$RotateIngestToken,
  [switch]$ApplyDockerRestart
)

$ErrorActionPreference = "Stop"

if (-not $RotateAdminToken -and -not $RotateIngestToken) {
  throw "Informe -RotateAdminToken, -RotateIngestToken ou ambos."
}

function New-Secret {
  $bytes = New-Object byte[] 32
  $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
  $rng.GetBytes($bytes)
  return (($bytes | ForEach-Object { $_.ToString("x2") }) -join "")
}

function Mask-Secret {
  param([string]$Value)
  if (-not $Value) { return "(vazio)" }
  if ($Value.Length -le 10) { return "********" }
  return $Value.Substring(0, 4) + "..." + $Value.Substring($Value.Length - 4)
}

function Set-EnvValue {
  param([string]$Path, [string]$Key, [string]$Value)
  if (-not (Test-Path -LiteralPath $Path)) {
    throw "Arquivo nao encontrado: $Path"
  }
  $found = $false
  $lines = Get-Content -LiteralPath $Path | ForEach-Object {
    if ($_ -match "^${Key}=") {
      $found = $true
      "${Key}=${Value}"
    } else {
      $_
    }
  }
  if (-not $found) {
    $lines += "${Key}=${Value}"
  }
  Set-Content -Encoding ASCII -LiteralPath $Path -Value $lines
}

$rootEnv = ".env"
$supremeEnv = ".\supreme-backend\.env.production"
$prometheusToken = ".\infra\prometheus\supreme-api-token.local"

foreach ($path in @($rootEnv, $supremeEnv)) {
  if (-not (Test-Path -LiteralPath $path)) {
    throw "Arquivo obrigatorio ausente: $path"
  }
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDir = ".\.local\rotation-backups\$timestamp"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
Copy-Item -LiteralPath $rootEnv -Destination (Join-Path $backupDir ".env") -Force
Copy-Item -LiteralPath $supremeEnv -Destination (Join-Path $backupDir "supreme-backend.env.production") -Force
if (Test-Path -LiteralPath $prometheusToken) {
  Copy-Item -LiteralPath $prometheusToken -Destination (Join-Path $backupDir "supreme-api-token.local") -Force
}

if ($RotateAdminToken) {
  $newAdmin = New-Secret
  Set-EnvValue -Path $supremeEnv -Key "API_SECRET_KEY" -Value $newAdmin
  New-Item -ItemType Directory -Force -Path ".\infra\prometheus" | Out-Null
  Set-Content -Encoding ASCII -NoNewline -LiteralPath $prometheusToken -Value $newAdmin
  Write-Host "API_SECRET_KEY rotacionado: $(Mask-Secret $newAdmin)"
  Write-Host "Prometheus bearer token atualizado."
}

if ($RotateIngestToken) {
  $newIngest = New-Secret
  Set-EnvValue -Path $rootEnv -Key "API_INGEST_TOKEN" -Value $newIngest
  Set-EnvValue -Path $supremeEnv -Key "API_INGEST_TOKEN" -Value $newIngest
  Write-Host "API_INGEST_TOKEN rotacionado: $(Mask-Secret $newIngest)"
}

Write-Host "Backup dos envs anteriores: $backupDir"

if ($ApplyDockerRestart) {
  docker compose -f docker-compose.production.yml -f docker-compose.local.yml up -d --force-recreate --no-deps supreme-api supreme-worker prometheus supreme-iped-watcher supreme-iped-proxy
  docker compose -f docker-compose.production.yml -f docker-compose.local.yml up -d --force-recreate --no-deps nginx
  Write-Host "Containers afetados recriados."
} else {
  Write-Host "Reinicie os servicos afetados ou rode novamente com -ApplyDockerRestart."
}
