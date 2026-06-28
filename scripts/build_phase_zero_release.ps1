param(
  [string]$Root = ".",
  [string]$OutputDir = "..\..\outputs",
  [string]$WorkDir = "..\..\tmp\phase-zero-release",
  [string]$NamePrefix = "supreme-v4-phase-zero-100"
)

$ErrorActionPreference = "Stop"

$rootPath = (Resolve-Path -LiteralPath $Root).Path
$outputPath = [System.IO.Path]::GetFullPath((Join-Path $rootPath $OutputDir))
$workPath = [System.IO.Path]::GetFullPath((Join-Path $rootPath $WorkDir))
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$stagePath = Join-Path $workPath "src-$timestamp"
$zipPath = Join-Path $outputPath "$NamePrefix-$timestamp.zip"

$excludedDirs = @(
  ".git",
  ".agents",
  ".codex",
  ".local",
  "IPED-local",
  "backups",
  "certs",
  "tmp",
  "__pycache__",
  ".pytest_cache",
  "node_modules"
)

$excludedFiles = @(
  ".env",
  "supreme-backend/.env.production",
  "sentinela/.env.production",
  "infra/prometheus/supreme-api-token.local",
  "infra/alertmanager/alertmanager.yml"
)

$forbiddenExtensions = @(
  ".zip", ".sqlite", ".sqlite3", ".db", ".duckdb", ".dump", ".bak",
  ".E01", ".Ex01", ".aff4", ".raw", ".dd", ".ad1", ".l01", ".pyc", ".pyo"
)

function Convert-ToRelativePath {
  param([string]$Path)
  $relative = $Path.Substring($rootPath.Length).TrimStart("\", "/")
  return ($relative -replace "\\", "/")
}

function Test-IsExcludedDir {
  param([string]$RelativePath)
  $parts = $RelativePath -split "/"
  foreach ($part in $parts) {
    if ($excludedDirs -contains $part) {
      return $true
    }
  }
  return $false
}

New-Item -ItemType Directory -Force -Path $outputPath | Out-Null
if (Test-Path -LiteralPath $workPath) {
  Remove-Item -LiteralPath $workPath -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $stagePath | Out-Null

$files = Get-ChildItem -LiteralPath $rootPath -Recurse -File -Force -ErrorAction SilentlyContinue | Where-Object {
  $relative = Convert-ToRelativePath -Path $_.FullName
  -not (Test-IsExcludedDir -RelativePath $relative) -and
  -not ($excludedFiles -contains $relative) -and
  -not ($forbiddenExtensions -contains $_.Extension)
}

foreach ($file in $files) {
  $relative = Convert-ToRelativePath -Path $file.FullName
  $target = Join-Path $stagePath ($relative -replace "/", "\")
  $targetDir = Split-Path -Parent $target
  New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
  Copy-Item -LiteralPath $file.FullName -Destination $target -Force
}

if (Test-Path -LiteralPath $zipPath) {
  Remove-Item -LiteralPath $zipPath -Force
}

Compress-Archive -Path (Join-Path $stagePath "*") -DestinationPath $zipPath -Force

if (-not (Test-Path -LiteralPath $zipPath)) {
  throw "Release ZIP was not created: $zipPath"
}

Write-Host "Release source: $stagePath"
Write-Host "Release zip: $zipPath"
