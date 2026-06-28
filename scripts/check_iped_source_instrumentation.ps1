param(
  [string]$IpedSourceRoot = ".\tmp\iped-src"
)

$ErrorActionPreference = "Stop"
$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure([string]$Message) {
  $failures.Add($Message) | Out-Null
  Write-Host "[FAIL] $Message" -ForegroundColor Red
}

function Add-Pass([string]$Message) {
  Write-Host "[PASS] $Message" -ForegroundColor Green
}

function Require-File([string]$Path) {
  if (Test-Path -LiteralPath $Path) {
    Add-Pass "File exists: $Path"
    return $true
  }
  Add-Failure "Missing file: $Path"
  return $false
}

Write-Host "SUPREME V4 - real IPED source instrumentation check" -ForegroundColor Cyan

$listener = Join-Path $IpedSourceRoot "iped-app\src\main\java\iped\app\ui\ResultTableListener.java"
$model = Join-Path $IpedSourceRoot "iped-app\src\main\java\iped\app\ui\ResultTableModel.java"
$logger = Join-Path $IpedSourceRoot "iped-app\src\main\java\iped\app\ui\SupremeAuditLogger.java"
$loader = Join-Path $IpedSourceRoot "iped-app\src\main\java\iped\app\ui\UICaseDataLoader.java"

$listenerOk = Require-File $listener
$modelOk = Require-File $model
$loggerOk = Require-File $logger
$loaderOk = Require-File $loader

if ($listenerOk) {
  $text = Get-Content -LiteralPath $listener -Raw -Encoding UTF8
  foreach ($needle in @(
    "SupremeAuditLogger.onItemClose",
    "SupremeAuditLogger.onItemOpen",
    "getSearcher().doc",
    "supremePreviousDocId",
    "logger.warn(""SUPREME audit hook failed"
  )) {
    if ($text.Contains($needle)) { Add-Pass "ResultTableListener contains: $needle" } else { Add-Failure "ResultTableListener missing: $needle" }
  }
}

if ($loaderOk) {
  $text = Get-Content -LiteralPath $loader -Raw -Encoding UTF8
  foreach ($needle in @(
    "SUPREME audit case-load probe emitted",
    "getLuceneIdStream().findFirst()",
    "SupremeAuditLogger.onItemOpen",
    "SupremeAuditLogger.onItemClose",
    "LOGGER.warn(""SUPREME audit case-load probe failed"
  )) {
    if ($text.Contains($needle)) { Add-Pass "UICaseDataLoader contains: $needle" } else { Add-Failure "UICaseDataLoader missing: $needle" }
  }
}

if ($modelOk) {
  $text = Get-Content -LiteralPath $model -Raw -Encoding UTF8
  foreach ($needle in @(
    "SupremeAuditLogger.onBookmark",
    "getSearcher().doc",
    "Boolean.TRUE.equals(value)",
    "supremeBookmarkDocId"
  )) {
    if ($text.Contains($needle)) { Add-Pass "ResultTableModel contains: $needle" } else { Add-Failure "ResultTableModel missing: $needle" }
  }
}

if ($loggerOk) {
  $text = Get-Content -LiteralPath $logger -Raw -Encoding UTF8
  foreach ($needle in @(
    "SUPREME_AUDIT_LOG",
    "SUPREME_USER_ID",
    "supreme_audit.ndjson",
    "onItemOpen",
    "onItemClose",
    "onBookmark"
  )) {
    if ($text.Contains($needle)) { Add-Pass "SupremeAuditLogger contains: $needle" } else { Add-Failure "SupremeAuditLogger missing: $needle" }
  }
}

Write-Host ""
Write-Host "Real IPED source instrumentation summary: $($failures.Count) failure(s)." -ForegroundColor Cyan
if ($failures.Count -gt 0) {
  exit 1
}
exit 0
