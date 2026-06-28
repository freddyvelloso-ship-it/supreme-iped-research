param(
    [string]$Root = "."
)

$ErrorActionPreference = "Stop"
$rootPath = (Resolve-Path -LiteralPath $Root).Path
$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure([string]$Message) {
    $failures.Add($Message) | Out-Null
}

function Read-Text([string]$RelativePath) {
    $path = Join-Path $rootPath $RelativePath
    if (-not (Test-Path -LiteralPath $path)) {
        Add-Failure "Arquivo obrigatorio ausente: $RelativePath"
        return ""
    }
    return Get-Content -LiteralPath $path -Raw -Encoding UTF8
}

$supremeAlgorithm = Read-Text "supreme-backend\src\engine\supreme\algorithm.py"
$supremeIeo = Read-Text "supreme-backend\src\engine\supreme\ieo.py"
$supremePsi = Read-Text "supreme-backend\src\engine\supreme\psi.py"
$supremeFlags = Read-Text "supreme-backend\src\engine\supreme\red_flags.py"
$pipeline = Read-Text "supreme-backend\src\worker\pipeline.py"
$sentinelaIngest = Read-Text "sentinela\src\app\api\ingest.py"
$sentinelaDashboard = Read-Text "sentinela\src\app\api\dashboard.py"
$sentinelaExport = Read-Text "sentinela\src\app\api\export.py"

if ($supremeAlgorithm -notmatch 'CURRENT_ALGORITHM_VERSION\s*=\s*"SUPREME-ANALYTICS-1\.0\.0"') {
    Add-Failure "SUPREME nao registra CURRENT_ALGORITHM_VERSION esperado."
}
foreach ($needle in @("def algorithm_parameters", "IEOParameters", "PSIParameters", "RedFlagParameters")) {
    if ($supremeAlgorithm -notmatch [regex]::Escape($needle)) {
        Add-Failure "Fonte unica de parametros sem '$needle'."
    }
}
foreach ($needle in @("def compute_ieo", "ALGORITHM_SPEC")) {
    if ($supremeIeo -notmatch [regex]::Escape($needle)) {
        Add-Failure "Motor IEO nao usa fonte unica versionada: $needle."
    }
}
foreach ($needle in @("def compute_psi", "CURRENT_ALGORITHM_VERSION", "ALGORITHM_SPEC")) {
    if ($supremePsi -notmatch [regex]::Escape($needle)) {
        Add-Failure "Motor PSI nao usa fonte unica versionada: $needle."
    }
}
foreach ($needle in @("def evaluate_red_flags", "CURRENT_ALGORITHM_VERSION", "ALGORITHM_SPEC")) {
    if ($supremeFlags -notmatch [regex]::Escape($needle)) {
        Add-Failure "Motor de red flags nao usa fonte unica versionada: $needle."
    }
}
foreach ($needle in @("check_critical_load", "_critical_load_psychometric_pair", "evaluate_red_flags", "algorithm_parameters")) {
    if ($pipeline -notmatch [regex]::Escape($needle)) {
        Add-Failure "Pipeline SUPREME sem evidencia obrigatoria: $needle."
    }
}
foreach ($needle in @("algorithm_version", "algorithm_parameters", "Nao calcula regra critica")) {
    if ($sentinelaIngest -notmatch [regex]::Escape($needle)) {
        Add-Failure "Ingest SENTINELA sem evidencia viewer-only/metadados: $needle."
    }
}
foreach ($needle in @("algorithm_version", "algorithm_parameters")) {
    if ($sentinelaDashboard -notmatch [regex]::Escape($needle)) {
        Add-Failure "Dashboard SENTINELA nao expoe metadados: $needle."
    }
    if ($sentinelaExport -notmatch [regex]::Escape($needle)) {
        Add-Failure "Export SENTINELA nao expoe metadados: $needle."
    }
}

$frontendFiles = @(
    "sentinela\static\index.html",
    "sentinela\static\war_room.html"
)
$forbiddenLiteral = @(
    "IEO_linear",
    "IEO_sat",
    "IEO_final",
    "PSI =",
    "threshold crítico",
    "IEO >",
    "IEO_z >",
    "1.5σ",
    "clinicamente elevada",
    "avaliação clínica",
    "Nível de Risco"
)
foreach ($relative in $frontendFiles) {
    $text = Read-Text $relative
    foreach ($pattern in $forbiddenLiteral) {
        if ($text.Contains($pattern)) {
            Add-Failure "Calculo/regra critica no frontend: $relative contem '$pattern'."
        }
    }
}

foreach ($relative in @(
    "supreme-backend\tests\test_unified_ieo_math.py",
    "supreme-backend\tests\test_unified_psi_math.py",
    "supreme-backend\tests\test_unified_red_flags_math.py",
    "supreme-backend\tests\test_phase3_determinism_and_versioning.py",
    "sentinela\tests\test_phase3_viewer_only.py"
)) {
    if (-not (Test-Path -LiteralPath (Join-Path $rootPath $relative))) {
        Add-Failure "Teste obrigatorio ausente: $relative"
    }
}

if ($failures.Count -gt 0) {
    Write-Host "Phase 3 analytics check FAILED"
    foreach ($failure in $failures) {
        Write-Host "FAIL: $failure"
    }
    exit 1
}

Write-Host "Phase 3 analytics check PASSED"
Write-Host "Resumo Fase 3: 0 falha(s)"
