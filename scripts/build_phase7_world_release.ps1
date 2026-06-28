param(
  [string]$Root = ".",
  [string]$OutputDir = "..\..\outputs",
  [string]$WorkDir = "..\..\tmp\phase7-release",
  [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"
$rootPath = (Resolve-Path -LiteralPath $Root).Path
Push-Location $rootPath
try {
  & powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase7_release_provenance.ps1 -Root .
  & $PythonExe scripts\phase7_nist_cftt_benchmark.py --root .
  if ($LASTEXITCODE -ne 0) { throw "Phase 7 benchmark failed before release" }
  & powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase7_world_production_check.ps1 -Root . -PythonExe $PythonExe -SkipDockerChecks
  if ($LASTEXITCODE -ne 0) { throw "Phase 7 gate failed before release" }
  & powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_phase_zero_release.ps1 -Root . -OutputDir $OutputDir -WorkDir $WorkDir -NamePrefix "supreme-v4-phase-seven-world-production"
}
finally {
  Pop-Location
}

