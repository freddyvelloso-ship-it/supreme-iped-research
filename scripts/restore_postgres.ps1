param(
  [Parameter(Mandatory = $true)]
  [string]$DumpPath,
  [ValidateSet("supreme", "sentinela")]
  [string]$Database = "supreme",
  [switch]$ConfirmRestore
)

$ErrorActionPreference = "Stop"

if (-not $ConfirmRestore) {
  throw "Restore e destrutivo. Rode novamente com -ConfirmRestore apos validar o dump."
}
if (-not (Test-Path -LiteralPath $DumpPath)) {
  throw "Dump nao encontrado: $DumpPath"
}

$service = if ($Database -eq "supreme") { "supreme-db" } else { "sentinela-db" }
$user = if ($Database -eq "supreme") { "supreme" } else { "sentinela" }
$container = (& docker compose -f docker-compose.production.yml -f docker-compose.local.yml ps -q $service 2>$null)
if (-not $container) {
  $container = (& docker compose -f docker-compose.production.yml ps -q $service 2>$null)
}
if (-not $container) {
  throw "Container do servico $service nao encontrado."
}

$remote = "/tmp/restore_${Database}.dump"
& docker cp $DumpPath "${container}:${remote}"
if ($LASTEXITCODE -ne 0) { throw "docker cp falhou" }

try {
  & docker exec $container pg_restore -U $user -d $Database --clean --if-exists --no-owner --role=$user $remote
  if ($LASTEXITCODE -ne 0) { throw "pg_restore falhou" }
  Write-Host "Restore concluido para banco $Database."
} finally {
  & docker exec $container rm -f $remote | Out-Null
}
