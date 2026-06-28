param(
  [string]$Root = "."
)

$ErrorActionPreference = "Stop"
$Failures = New-Object System.Collections.Generic.List[string]
$Warnings = New-Object System.Collections.Generic.List[string]

function Add-Failure {
  param([string]$Message)
  $Failures.Add($Message) | Out-Null
  Write-Host "[FAIL] $Message" -ForegroundColor Red
}

function Add-WarningMessage {
  param([string]$Message)
  $Warnings.Add($Message) | Out-Null
  Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Add-Pass {
  param([string]$Message)
  Write-Host "[ OK ] $Message" -ForegroundColor Green
}

function Test-FilePresent {
  param([string]$Path)
  if (Test-Path -LiteralPath $Path) {
    Add-Pass "Arquivo presente: $Path"
  } else {
    Add-Failure "Arquivo obrigatorio ausente: $Path"
  }
}

$rootPath = (Resolve-Path -LiteralPath $Root).Path
Push-Location $rootPath
try {
  Write-Host "SUPREME V4 - Phase 0 audit" -ForegroundColor Cyan

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
    "docs/ENVIRONMENT_PROFILES.md",
    "docs/PHASE_ZERO_RELEASE.md",
    "scripts/release_phase_zero_check.ps1"
  )) {
    Test-FilePresent -Path $path
  }

  $criticalFiles = @(
    ".env.production.example",
    "supreme-backend/.env.production.example",
    "sentinela/.env.production.example",
    ".gitignore",
    "README.md",
    "README_INSTALACAO.md",
    "LEIA_PRIMEIRO_HANDOFF_FINAL_DEV.md",
    "docs/ENVIRONMENT_PROFILES.md",
    "docs/PHASE_ZERO_RELEASE.md",
    "scripts/release_phase_zero_check.ps1"
  )

  $mojibakePattern = ([char]0x00C3) + "|" + ([char]0x00C2) + "|" + ([char]0x00E2) + "|" + ([char]0xFFFD)
  foreach ($file in $criticalFiles) {
    if (-not (Test-Path -LiteralPath $file)) {
      continue
    }
    $content = Get-Content -LiteralPath $file -Raw
    if ($content -match $mojibakePattern) {
      Add-Failure "Mojibake em arquivo critico: $file"
    }
  }

  $versionDriftPattern = ("SUPREME V" + "5") + "|" + ("SUPREME_" + "V5") + "|" + ("V4" + "/" + "V5")
  $scanFiles = Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
      $_.FullName -notmatch "\\IPED-local\\" -and
      $_.FullName -notmatch "\\__pycache__\\" -and
      $_.Extension -notin @(".exe", ".dll", ".jar", ".db", ".png", ".jpg", ".jpeg", ".mp4", ".zip")
    }
  foreach ($file in $scanFiles) {
    $relative = $file.FullName.Substring($rootPath.Length + 1)
    if ($relative -in @("scripts\release_phase_zero_check.ps1", "docs\PHASE_ZERO_RELEASE.md", "scripts\phase_zero_audit.ps1")) {
      continue
    }
    $content = Get-Content -LiteralPath $file.FullName -Raw -ErrorAction SilentlyContinue
    if ($content -match $versionDriftPattern) {
      Add-Failure "Identidade de versao inconsistente em: $relative"
    }
  }

  & powershell -ExecutionPolicy Bypass -File ".\scripts\release_phase_zero_check.ps1" -Root $rootPath
  if ($LASTEXITCODE -ne 0) {
    Add-Failure "release_phase_zero_check.ps1 falhou"
  }

  Write-Host ""
  Write-Host "Resumo Fase 0: $($Failures.Count) falha(s), $($Warnings.Count) aviso(s)." -ForegroundColor Cyan
  if ($Failures.Count -gt 0) {
    exit 1
  }
  exit 0
}
finally {
  Pop-Location
}
