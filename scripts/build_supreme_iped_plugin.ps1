param(
  [string]$Root = ".",
  [string]$IpedRelease = ".\tmp\iped-src\target\release\iped-4.4.0-SNAPSHOT",
  [string]$Javac = "javac",
  [switch]$RequireRealSigning
)

$ErrorActionPreference = "Stop"

$rootPath = (Resolve-Path -LiteralPath $Root).Path
$pluginRoot = Join-Path $rootPath "supreme-iped-plugin"
$srcRoot = Join-Path $pluginRoot "src\main\java"
$buildDir = Join-Path $pluginRoot "build"
$classesDir = Join-Path $buildDir "classes"
$distDir = Join-Path $pluginRoot "dist"
$jarPath = Join-Path $distDir "supreme-iped-plugin.jar"
$manifestPath = Join-Path $distDir "supreme-iped-plugin-manifest.json"

New-Item -ItemType Directory -Force $classesDir, $distDir | Out-Null

$ipedReleasePath = (Resolve-Path -LiteralPath (Join-Path $rootPath $IpedRelease)).Path
$classPathItems = @(
  (Join-Path $rootPath "tmp\iped-src\iped-api\target\iped-api-4.4.0-SNAPSHOT.jar"),
  (Join-Path $rootPath "tmp\iped-src\iped-viewers\iped-viewers-api\target\iped-viewers-api-4.4.0-SNAPSHOT.jar"),
  (Join-Path $ipedReleasePath "lib\docking-frames-common-1.1.2.jar"),
  (Join-Path $ipedReleasePath "lib\docking-frames-core-1.1.2.jar"),
  (Join-Path $ipedReleasePath "lib\tika-core-2.4.0-p1.jar")
)
$classpath = ($classPathItems -join ";")

$sources = Get-ChildItem -LiteralPath $srcRoot -Recurse -File -Filter "*.java"
if ($sources.Count -eq 0) {
  throw "No Java sources found in $srcRoot"
}

& $Javac -encoding UTF-8 -source 11 -target 11 -cp $classpath -d $classesDir @($sources.FullName)
if ($LASTEXITCODE -ne 0) {
  throw "javac failed"
}

if (Test-Path -LiteralPath $jarPath) {
  Remove-Item -LiteralPath $jarPath -Force
}
& jar --create --file $jarPath -C $classesDir .
if ($LASTEXITCODE -ne 0) {
  throw "jar creation failed"
}

$signingMode = "unsigned-dev"
if ($env:SUPREME_CODESIGN_KEYSTORE -and $env:SUPREME_CODESIGN_ALIAS -and $env:SUPREME_CODESIGN_STOREPASS) {
  & jarsigner -keystore $env:SUPREME_CODESIGN_KEYSTORE -storepass $env:SUPREME_CODESIGN_STOREPASS $jarPath $env:SUPREME_CODESIGN_ALIAS
  if ($LASTEXITCODE -ne 0) {
    throw "jarsigner failed"
  }
  $signingMode = "jarsigner"
} elseif ($RequireRealSigning) {
  throw "Real code-signing keystore is required. Set SUPREME_CODESIGN_KEYSTORE, SUPREME_CODESIGN_ALIAS and SUPREME_CODESIGN_STOREPASS."
}

$hash = (Get-FileHash -LiteralPath $jarPath -Algorithm SHA256).Hash.ToLowerInvariant()
$manifest = [ordered]@{
  artifact = "supreme-iped-plugin.jar"
  artifact_sha256 = $hash
  plugin_version = "SUPREME-IPED-PLUGIN-1.0.0"
  protocol_version = "SUPREME-FIELD-EVENTS-1.0"
  build_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
  iped_extension_point = "iped.viewers.api.ResultSetViewer"
  iped_release = $ipedReleasePath
  signing_mode = $signingMode
  production_signing_required = $true
}
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifestPath -Encoding UTF8

Write-Host "SUPREME IPED plugin built: $jarPath"
Write-Host "SHA256: $hash"
Write-Host "Signing mode: $signingMode"
