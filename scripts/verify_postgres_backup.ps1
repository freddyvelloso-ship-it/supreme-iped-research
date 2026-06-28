param(
  [Parameter(Mandatory = $true)]
  [string]$DumpPath,
  [ValidateSet("supreme", "sentinela")]
  [string]$Database = "supreme"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $DumpPath)) {
  throw "Dump nao encontrado: $DumpPath"
}

$service = if ($Database -eq "supreme") { "supreme-db" } else { "sentinela-db" }
$container = (& docker compose -f docker-compose.production.yml -f docker-compose.local.yml ps -q $service 2>$null)
if (-not $container) {
  $container = (& docker compose -f docker-compose.production.yml ps -q $service 2>$null)
}
if (-not $container) {
  throw "Container do servico $service nao encontrado."
}

$remote = "/tmp/verify_${Database}.dump"
& docker cp $DumpPath "${container}:${remote}"
if ($LASTEXITCODE -ne 0) { throw "docker cp falhou" }

try {
  $list = & docker exec $container pg_restore --list $remote
  if ($LASTEXITCODE -ne 0) { throw "pg_restore --list falhou" }
  $tableCount = @($list | Where-Object { $_ -match " TABLE " }).Count
  if ($tableCount -lt 1) {
    throw "Dump valido, mas sem tabelas detectadas."
  }
  $hash = Get-FileHash -Algorithm SHA256 -LiteralPath $DumpPath
  Write-Host "Backup valido: $DumpPath"
  Write-Host "Banco alvo: $Database"
  Write-Host "Tabelas detectadas: $tableCount"
  Write-Host "SHA256: $($hash.Hash)"
} finally {
  & docker exec $container rm -f $remote | Out-Null
}
