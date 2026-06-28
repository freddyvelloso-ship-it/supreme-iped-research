param(
  [string]$Root = ".",
  [string]$PythonExe = "python",
  [switch]$RequireProductionPrereqs
)

$ErrorActionPreference = "Stop"
$rootPath = (Resolve-Path -LiteralPath $Root).Path
$failures = New-Object System.Collections.Generic.List[string]
$blockers = New-Object System.Collections.Generic.List[string]

function Add-Pass([string]$Message) { Write-Host "[ OK ] $Message" -ForegroundColor Green }
function Add-Failure([string]$Message) { $failures.Add($Message) | Out-Null; Write-Host "[FAIL] $Message" -ForegroundColor Red }
function Add-Blocker([string]$Message) { $blockers.Add($Message) | Out-Null; Write-Host "[BLOCK] $Message" -ForegroundColor Yellow }

function Require-File([string]$Path) {
  $full = Join-Path $rootPath $Path
  if (Test-Path -LiteralPath $full) { Add-Pass "Exists: $Path" } else { Add-Failure "Missing: $Path" }
}

$ledger = Get-Content -LiteralPath (Join-Path $rootPath "docs\PHASE_EXECUTION_LEDGER.md") -Raw
foreach ($phase in 0..7) {
  if ($ledger -match "Phase $phase[\s\S]*?Status:\s+100_PERCENT_COMPLETE") {
    Add-Pass "Phase $phase is 100_PERCENT_COMPLETE"
  } else {
    Add-Failure "Phase $phase is not recorded as 100_PERCENT_COMPLETE"
  }
}

foreach ($file in @(
  "supreme-iped-plugin\src\main\java\com\supreme\iped\SupremeFieldTelemetryViewer.java",
  "supreme-iped-plugin\dist\supreme-iped-plugin.jar",
  "supreme-iped-plugin\dist\supreme-iped-plugin-manifest.json",
  "supreme-agent-windows\supreme_agent\agent.py",
  "supreme-agent-windows\supreme_agent\journey.py",
  "supreme-agent-windows\supreme_agent\pairing.py",
  "supreme-agent-windows\supreme_agent\mapper.py",
  "supreme-agent-windows\tests\test_agent_phase8.py",
  "scripts\install_supreme_iped_plugin.ps1",
  "scripts\test_phase8_plugin_install.ps1",
  "scripts\verify_supreme_iped_plugin.ps1",
  "scripts\phase8_field_forensic_replay.py",
  "docs\PHASE_EIGHT_FIELD_FORENSIC_ARCHITECTURE.md",
  "docs\IPED_PLUGIN_INSTALLATION.md",
  "docs\AGENT_WINDOWS_OPERATIONS.md",
  "docs\CENTRAL_SERVER_DEPLOYMENT.md",
  "docs\FIELD_CHAIN_OF_CUSTODY.md",
  "docs\EXTERNAL_SENTINELA_ACCESS.md",
  "docs\PHASE_EIGHT_LIMITATIONS_AND_BLOCKERS.md"
)) { Require-File $file }

$pluginSource = Get-Content -LiteralPath (Join-Path $rootPath "supreme-iped-plugin\src\main\java\com\supreme\iped\SupremeFieldTelemetryViewer.java") -Raw
foreach ($needle in @("implements ResultSetViewer", "addListSelectionListener", "session_start", "session_end", "item_open", "item_close", "image_view", "video_play", "classification_event")) {
  if ($pluginSource.Contains($needle)) { Add-Pass "Plugin contains $needle" } else { Add-Failure "Plugin missing $needle" }
}
if ($pluginSource.Contains("SupremeAuditLogger")) { Add-Failure "Plugin depends on legacy SupremeAuditLogger patch" } else { Add-Pass "Plugin does not depend on legacy SupremeAuditLogger" }

$agentSource = Get-Content -LiteralPath (Join-Path $rootPath "supreme-agent-windows\supreme_agent\agent.py") -Raw
foreach ($needle in @("send_central_ingest_with_retry", "build_central_ingest_request", "/v1/events/ingest", "Authorization")) {
  if ($agentSource.Contains($needle)) { Add-Pass "Agent contains $needle" } else { Add-Failure "Agent missing $needle" }
}

$journeySource = Get-Content -LiteralPath (Join-Path $rootPath "supreme-agent-windows\supreme_agent\journey.py") -Raw
foreach ($needle in @("PRE_SESSION_INSTRUMENTS", "POST_SESSION_INSTRUMENTS", "PANAS_SHORT", "wait_iped_close")) {
  if ($journeySource.Contains($needle)) { Add-Pass "Journey contains $needle" } else { Add-Failure "Journey missing $needle" }
}

$pairingSource = Get-Content -LiteralPath (Join-Path $rootPath "supreme-agent-windows\supreme_agent\pairing.py") -Raw
foreach ($needle in @("issue_device_credential", "validate_device_credential", "revoke_fingerprint", "institution_id", "study_id", "case_id", "participant_scope")) {
  if ($pairingSource.Contains($needle)) { Add-Pass "Pairing contains $needle" } else { Add-Failure "Pairing missing $needle" }
}

$manifestPath = Join-Path $rootPath "supreme-iped-plugin\dist\supreme-iped-plugin-manifest.json"
if (Test-Path -LiteralPath $manifestPath) {
  $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
  if ($manifest.signing_mode -eq "jarsigner") { Add-Pass "Plugin has real jarsigner signature mode" } else { Add-Blocker "Production code-signing certificate/keystore not supplied; current signing_mode=$($manifest.signing_mode)" }
}

if ($RequireProductionPrereqs) {
  if (-not $env:SUPREME_PRODUCTION_SENTINELA_URL -or $env:SUPREME_PRODUCTION_SENTINELA_URL -match "localhost|127\.0\.0\.1|example|invalid") {
    Add-Blocker "Production SENTINELA external URL/domain not supplied"
  }
  if (-not $env:SUPREME_CODESIGN_KEYSTORE) {
    Add-Blocker "Real code-signing keystore not supplied"
  }
}

& $PythonExe (Join-Path $rootPath "scripts\phase8_field_forensic_replay.py") --root $rootPath | Out-Host
if ($LASTEXITCODE -ne 0) { Add-Failure "Phase 8 field replay failed" } else { Add-Pass "Phase 8 field replay passed" }

Write-Host "Resumo Fase 8: $($failures.Count) falha(s), $($blockers.Count) bloqueio(s)." -ForegroundColor Cyan
if ($failures.Count -gt 0) { exit 1 }
if ($RequireProductionPrereqs -and $blockers.Count -gt 0) { exit 2 }
exit 0
