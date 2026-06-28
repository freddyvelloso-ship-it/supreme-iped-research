param(
  [string]$Root = "."
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

$rootPath = (Resolve-Path -LiteralPath $Root).Path
Push-Location $rootPath
try {
  $sloDoc = "docs\SLO_OBSERVABILITY.md"
  $rules = "infra\prometheus\alert_rules.yml"
  if (-not (Test-Path -LiteralPath $sloDoc)) { Fail "SLO doc missing: $sloDoc" }
  if (-not (Test-Path -LiteralPath $rules)) { Fail "Prometheus rules missing: $rules" }
  if (Test-Path -LiteralPath $sloDoc) {
    $content = Get-Content -LiteralPath $sloDoc -Raw
    foreach ($required in @("99.5", "p95", "DLQ", "burn rate", "restore")) {
      if ($content -notmatch [regex]::Escape($required)) { Fail "SLO doc missing marker: $required" }
    }
    Pass "SLO document contains availability, latency, DLQ and restore objectives"
  }
  if (Test-Path -LiteralPath $rules) {
    $content = Get-Content -LiteralPath $rules -Raw
    foreach ($required in @("APIIndisponivel", "SENTINELAIndisponivel", "RedisIndisponivel", "PostgreSQLIndisponivel", "DLQNaoVazia", "SLOBurnRateAPI", "SLOBurnRatePipeline")) {
      if ($content -notmatch [regex]::Escape($required)) { Fail "Alert rules missing: $required" }
    }
    Pass "Prometheus rules contain availability and burn-rate alerts"
  }
  Write-Host "Resumo Fase 7 SLO: $($Failures.Count) falha(s)."
  if ($Failures.Count -gt 0) { exit 1 }
}
finally {
  Pop-Location
}

