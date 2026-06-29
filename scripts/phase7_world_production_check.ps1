param(
  [string]$Root = ".",
  [string]$PythonExe = "python",
  [switch]$SkipDockerChecks
)

$ErrorActionPreference = "Stop"
$Failures = New-Object System.Collections.Generic.List[string]

function Fail([string]$Message) {
  $Failures.Add($Message) | Out-Null
  Write-Host "[FAIL] $Message" -ForegroundColor Red
}

function Pass([string]$Message) {
  Write-Host "[ OK ] $Message" -ForegroundColor Green
}

function Require-File([string]$Path) {
  if (Test-Path -LiteralPath $Path) { Pass "File present: $Path" } else { Fail "Missing file: $Path" }
}

function Require-Text([string]$Path, [string]$Pattern, [string]$Label) {
  if (-not (Test-Path -LiteralPath $Path)) {
    Fail "Missing file for text check: $Path"
    return
  }
  $content = Get-Content -LiteralPath $Path -Raw
  if ($content -match $Pattern) { Pass "$Label" } else { Fail "$Label not found in $Path" }
}

$rootPath = (Resolve-Path -LiteralPath $Root).Path
Push-Location $rootPath
try {
  Write-Host "SUPREME V4 Phase 7 world production gate" -ForegroundColor Cyan
  $powerShellExe = if ($PSVersionTable.PSEdition -eq "Desktop") { "powershell" } else { "pwsh" }

  $ledger = Get-Content -LiteralPath "docs\PHASE_EXECUTION_LEDGER.md" -Raw
  foreach ($phase in 0..6) {
    if ($ledger -match "## Phase $phase[\s\S]*?Status: 100_PERCENT_COMPLETE") {
      Pass "Phase $phase precondition complete"
    } else {
      Fail "Phase $phase is not marked 100_PERCENT_COMPLETE"
    }
  }

  foreach ($path in @(
    ".github\workflows\ci.yml",
    "docker-compose.production.yml",
    "docker-compose.staging.yml",
    "env\.env.staging.example",
    "supreme-backend\.env.staging.example",
    "sentinela\.env.staging.example",
    "scripts\phase7_nist_cftt_benchmark.py",
    "scripts\phase7_observability_slo_check.ps1",
    "scripts\phase7_backup_restore_check.ps1",
    "scripts\phase7_release_provenance.ps1",
    "scripts\build_phase7_world_release.ps1",
    "docs\PHASE_SEVEN_WORLD_PRODUCTION.md",
    "docs\STAGING_DEPLOYMENT.md",
    "docs\SLO_OBSERVABILITY.md",
    "docs\BACKUP_RESTORE_DR.md",
    "docs\PHASE_SEVEN_NIST_CFTT_BENCHMARK.md",
    "docs\WHITEPAPER_SUPREME_V4.md",
    "docs\audit\SECURITY_EXTERNAL_AUDIT_PACKAGE.md",
    "docs\audit\STATISTICAL_METHODOLOGICAL_AUDIT_PACKAGE.md",
    "docs\roles\DEVELOPER.md",
    "docs\roles\RESEARCHER.md",
    "docs\roles\AUDITOR.md",
    "docs\roles\OPERATOR.md",
    "docs\runbooks\API_DOWN.md",
    "docs\runbooks\SENTINELA_DOWN.md",
    "docs\runbooks\DATABASE_UNAVAILABLE.md",
    "docs\runbooks\REDIS_UNAVAILABLE.md",
    "docs\runbooks\DLQ_NON_EMPTY.md",
    "docs\runbooks\IPED_INGEST_STOPPED.md",
    "docs\runbooks\TLS_CERTIFICATE.md",
    "docs\runbooks\RESTORE_EMERGENCY.md",
    "docs\runbooks\SECRET_LEAK.md",
    "docs\runbooks\LGPD_REVOCATION.md",
    "docs\runbooks\PIPELINE_STUCK.md"
  )) { Require-File $path }

  Require-Text ".github\workflows\ci.yml" "phase7_world_production_check" "CI runs Phase 7 gate"
  Require-Text ".github\workflows\ci.yml" "secret_scan" "CI runs secret scan"
  Require-Text ".github\workflows\ci.yml" "dependency_scan" "CI runs dependency scan"
  Require-Text ".github\workflows\ci.yml" "sast_scan" "CI runs SAST"
  Require-Text ".github\workflows\ci.yml" "generate_sbom" "CI generates SBOM"
  Require-Text ".github\workflows\ci.yml" "docker save" "CI publishes image digest artifacts"
  Require-Text "docker-compose.staging.yml" "supreme_v4_staging" "Staging uses isolated named volumes"
  Require-Text "sentinela\src\app\api\export.py" "algorithm_version" "Exports include algorithm version"
  Require-Text "sentinela\src\app\api\export.py" "algorithm_parameters" "Exports include algorithm parameters"
  Require-Text "sentinela\src\app\api\product.py" "viewer-only" "SENTINELA product remains viewer-only"
  Require-Text "docs\PHASE_FIVE_REAL_IPED_TEST_20260623.md" "Real IPED acceptance is APPROVED" "Real IPED acceptance recorded"

  $benchmarkScript = Join-Path $rootPath "scripts/phase7_nist_cftt_benchmark.py"
  & $PythonExe $benchmarkScript --root $rootPath
  if ($LASTEXITCODE -ne 0) { Fail "Phase 7 benchmark failed" } else { Pass "Phase 7 benchmark passed" }

  $sloScript = Join-Path $rootPath "scripts/phase7_observability_slo_check.ps1"
  & $powerShellExe -NoProfile -ExecutionPolicy Bypass -File $sloScript -Root $rootPath
  if ($LASTEXITCODE -ne 0) { Fail "Phase 7 SLO gate failed" } else { Pass "Phase 7 SLO gate passed" }

  if (-not (Test-Path -LiteralPath "reports\phase7\release_provenance.json")) {
    $provenanceScript = Join-Path $rootPath "scripts/phase7_release_provenance.ps1"
    & $powerShellExe -NoProfile -ExecutionPolicy Bypass -File $provenanceScript -Root $rootPath
  }
  Require-File "reports\phase7\release_provenance.json"
  Require-Text "reports\phase7\release_provenance.json" "provenance_signature_sha256" "Release provenance is signed by digest"

  if (-not $SkipDockerChecks) {
    & docker compose --env-file env\.env.staging.example -f docker-compose.production.yml -f docker-compose.staging.yml config --quiet
    if ($LASTEXITCODE -ne 0) { Fail "Staging compose config failed" } else { Pass "Staging compose config is valid" }
  } else {
    Pass "Docker compose check skipped by explicit flag"
  }

  $report = "docs\phase7_benchmark\benchmark_report.json"
  if (Test-Path -LiteralPath $report) {
    $bench = Get-Content -LiteralPath $report -Raw | ConvertFrom-Json
    if ($bench.status -eq "ok") { Pass "Benchmark report status ok" } else { Fail "Benchmark report status is not ok" }
  } else {
    Fail "Benchmark report missing"
  }

  Write-Host "Resumo Fase 7: $($Failures.Count) falha(s)."
  if ($Failures.Count -gt 0) { exit 1 }
}
finally {
  Pop-Location
}

