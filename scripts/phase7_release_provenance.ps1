param(
  [string]$Root = ".",
  [string]$OutputPath = "reports\phase7\release_provenance.json"
)

$ErrorActionPreference = "Stop"
$rootPath = (Resolve-Path -LiteralPath $Root).Path
$outPath = [System.IO.Path]::GetFullPath((Join-Path $rootPath $OutputPath))
$outDir = Split-Path -Parent $outPath
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$sensitiveRelativePaths = @(
  ".env",
  "supreme-backend/.env.production",
  "sentinela/.env.production",
  "infra/prometheus/supreme-api-token.local",
  "infra/alertmanager/alertmanager.yml",
  "certs/fullchain.pem",
  "certs/privkey.pem"
)
$files = Get-ChildItem -LiteralPath $rootPath -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
  $_.FullName -notmatch "\\(.git|tmp|backups|certs|IPED-local|\.local|\.pytest_cache|__pycache__)\\"
}
$items = foreach ($file in $files) {
  $relative = $file.FullName.Substring($rootPath.Length).TrimStart("\", "/") -replace "\\", "/"
  if ($sensitiveRelativePaths -contains $relative) { continue }
  $hash = Get-FileHash -Algorithm SHA256 -LiteralPath $file.FullName
  [ordered]@{ path = $relative; bytes = $file.Length; sha256 = $hash.Hash.ToLowerInvariant() }
}
$payload = [ordered]@{
  artifact = "SUPREME V4 phase 7 release provenance"
  generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
  signing_mode = "detached_digest_manifest"
  image_signing_policy = "CI must sign container image digests or release digests before publication"
  file_count = @($items).Count
  files = $items
}
$canonical = ($payload | ConvertTo-Json -Depth 8 -Compress)
$signature = [System.BitConverter]::ToString(
  [System.Security.Cryptography.SHA256]::Create().ComputeHash([Text.Encoding]::UTF8.GetBytes($canonical))
).Replace("-", "").ToLowerInvariant()
$payload["provenance_signature_sha256"] = $signature
$payload | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 -LiteralPath $outPath
Write-Host "Phase 7 release provenance generated: $outPath"
Write-Host "Signature SHA256: $signature"
