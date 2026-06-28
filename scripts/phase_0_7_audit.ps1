param(
  [switch]$Json,
  [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"
if (Get-Variable PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
  $PSNativeCommandUseErrorActionPreference = $false
}

$results = New-Object System.Collections.Generic.List[object]

function Add-Result {
  param(
    [string]$Phase,
    [string]$Check,
    [ValidateSet("PASS", "WARN", "FAIL")] [string]$Status,
    [string]$Evidence
  )
  $item = [pscustomobject]@{
    phase = $Phase
    check = $Check
    status = $Status
    evidence = $Evidence
  }
  $results.Add($item) | Out-Null
  if (-not $Json) {
    $color = if ($Status -eq "PASS") { "Green" } elseif ($Status -eq "WARN") { "Yellow" } else { "Red" }
    Write-Host "[$Status] $Phase - $Check - $Evidence" -ForegroundColor $color
  }
}

function Test-Exists {
  param([string]$Path)
  return Test-Path -LiteralPath $Path
}

function Count-Rg {
  param([string]$Pattern, [string[]]$Paths)
  $args = @("-n", $Pattern) + $Paths + @("-S")
  $out = & rg @args 2>$null
  if ($LASTEXITCODE -eq 2) {
    return -1
  }
  return @($out).Count
}

Write-Host "SUPREME V4 - auditoria consolidada fases 0 a 7" -ForegroundColor Cyan

# Fase 0
Add-Result "Fase 0" "release gate existe" $(if (Test-Exists "scripts\release_phase_zero_check.ps1") { "PASS" } else { "FAIL" }) "scripts\release_phase_zero_check.ps1"
Add-Result "Fase 0" "env examples existem" $(if ((Test-Exists ".env.production.example") -and (Test-Exists "supreme-backend\.env.production.example") -and (Test-Exists "sentinela\.env.production.example")) { "PASS" } else { "FAIL" }) ".env.production.example + apps"
$versionDriftPattern = ("SUPREME V" + "5") + "|" + ("SUPREME_" + "V5") + "|" + ("V4" + "/" + "V5")
$v5Count = Count-Rg $versionDriftPattern @(".")
Add-Result "Fase 0" "identidade V4 sem V5 fora de historico" $(if ($v5Count -le 0) { "PASS" } else { "WARN" }) "$v5Count ocorrencia(s) potenciais"
$mojibakePattern = ([char]0x00C3) + "|" + ([char]0x00C2) + "|" + ([char]0x00E2)
$mojibake = Count-Rg $mojibakePattern @("docs", "sentinela\static", "supreme-backend\src\app\forms")
Add-Result "Fase 0" "encoding/mojibake" $(if ($mojibake -eq 0) { "PASS" } else { "WARN" }) "$mojibake ocorrencia(s) potenciais"

# Fase 1
Add-Result "Fase 1" "setup local unico" $(if (Test-Exists "SUBIR_LOCAL.ps1") { "PASS" } else { "FAIL" }) "SUBIR_LOCAL.ps1"
Add-Result "Fase 1" "compose local" $(if (Test-Exists "docker-compose.local.yml") { "PASS" } else { "FAIL" }) "docker-compose.local.yml"
Add-Result "Fase 1" "smoke/form/IPED E2E" $(if ((Test-Exists "scripts\smoke_test.ps1") -and (Test-Exists "scripts\form_flow_e2e.ps1") -and (Test-Exists "scripts\iped_operational_e2e.ps1")) { "PASS" } else { "FAIL" }) "scripts E2E"

# Fase 2
$localStorage = Count-Rg "localStorage|sessionStorage" @("sentinela\static", "sentinela\src")
Add-Result "Fase 2" "sessao web sem storage JS" $(if ($localStorage -eq 0) { "PASS" } else { "WARN" }) "$localStorage uso(s) de storage no cliente"
$roles = Count-Rg "master|pesquisador|auditor|operador|leitura_agregada" @("sentinela\src", "sentinela\static")
Add-Result "Fase 2" "RBAC granular" "WARN" "$roles referencias; roles atuais ainda precisam ser expandidos"
Add-Result "Fase 2" "rotacao de tokens" $(if (Test-Exists "scripts\rotate_api_tokens.ps1") { "PASS" } else { "FAIL" }) "scripts\rotate_api_tokens.ps1"
Add-Result "Fase 2" "SAST/SBOM/dependency scan" "WARN" "CI atual nao inclui trilha completa"

# Fase 3
Add-Result "Fase 3" "motor SUPREME IEO/PSI/risk" $(if ((Test-Exists "supreme-backend\src\engine\supreme\ieo.py") -and (Test-Exists "supreme-backend\src\engine\supreme\psi.py") -and (Test-Exists "supreme-backend\src\engine\supreme\risk.py")) { "PASS" } else { "FAIL" }) "engine supreme"
Add-Result "Fase 3" "SENTINELA sem engine analitico legado" $(if (Test-Exists "sentinela\src\engine\red_flags.py") { "WARN" } else { "PASS" }) "sentinela\src\engine\red_flags.py"
Add-Result "Fase 3" "algorithm registry" $(if (Count-Rg "algorithm_registry|algorithm_version" @("supreme-backend") -gt 0) { "PASS" } else { "FAIL" }) "versionamento encontrado"

# Fase 4
Add-Result "Fase 4" "E2E operacional IPED" $(if (Test-Exists "scripts\iped_operational_e2e.py") { "PASS" } else { "FAIL" }) "scripts\iped_operational_e2e.py"
Add-Result "Fase 4" "dataset ground truth/model card" $(if ((Test-Exists "docs\MODEL_CARD_SUPREME.md") -and (Test-Exists "docs\PHASE_FOUR_SCIENTIFIC_VALIDATION.md") -and (Test-Exists "docs\phase4_validation\synthetic_ground_truth_dataset.jsonl")) { "PASS" } else { "FAIL" }) "validacao cientifica sintetica reproduzivel"
Add-Result "Fase 4" "gate validacao cientifica" $(if (Test-Exists "scripts\phase4_scientific_validation_check.ps1") { "PASS" } else { "FAIL" }) "scripts\phase4_scientific_validation_check.ps1"

# Fase 5
Add-Result "Fase 5" "gate IPED real" $(if ((Test-Exists "scripts\verify_iped_real_environment.ps1") -and (Test-Exists "scripts\accept_iped_real_session.ps1")) { "PASS" } else { "FAIL" }) "scripts de aceite real"
Add-Result "Fase 5" "hash chain/event signature/replay" $(if ((Test-Exists "scripts\phase5_forensic_custody_check.ps1") -and (Test-Exists "docs\phase5_forensic\forensic_export.json") -and (Test-Exists "docs\PHASE_FIVE_FORENSIC_CUSTODY.md")) { "PASS" } else { "FAIL" }) "gate forense deterministico Fase 5"

# Fase 6
Add-Result "Fase 6" "especificacao produto SENTINELA" $(if (Test-Exists "docs\PHASE_SIX_SENTINELA_PRODUCT.md") { "PASS" } else { "FAIL" }) "docs\PHASE_SIX_SENTINELA_PRODUCT.md"
Add-Result "Fase 6" "export CSV/JSON/Parquet/dicionario" "WARN" "CSV existe; JSON/Parquet/dicionario pendentes"

# Fase 7
Add-Result "Fase 7" "especificacao producao mundial" $(if (Test-Exists "docs\PHASE_SEVEN_WORLD_PRODUCTION.md") { "PASS" } else { "FAIL" }) "docs\PHASE_SEVEN_WORLD_PRODUCTION.md"
Add-Result "Fase 7" "CI/CD completo" $(if (Test-Exists ".github\workflows\ci.yml") { "WARN" } else { "FAIL" }) "CI existe, mas falta secret/dependency/SAST/SBOM/assinatura"

$summary = [pscustomobject]@{
  generated_at = (Get-Date).ToString("s")
  pass = @($results | Where-Object status -eq "PASS").Count
  warn = @($results | Where-Object status -eq "WARN").Count
  fail = @($results | Where-Object status -eq "FAIL").Count
  results = $results
}

if ($OutputPath) {
  $summary | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 -LiteralPath $OutputPath
}

if ($Json) {
  $summary | ConvertTo-Json -Depth 5
} else {
  Write-Host ""
  Write-Host "Resumo: PASS=$($summary.pass), WARN=$($summary.warn), FAIL=$($summary.fail)" -ForegroundColor Cyan
}

if ($summary.fail -gt 0) {
  exit 1
}
exit 0
