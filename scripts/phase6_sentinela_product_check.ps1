param(
  [string]$Root = ".",
  [string]$AuditLog = "tmp\iped-audit\supreme_audit.ndjson"
)

$ErrorActionPreference = "Stop"
$failures = New-Object System.Collections.Generic.List[string]
$blockers = New-Object System.Collections.Generic.List[string]

function Add-Failure([string]$Message) {
  $failures.Add($Message) | Out-Null
  Write-Host "[FAIL] $Message" -ForegroundColor Red
}

function Add-Pass([string]$Message) {
  Write-Host "[PASS] $Message" -ForegroundColor Green
}

function Add-Blocker([string]$Message) {
  $blockers.Add($Message) | Out-Null
  Write-Host "[BLOCKER] $Message" -ForegroundColor Yellow
}

function Test-File([string]$RelativePath) {
  return Test-Path -LiteralPath (Join-Path $Root $RelativePath)
}

function Read-Text([string]$RelativePath) {
  return Get-Content -LiteralPath (Join-Path $Root $RelativePath) -Raw -Encoding UTF8
}

Write-Host "SUPREME V4 - Phase 6 SENTINELA product check" -ForegroundColor Cyan

foreach ($path in @(
  "sentinela\src\app\api\product.py",
  "sentinela\src\app\api\export.py",
  "sentinela\src\app\auth.py",
  "sentinela\static\index.html",
  "sentinela\tests\test_phase6_product.py"
)) {
  if (Test-File $path) { Add-Pass "Required file exists: $path" } else { Add-Failure "Missing required file: $path" }
}

if (Test-File "sentinela\src\app\api\product.py") {
  $product = Read-Text "sentinela\src\app\api\product.py"
  foreach ($needle in @(
    'prefix="/api/product"',
    '@router.get("/workspace")',
    '@router.get("/studies")',
    '@router.get("/participants")',
    '@router.get("/pipeline-health")',
    '@router.get("/data-quality")',
    '@router.get("/report/html")',
    '@router.get("/report/pdf")',
    'X-SENTINELA-Report-Signature',
    'not_automatic_causal_nexus'
  )) {
    if ($product.Contains($needle)) { Add-Pass "Product endpoint/evidence present: $needle" } else { Add-Failure "Product endpoint/evidence missing: $needle" }
  }
}

if (Test-File "sentinela\src\app\api\export.py") {
  $export = Read-Text "sentinela\src\app\api\export.py"
  foreach ($needle in @(
    '@router.get("/csv"',
    '@router.get("/json"',
    '@router.get("/parquet"',
    '@router.get("/data-dictionary"',
    'algorithm_version',
    'algorithm_parameters',
    'X-SENTINELA-Export-Signature'
  )) {
    if ($export.Contains($needle)) { Add-Pass "Export endpoint/evidence present: $needle" } else { Add-Failure "Export endpoint/evidence missing: $needle" }
  }
}

if (Test-File "sentinela\src\app\auth.py") {
  $auth = Read-Text "sentinela\src\app\auth.py"
  foreach ($needle in @(
    'product:studies',
    'product:participants',
    'product:pipeline',
    'product:data_quality',
    'report:signed',
    'participant_registry pr_scope',
    'institution_id',
    'study_id',
    'case_id'
  )) {
    if ($auth.Contains($needle)) { Add-Pass "RBAC/scope evidence present: $needle" } else { Add-Failure "RBAC/scope evidence missing: $needle" }
  }
}

if (Test-File "sentinela\static\index.html") {
  $ui = Read-Text "sentinela\static\index.html"
  foreach ($needle in @(
    'section-studies',
    'section-pipeline',
    'section-dataquality',
    'section-exports',
    '/api/product/studies',
    '/api/product/pipeline-health',
    '/api/product/data-quality',
    '/api/product/report/pdf',
    'Nenhum estudo',
    'Sem dados de qualidade'
  )) {
    if ($ui.Contains($needle)) { Add-Pass "UI product evidence present: $needle" } else { Add-Failure "UI product evidence missing: $needle" }
  }
}

