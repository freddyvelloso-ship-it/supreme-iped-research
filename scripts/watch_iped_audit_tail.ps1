param(
  [string]$AuditLog = "$env:USERPROFILE\supreme_audit.ndjson"
)

$ErrorActionPreference = "Stop"

Write-Host "SUPREME V4 - monitor NDJSON IPED real" -ForegroundColor Cyan
Write-Host "Arquivo: $AuditLog" -ForegroundColor DarkGray

if (-not (Test-Path -LiteralPath $AuditLog)) {
  Write-Host "Arquivo ainda nao existe. Abra o IPED patched para gerar eventos." -ForegroundColor Yellow
  New-Item -ItemType File -Force -Path $AuditLog | Out-Null
}

Get-Content -LiteralPath $AuditLog -Wait -Tail 10 | ForEach-Object {
  $line = $_
  try {
    $obj = $line | ConvertFrom-Json
    $kind = $obj.event
    $item = $obj.itemId
    $media = $obj.mediaType
    $open = $obj.openTs
    $close = $obj.closeTs
    Write-Host "[$kind] item=$item media=$media openTs=$open closeTs=$close"
  } catch {
    Write-Host $line -ForegroundColor Yellow
  }
}
