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
    "scripts\phase4_scientific_validation.py",
    "docs\phase4_validation\synthetic_ground_truth_dataset.jsonl",
    "docs\phase4_validation\validation_metrics.json",
    "docs\phase4_validation\GROUND_TRUTH.md",
    "docs\PHASE_FOUR_SCIENTIFIC_VALIDATION.md",
    "docs\MODEL_CARD_SUPREME.md",
    "supreme-backend\tests\test_phase4_scientific_validation.py"
)

foreach ($relative in $required) {
    if (-not (Test-Path -LiteralPath (Join-Path $rootPath $relative))) {
        Add-Failure "Arquivo obrigatorio ausente: $relative"
    }
}

$datasetPath = Join-Path $rootPath "docs\phase4_validation\synthetic_ground_truth_dataset.jsonl"
if (Test-Path -LiteralPath $datasetPath) {
    $datasetText = Get-Content -LiteralPath $datasetPath -Raw -Encoding UTF8
    foreach ($scenario in @("baixo_risco", "reatividade", "dissonancia", "cronicidade", "convergencia_critica")) {
        if ($datasetText -notmatch [regex]::Escape($scenario)) {
            Add-Failure "Dataset sem scenario obrigatorio: $scenario"
        }
    }
    foreach ($forbidden in @("IPED-local", "PRIVATE KEY", "BEGIN CERTIFICATE", "BOOTSTRAP_TOKEN", "PASSWORD=", "SALT=", "API_KEY=")) {
        if ($datasetText -match [regex]::Escape($forbidden)) {
            Add-Failure "Dataset contem marcador proibido: $forbidden"
        }
    }
}

$metricsPath = Join-Path $rootPath "docs\phase4_validation\validation_metrics.json"
if (Test-Path -LiteralPath $metricsPath) {
    $metrics = Get-Content -LiteralPath $metricsPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($metrics.algorithm_version -ne "SUPREME-ANALYTICS-1.0.0") {
        Add-Failure "Metrics com algorithm_version inesperado."
    }
    if ($metrics.seed -ne 424242) {
        Add-Failure "Metrics com seed inesperado."
    }
    if (-not $metrics.dataset.digest_sha256) {
        Add-Failure "Metrics sem digest de dataset."
    }
    if ($metrics.external_independent_validation -ne "not_performed") {
        Add-Failure "Metrics deve diferenciar validacao externa independente como nao realizada."
    }
}

if ($failures.Count -eq 0) {
    Push-Location $rootPath
    try {
        & $PythonExe "scripts\phase4_scientific_validation.py" check
        if ($LASTEXITCODE -ne 0) {
            Add-Failure "Recomputacao deterministica da validacao falhou."
        }
    }
    finally {
        Pop-Location
    }
}

if ($failures.Count -gt 0) {
    Write-Host "Phase 4 scientific validation check FAILED"
    foreach ($failure in $failures) {
        Write-Host "FAIL: $failure"
    }
    exit 1
}

Write-Host "Phase 4 scientific validation check PASSED"
Write-Host "Resumo Fase 4: 0 falha(s)"
