param(
    [string]$Root = ".",
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"
$rootPath = (Resolve-Path -LiteralPath $Root).Path
$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure([string]$Message) {
    $failures.Add($Message) | Out-Null
}

$required = @(
    "scripts\phase5_forensic_custody.py",
    "scripts\phase5_forensic_custody_check.ps1",
    "docs\phase5_forensic\signed_events.jsonl",
    "docs\phase5_forensic\input_hash_chain.json",
    "docs\phase5_forensic\processing_hash_chain.json",
    "docs\phase5_forensic\output_hash_chain.json",
    "docs\phase5_forensic\admin_audit_log.jsonl",
    "docs\phase5_forensic\session_manifest.json",
    "docs\phase5_forensic\integrity_report.json",
    "docs\phase5_forensic\forensic_export.json",
    "docs\PHASE_FIVE_FORENSIC_CUSTODY.md",
    "supreme-backend\tests\test_phase5_forensic_custody.py"
)

foreach ($relative in $required) {
    if (-not (Test-Path -LiteralPath (Join-Path $rootPath $relative))) {
        Add-Failure "Arquivo obrigatorio ausente: $relative"
    }
}

$exportPath = Join-Path $rootPath "docs\phase5_forensic\forensic_export.json"
if (Test-Path -LiteralPath $exportPath) {
    $exportText = Get-Content -LiteralPath $exportPath -Raw -Encoding UTF8
    foreach ($forbidden in @("IPED-local", "PRIVATE KEY", "BEGIN CERTIFICATE", "BOOTSTRAP_TOKEN", "PASSWORD=", "SALT=", "API_KEY=", ".E01", ".dump", ".db")) {
        if ($exportText -match [regex]::Escape($forbidden)) {
            Add-Failure "Export forense contem marcador proibido: $forbidden"
        }
    }
    $export = $exportText | ConvertFrom-Json
    if ($export.manifest.evidence_mode -ne "simulated_iped") {
        Add-Failure "Manifesto deve diferenciar evidencia simulada de IPED real."
    }
    foreach ($field in @("iped", "iped_patch", "proxy", "watcher", "supreme", "sentinela", "algorithm")) {
        if (-not $export.manifest.versions.$field) {
            Add-Failure "Manifesto sem versao obrigatoria: $field"
        }
    }
    if ($export.integrity_report.status -ne "verifiable") {
        Add-Failure "Relatorio de integridade nao esta verificavel."
    }
    if ($export.integrity_report.signed_event_count -lt 1) {
        Add-Failure "Relatorio de integridade sem eventos assinados."
    }
}

if ($failures.Count -eq 0) {
    Push-Location $rootPath
    try {
        & $PythonExe "scripts\phase5_forensic_custody.py" check
        if ($LASTEXITCODE -ne 0) {
            Add-Failure "Verificacao deterministica da cadeia forense falhou."
        }
    }
    finally {
        Pop-Location
    }
}

if ($failures.Count -gt 0) {
    Write-Host "Phase 5 forensic custody check FAILED"
    foreach ($failure in $failures) {
        Write-Host "FAIL: $failure"
    }
    exit 1
}

Write-Host "Phase 5 forensic custody check PASSED"
Write-Host "Resumo Fase 5: 0 falha(s)"

