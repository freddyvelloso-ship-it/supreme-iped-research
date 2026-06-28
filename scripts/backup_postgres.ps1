param(
  [string]$OutputDir = ".\backups\postgres",
  [switch]$IncludeLocalOverride
)

$ErrorActionPreference = "Stop"

function Invoke-Compose {
  param([string[]]$Args)
  $compose = @("-f", "docker-compose.production.yml")
  if ($IncludeLocalOverride -or (Test-Path -LiteralPath "docker-compose.local.yml")) {
    $compose += @("-f", "docker-compose.local.yml")
  }
  & docker compose @compose @Args
  if ($LASTEXITCODE -ne 0) {
    throw "docker compose falhou: $($Args -join ' ')"
  }
}

function Backup-Database {
  param(
    [string]$Service,
    [string]$Database,
    [string]$User,
    [string]$OutputFile
  )

  $container = (& docker compose -f docker-compose.production.yml -f docker-compose.local.yml ps -q $Service 2>$null)
  if (-not $container) {
    $container = (& docker compose -f docker-compose.production.yml ps -q $Service 2>$null)
  }
  if (-not $container) {
    throw "Container do servico $Service nao encontrado."
  }

  $remote = "/tmp/${Database}_backup.dump"
  & docker exec $container pg_dump -U $User -d $Database -Fc -f $remote
  if ($LASTEXITCODE -ne 0) { throw "pg_dump falhou para $Database" }

  & docker cp "${container}:${remote}" $OutputFile
  if ($LASTEXITCODE -ne 0) { throw "docker cp falhou para $Database" }

  & docker exec $container rm -f $remote | Out-Null
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$supremeOut = Join-Path $OutputDir "supreme_${stamp}.dump"
$sentinelaOut = Join-Path $OutputDir "sentinela_${stamp}.dump"

Backup-Database -Service "supreme-db" -Database "supreme" -User "supreme" -OutputFile $supremeOut
Backup-Database -Service "sentinela-db" -Database "sentinela" -User "sentinela" -OutputFile $sentinelaOut

$manifest = Join-Path $OutputDir "backup_${stamp}.manifest.json"
$items = @($supremeOut, $sentinelaOut) | ForEach-Object {
  $hash = Get-FileHash -Algorithm SHA256 -LiteralPath $_
  [ordered]@{
    path = $_
    bytes = (Get-Item -LiteralPath $_).Length
    sha256 = $hash.Hash
  }
}

@{
  created_at_utc = $stamp
  format = "pg_dump_custom"
  files = $items
} | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 -LiteralPath $manifest

Write-Host "Backups criados:"
Write-Host "  $supremeOut"
Write-Host "  $sentinelaOut"
Write-Host "Manifest:"
Write-Host "  $manifest"
