param(
  [string]$Root = ".",
  [switch]$RequireRealSigning
)

$ErrorActionPreference = "Stop"
$rootPath = (Resolve-Path -LiteralPath $Root).Path
$jarPath = Join-Path $rootPath "supreme-iped-plugin\dist\supreme-iped-plugin.jar"
$manifestPath = Join-Path $rootPath "supreme-iped-plugin\dist\supreme-iped-plugin-manifest.json"
$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure([string]$Message) {
  $failures.Add($Message) | Out-Null
  Write-Host "[FAIL] $Message" -ForegroundColor Red
}

function Add-Pass([string]$Message) {
  Write-Host "[ OK ] $Message" -ForegroundColor Green
}

if (-not (Test-Path -LiteralPath $jarPath)) { Add-Failure "Plugin JAR not found: $jarPath" } else { Add-Pass "Plugin JAR exists" }
if (-not (Test-Path -LiteralPath $manifestPath)) { Add-Failure "Plugin manifest not found: $manifestPath" } else { Add-Pass "Plugin manifest exists" }

if ((Test-Path -LiteralPath $jarPath) -and (Test-Path -LiteralPath $manifestPath)) {
  $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
  $hash = (Get-FileHash -LiteralPath $jarPath -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($hash -eq $manifest.artifact_sha256) { Add-Pass "Plugin SHA256 matches manifest" } else { Add-Failure "Plugin SHA256 does not match manifest" }
  $jarList = & jar tf $jarPath
  if ($jarList -match "com/supreme/iped/SupremeFieldTelemetryViewer.class") { Add-Pass "Plugin class is packaged" } else { Add-Failure "Plugin class missing from JAR" }
  if ($manifest.iped_extension_point -eq "iped.viewers.api.ResultSetViewer") { Add-Pass "Plugin uses IPED ResultSetViewer extension point" } else { Add-Failure "Unexpected IPED extension point" }
  if ($RequireRealSigning -and $manifest.signing_mode -ne "jarsigner") { Add-Failure "Production requires real JAR signature; current signing_mode=$($manifest.signing_mode)" }
}

Write-Host "Resumo Fase 8 plugin verification: $($failures.Count) falha(s)." -ForegroundColor Cyan
if ($failures.Count -gt 0) { exit 1 }
exit 0
