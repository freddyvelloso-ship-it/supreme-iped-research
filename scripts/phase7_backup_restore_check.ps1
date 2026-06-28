param(
  [string]$OutputDir = ".\backups\phase7",
  [switch]$SkipDocker
)

$ErrorActionPreference = "Stop"

if ($SkipDocker) {
  Write-Host "Backup/restore Docker check skipped by explicit flag."
  exit 0
}

function Service-Container([string]$Service) {
  $container = (& docker compose -f docker-compose.production.yml -f docker-compose.local.yml ps -q $Service 2>$null)
  if (-not $container) {
    throw "Container not found for service $Service"
  }
  return $container.Trim()
}

function Backup-And-Restore-TempDb {
  param(
    [string]$Service,
    [string]$Database,
    [string]$User,
    [string]$OutputFile
  )
  $container = Service-Container $Service
  $remote = "/tmp/${Database}_phase7.dump"
  $restoreDb = "phase7_restore_${Database}_$(Get-Date -Format 'HHmmss')"

  & docker exec $container pg_dump -U $User -d $Database -Fc -f $remote
  if ($LASTEXITCODE -ne 0) { throw "pg_dump failed for $Database" }
  & docker cp "${container}:${remote}" $OutputFile
  if ($LASTEXITCODE -ne 0) { throw "docker cp failed for $Database" }
  & docker exec $container createdb -U $User $restoreDb
  if ($LASTEXITCODE -ne 0) { throw "createdb failed for $restoreDb" }
  try {
    & docker exec $container pg_restore -U $User -d $restoreDb --no-owner --role=$User $remote
    if ($LASTEXITCODE -ne 0) { throw "pg_restore failed for $restoreDb" }
    $tables = & docker exec $container psql -U $User -d $restoreDb -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';"
    if ([int]$tables.Trim() -lt 1) { throw "restore for $restoreDb produced no public tables" }
  }
  finally {
    & docker exec $container dropdb -U $User --if-exists $restoreDb | Out-Null
    & docker exec $container rm -f $remote | Out-Null
  }
  $hash = Get-FileHash -Algorithm SHA256 -LiteralPath $OutputFile
  return [ordered]@{
    database = $Database
    dump_path = $OutputFile
    bytes = (Get-Item -LiteralPath $OutputFile).Length
    sha256 = $hash.Hash.ToLowerInvariant()
    restore_mode = "temporary_database"
    restore_status = "ok"
  }
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$supremeOut = Join-Path $OutputDir "supreme_${stamp}.dump"
$sentinelaOut = Join-Path $OutputDir "sentinela_${stamp}.dump"
$results = @(
  (Backup-And-Restore-TempDb -Service "supreme-db" -Database "supreme" -User "supreme" -OutputFile $supremeOut),
  (Backup-And-Restore-TempDb -Service "sentinela-db" -Database "sentinela" -User "sentinela" -OutputFile $sentinelaOut)
)
$manifest = Join-Path $OutputDir "phase7_backup_restore_${stamp}.json"
@{
  generated_at_utc = $stamp
  status = "ok"
  results = $results
} | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 -LiteralPath $manifest

Write-Host "Phase 7 backup/restore status: ok"
Write-Host "Manifest: $manifest"

