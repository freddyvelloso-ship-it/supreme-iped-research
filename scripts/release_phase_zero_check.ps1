param(
  [string]$Root = "."
)

$ErrorActionPreference = "Stop"
$Failures = New-Object System.Collections.Generic.List[string]

function Add-Failure {
  param([string]$Message)
  $Failures.Add($Message) | Out-Null
  Write-Host "[FAIL] $Message" -ForegroundColor Red
}

function Add-Pass {
  param([string]$Message)
  Write-Host "[ OK ] $Message" -ForegroundColor Green
}

function Test-RequiredFile {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) {
    Add-Failure "Arquivo obrigatorio ausente: $Path"
  }
}

$rootPath = (Resolve-Path -LiteralPath $Root).Path
Push-Location $rootPath
try {
  Write-Host "SUPREME V4 Phase 0 release gate" -ForegroundColor Cyan

  foreach ($path in @(
    ".env.example",
    ".env.production.example",
    "supreme-backend/.env.production.example",
    "sentinela/.env.production.example",
    "env/README.md",
    "env/.env.local.example",
    "env/.env.demo.example",
    "env/.env.homologation.example",
    "env/.env.production.example",
    "docs/ENVIRONMENT_PROFILES.md"
  )) {
    Test-RequiredFile -Path $path
  }

  $forbiddenPaths = @(
    ".env",
    "supreme-backend/.env.production",
    "sentinela/.env.production",
    "certs/fullchain.pem",
    "certs/privkey.pem",
    "infra/prometheus/supreme-api-token.local",
    "infra/alertmanager/alertmanager.yml",
    "IPED-local",
    ".local",
    "backups"
  )

  foreach ($path in $forbiddenPaths) {
    if (Test-Path -LiteralPath $path) {
      Add-Failure "Artefato sensivel presente: $path"
    }
  }

  $nestedZips = Get-ChildItem -Recurse -File -Filter "*.zip" -ErrorAction SilentlyContinue
  foreach ($zip in $nestedZips) {
    Add-Failure "ZIP aninhado proibido no release: $($zip.FullName.Substring($rootPath.Length + 1))"
  }

  $forbiddenArtifacts = Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
      $_.Name -match "^(audit|supreme_audit).*\.ndjson$" -or
      $_.Extension -in @(".sqlite", ".sqlite3", ".db", ".duckdb", ".dump", ".bak", ".E01", ".Ex01", ".aff4", ".raw", ".dd", ".ad1", ".l01")
    }
  foreach ($artifact in $forbiddenArtifacts) {
    Add-Failure "Artefato local/forense proibido no release: $($artifact.FullName.Substring($rootPath.Length + 1))"
  }

  $scanFiles = Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
      $_.FullName -notmatch "\\__pycache__\\" -and
      $_.Extension -notin @(".exe", ".dll", ".jar", ".db", ".png", ".jpg", ".jpeg", ".mp4", ".zip")
    }

  foreach ($file in $scanFiles) {
    $relative = $file.FullName.Substring($rootPath.Length + 1)
    try {
      $content = Get-Content -LiteralPath $file.FullName -Raw -ErrorAction Stop
    } catch {
      continue
    }

    $isReleaseGate = $relative -eq "scripts\release_phase_zero_check.ps1"
    $isPhaseZeroBuild = $relative -eq "scripts\build_phase_zero_release.ps1"
    $isPhaseZeroDoc = $relative -eq "docs\PHASE_ZERO_RELEASE.md"

    if (-not $isReleaseGate -and -not $isPhaseZeroBuild -and -not $isPhaseZeroDoc -and $content -match "SUPREME V5|SUPREME_V5|V4/V5") {
      Add-Failure "Identidade de versao inconsistente em: $relative"
    }

    $isExample = $relative -match "\.md$|\.example$|\.env\.example$|\.env\.production\.example$|README|docs\\|AUDITORIA|RELATORIO|tests\\|env\\|scripts\\release_phase_zero_check\.ps1"
    if (-not $isExample) {
      if ($content -match "(?m)^\s*(API_SECRET_KEY|API_INGEST_TOKEN|SUPREME_SALT|BOOTSTRAP_TOKEN|GRAFANA_ADMIN_PASSWORD)\s*=\s*(?!CHANGE_ME|GERE_|dev_|test_|<|\$|%|\{)") {
        Add-Failure "Possivel segredo real em: $relative"
      }
      if ($content -match "-----BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY-----") {
        Add-Failure "Chave privada detectada em: $relative"
      }
    }
  }

  if ($Failures.Count -gt 0) {
    Write-Host ""
    Write-Host "Resumo: $($Failures.Count) falha(s)." -ForegroundColor Red
    exit 1
  }

  Add-Pass "Sem .env, certificados privados, tokens locais, ZIP aninhado ou identidade V5 fora do pacote IPED."
  Write-Host "Resumo: 0 falha(s)." -ForegroundColor Green
}
finally {
  Pop-Location
}