$scanTargets = @(
  "sentinela\src\app\api\dashboard.py",
  "sentinela\src\app\api\export.py",
  "sentinela\src\app\api\product.py",
  "sentinela\static\index.html",
  "sentinela\static\war_room.html"
)
foreach ($target in $scanTargets) {
  if (-not (Test-File $target)) { continue }
  $text = Read-Text $target
  foreach ($pattern in @("compute_ieo(", "compute_psi(", "evaluate_red_flags(", "check_critical_load(")) {
    if ($text.Contains($pattern)) {
      Add-Failure "Critical analytical calculation pattern found in SENTINELA viewer file ${target}: $pattern"
    }
  }
}
if ($failures.Count -eq 0) { Add-Pass "No critical calculation function calls found in SENTINELA viewer files." }

$auditPath = if ([System.IO.Path]::IsPathRooted($AuditLog)) { $AuditLog } else { Join-Path $Root $AuditLog }
$realIpedDocApproved = $false
if (Test-File "docs\PHASE_FIVE_REAL_IPED_TEST_20260623.md") {
  $ipedDoc = Read-Text "docs\PHASE_FIVE_REAL_IPED_TEST_20260623.md"
  if ($ipedDoc.Contains("Status: APPROVED FOR PHASE 6") -and $ipedDoc.Contains("Real IPED acceptance is APPROVED")) {
    Add-Pass "Real IPED acceptance document is approved for Phase 6."
    $realIpedDocApproved = $true
  } else {
    Add-Blocker "Real IPED acceptance document is not approved for Phase 6."
  }
} else {
  Add-Failure "Missing real IPED acceptance document."
}

if (Test-Path -LiteralPath $auditPath) {
  $processable = 0
  foreach ($line in Get-Content -LiteralPath $auditPath) {
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    try {
      $entry = $line | ConvertFrom-Json
      if ($entry.event -in @("close", "classification_event") -and $entry.itemId -and $entry.openTs -and $entry.closeTs -and $entry.userId) {
        $processable += 1
      }
    } catch {
      Add-Failure "Invalid NDJSON line in real IPED audit log: $line"
    }
  }
  if ($processable -gt 0) {
    Add-Pass "Real IPED audit log has $processable processable line(s): $auditPath"
  } else {
    Add-Blocker "Real IPED audit log exists but has no processable close/classification_event lines: $auditPath"
  }
} else {
  Add-Blocker "Real IPED audit log not found: $auditPath"
}

if (Get-Command docker -ErrorAction SilentlyContinue) {
  $composeProjectName = if ($env:COMPOSE_PROJECT_NAME) { $env:COMPOSE_PROJECT_NAME } else { "supreme-v4-test-clone" }
  $dbOut = & docker compose -p $composeProjectName -f (Join-Path $Root "docker-compose.production.yml") -f (Join-Path $Root "docker-compose.local.yml") exec -T supreme-db psql -U supreme -d supreme -tAc "SELECT COUNT(*) FROM events_raw WHERE source_tool='iped' AND (created_at >= now() - interval '2 hours' OR timestamp >= now() - interval '2 hours');" 2>&1
  if ($LASTEXITCODE -eq 0) {
    $dbCount = 0
    [int]::TryParse((($dbOut | Out-String).Trim()), [ref]$dbCount) | Out-Null
    if ($dbCount -gt 0) {
      Add-Pass "SUPREME database has $dbCount recently ingested source_tool='iped' event(s)."
    } else {
      Add-Blocker "SUPREME database has no recently ingested source_tool='iped' event."
    }
  } else {
    Add-Blocker "Could not query SUPREME database for real IPED evidence: $dbOut"
  }
} elseif ($realIpedDocApproved) {
  Add-Blocker "Docker not available to confirm real IPED database ingestion."
}

Write-Host ""
Write-Host "Phase 6 SENTINELA product check summary: $($failures.Count) failure(s), $($blockers.Count) blocker(s)." -ForegroundColor Cyan
if ($failures.Count -gt 0 -or $blockers.Count -gt 0) {
  exit 1
}
exit 0
