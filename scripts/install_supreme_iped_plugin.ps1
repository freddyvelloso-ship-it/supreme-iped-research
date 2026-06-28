param(
  [Parameter(Mandatory=$true)] [string]$IpedHome,
  [string]$Root = ".",
  [switch]$Force,
  [switch]$Rollback,
  [switch]$VerifyOnly
)

$ErrorActionPreference = "Stop"
$rootPath = (Resolve-Path -LiteralPath $Root).Path
$ipedPath = (Resolve-Path -LiteralPath $IpedHome).Path
$jarPath = Join-Path $rootPath "supreme-iped-plugin\dist\supreme-iped-plugin.jar"
$manifestPath = Join-Path $rootPath "supreme-iped-plugin\dist\supreme-iped-plugin-manifest.json"
$pluginDir = Join-Path $ipedPath "plugins"
$confPath = Join-Path $ipedPath "conf\ResultSetViewersConf.xml"
$backupPath = "$confPath.supreme.bak"
$installManifest = Join-Path $ipedPath "supreme-plugin-install-manifest.json"
$className = "com.supreme.iped.SupremeFieldTelemetryViewer"

if (-not (Test-Path -LiteralPath $jarPath)) { throw "Plugin JAR not found: $jarPath" }
if (-not (Test-Path -LiteralPath $manifestPath)) { throw "Plugin manifest not found: $manifestPath" }
if (-not (Test-Path -LiteralPath $confPath)) { throw "IPED ResultSetViewersConf.xml not found: $confPath" }

if ($Rollback) {
  if (-not (Test-Path -LiteralPath $backupPath)) { throw "Rollback backup not found: $backupPath" }
  Copy-Item -LiteralPath $backupPath -Destination $confPath -Force
  Remove-Item -LiteralPath (Join-Path $pluginDir "supreme-iped-plugin.jar") -Force -ErrorAction SilentlyContinue
  Write-Host "SUPREME IPED plugin rollback completed."
  exit 0
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$hash = (Get-FileHash -LiteralPath $jarPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($hash -ne $manifest.artifact_sha256) { throw "Plugin JAR hash does not match manifest." }

$confText = Get-Content -LiteralPath $confPath -Raw
$alreadyConfigured = $confText.Contains($className)
if ($VerifyOnly) {
  if (-not $alreadyConfigured) { throw "SUPREME plugin class is not configured in ResultSetViewersConf.xml." }
  if (-not (Test-Path -LiteralPath (Join-Path $pluginDir "supreme-iped-plugin.jar"))) { throw "SUPREME plugin JAR is not installed." }
  Write-Host "SUPREME IPED plugin installation verified."
  exit 0
}

New-Item -ItemType Directory -Force $pluginDir | Out-Null
Copy-Item -LiteralPath $jarPath -Destination (Join-Path $pluginDir "supreme-iped-plugin.jar") -Force

if (-not (Test-Path -LiteralPath $backupPath)) {
  Copy-Item -LiteralPath $confPath -Destination $backupPath -Force
} elseif (-not $Force) {
  throw "Backup already exists. Use -Force if you intentionally want to keep the existing backup and reinstall."
}

if (-not $alreadyConfigured) {
  [xml]$xml = Get-Content -LiteralPath $confPath
  $rootNode = $xml.SelectSingleNode("/resultSetViewers")
  if ($null -eq $rootNode) { throw "Invalid ResultSetViewersConf.xml: missing resultSetViewers root." }
  $viewer = $xml.CreateElement("resultSetViewer")
  $class = $xml.CreateElement("class")
  $class.InnerText = $className
  [void]$viewer.AppendChild($class)
  [void]$rootNode.AppendChild($viewer)
  $xml.Save($confPath)
}

$install = [ordered]@{
  installed_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
  iped_home = $ipedPath
  plugin_jar = (Join-Path $pluginDir "supreme-iped-plugin.jar")
  plugin_sha256 = $hash
  result_set_viewer_class = $className
  config_backup = $backupPath
  signing_mode = $manifest.signing_mode
}
$install | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $installManifest -Encoding UTF8

Write-Host "SUPREME IPED plugin installed in IPED home: $ipedPath"
