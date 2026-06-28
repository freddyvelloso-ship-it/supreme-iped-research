param(
  [string]$Root = "."
)

$ErrorActionPreference = "Stop"
$rootPath = (Resolve-Path -LiteralPath $Root).Path
$sourceIped = Join-Path $rootPath "tmp\iped-src\target\release\iped-4.4.0-SNAPSHOT"
if (-not (Test-Path -LiteralPath $sourceIped)) {
  throw "IPED release not found: $sourceIped"
}
$temp = Join-Path $rootPath "tmp\phase8-plugin-install-test"
if (Test-Path -LiteralPath $temp) {
  Remove-Item -LiteralPath $temp -Recurse -Force
}
New-Item -ItemType Directory -Force $temp | Out-Null
New-Item -ItemType Directory -Force (Join-Path $temp "conf"), (Join-Path $temp "plugins") | Out-Null
Copy-Item -LiteralPath (Join-Path $sourceIped "conf\ResultSetViewersConf.xml") -Destination (Join-Path $temp "conf\ResultSetViewersConf.xml") -Force

powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $rootPath "scripts\install_supreme_iped_plugin.ps1") -Root $rootPath -IpedHome $temp -Force
powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $rootPath "scripts\install_supreme_iped_plugin.ps1") -Root $rootPath -IpedHome $temp -VerifyOnly

$xml = Get-Content -LiteralPath (Join-Path $temp "conf\ResultSetViewersConf.xml") -Raw
if (-not $xml.Contains("com.supreme.iped.SupremeFieldTelemetryViewer")) {
  throw "Plugin class was not added to ResultSetViewersConf.xml"
}
if (-not (Test-Path -LiteralPath (Join-Path $temp "plugins\supreme-iped-plugin.jar"))) {
  throw "Plugin jar was not installed"
}

Write-Host "Phase 8 plugin installer test passed: $temp"
