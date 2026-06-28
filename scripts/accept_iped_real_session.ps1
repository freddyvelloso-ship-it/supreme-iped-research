param(
  [string]$AuditLog = "",
  [string]$IpedHome = $env:IPED_HOME,
  [string]$CasePath = "",
  [string]$Launcher = ".\LAUNCHER_IPED.ps1",
  [string]$UserId = "phase5-real-acceptance-operator",
  [int]$TimeoutSeconds = 180,
  [switch]$SkipLaunch,
  [switch]$SkipForms,
  [switch]$SkipDatabaseCheck,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"
if (Get-Variable PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
  $PSNativeCommandUseErrorActionPreference = $false
}

function Fail {
  param([string]$Message)
  Write-Host "[FAIL] $Message" -ForegroundColor Red
  exit 1
}

function Pass {
  param([string]$Message)
  Write-Host "[ OK ] $Message" -ForegroundColor Green
}

function Get-LineCount {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) {
    return 0
  }
  return (Get-Content -LiteralPath $Path | Measure-Object -Line).Lines
}

function Read-NewEntries {
  param([string]$Path, [int]$SkipLines)
  if (-not (Test-Path -LiteralPath $Path)) {
    return @()
  }
  $entries = @()
  $lines = Get-Content -LiteralPath $Path | Select-Object -Skip $SkipLines
  foreach ($line in $lines) {
    if ([string]::IsNullOrWhiteSpace($line)) {
      continue
    }
    try {
      $entries += ($line | ConvertFrom-Json)
    } catch {
      Fail "Linha nova invalida em ${Path}: $line"
    }
  }
  return $entries
}

function Read-DotEnv {
  param([string]$Path)
  $values = @{}
  if (-not (Test-Path -LiteralPath $Path)) {
    return $values
  }
  foreach ($line in Get-Content -LiteralPath $Path) {
    $trimmed = $line.Trim()
    if ($trimmed.Length -eq 0 -or $trimmed.StartsWith("#")) {
      continue
    }
    $parts = $trimmed -split "=", 2
    if ($parts.Count -eq 2) {
      $values[$parts[0].Trim()] = $parts[1].Trim().Trim('"').Trim("'")
    }
  }
  return $values
}

function Resolve-AuditLog {
  param([string]$Explicit)
  if (-not [string]::IsNullOrWhiteSpace($Explicit)) {
    return $Explicit
  }
  $rootEnv = Read-DotEnv -Path ".env"
  $configuredAuditDir = $rootEnv["IPED_AUDIT_DIR"]
  if ($configuredAuditDir) {
    if (-not [System.IO.Path]::IsPathRooted($configuredAuditDir)) {
      $configuredAuditDir = Join-Path (Get-Location).Path $configuredAuditDir
    }
    New-Item -ItemType Directory -Force -Path $configuredAuditDir | Out-Null
    return (Join-Path $configuredAuditDir "supreme_audit.ndjson")
  }
  return "$env:USERPROFILE\supreme_audit.ndjson"
}

function Invoke-PsqlScalar {
  param([string]$Sql)
  $out = & docker compose -f docker-compose.production.yml -f docker-compose.local.yml exec -T supreme-db psql -U supreme -d supreme -tAc $Sql 2>&1
  if ($LASTEXITCODE -ne 0) {
    throw "psql falhou: $out"
  }
  return (($out | Out-String).Trim())
}

function Wait-ForDbEvents {
  param([string]$StartedUtc, [int]$Timeout)
  $deadline = (Get-Date).AddSeconds($Timeout)
  $sql = "SELECT COUNT(*) FROM events_raw WHERE source_tool='iped' AND timestamp >= '$StartedUtc'::timestamptz;"
  $last = "0"
  while ((Get-Date) -lt $deadline) {
    $last = Invoke-PsqlScalar -Sql $sql
    if ([int]$last -gt 0) {
      return [int]$last
    }
    Start-Sleep -Seconds 5
  }
  Fail "Nenhum evento IPED real chegou em events_raw depois de $StartedUtc. Ultimo count=$last"
}

Write-Host "SUPREME V4 - aceite assistido com IPED real" -ForegroundColor Cyan
Write-Host "Criterio: IPED real precisa gerar NDJSON real e o watcher precisa gravar no banco." -ForegroundColor DarkGray
Write-Host ""

$AuditLog = Resolve-AuditLog -Explicit $AuditLog

if ($DryRun) {
  & ".\scripts\verify_iped_real_environment.ps1" -ReportOnly
  Pass "DryRun concluido: verificador executado; launcher e banco nao foram acionados."
  exit 0
}

& ".\scripts\verify_iped_real_environment.ps1" -IpedHome $IpedHome
if ($LASTEXITCODE -ne 0) {
  Fail "Ambiente IPED real reprovado antes do aceite."
}

$env:IPED_HOME = $IpedHome

$startedUtc = [DateTimeOffset]::UtcNow.ToString("o")
$before = Get-LineCount -Path $AuditLog
Write-Host "Linhas antes da sessao: $before"

if (-not $SkipLaunch) {
  if (-not (Test-Path -LiteralPath $Launcher)) {
    Fail "Launcher nao encontrado: $Launcher"
  }
  Write-Host "Abrindo launcher IPED real. Interaja com o IPED, abra itens reais e feche o IPED para continuar." -ForegroundColor Yellow
  & $Launcher -UserId $UserId -CasePath $CasePath -SkipForms:$SkipForms
  if ($LASTEXITCODE -ne 0) {
    Fail "Launcher IPED retornou codigo $LASTEXITCODE."
  }
} else {
  Write-Host "Modo SkipLaunch: aguardando linhas novas no log ja existente." -ForegroundColor Yellow
  Start-Sleep -Seconds 5
}

$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
$after = Get-LineCount -Path $AuditLog
while ($after -le $before -and (Get-Date) -lt $deadline) {
  Start-Sleep -Seconds 5
  $after = Get-LineCount -Path $AuditLog
}

if ($after -le $before) {
  Fail "IPED real nao gerou novas linhas em $AuditLog durante a janela de aceite."
}
Pass "IPED real gerou $($after - $before) linha(s) nova(s) em supreme_audit.ndjson"

$entries = Read-NewEntries -Path $AuditLog -SkipLines $before
$closedEntries = @($entries | Where-Object { $_.event -in @("close", "classification_event") })
if ($closedEntries.Count -eq 0) {
  Fail "Nenhuma linha nova processavel pelo watcher. Esperado event=close ou classification_event."
}

$first = $closedEntries[0]
foreach ($field in @("event", "itemId", "mediaType", "openTs", "closeTs", "userId")) {
  if ($null -eq $first.$field -or [string]::IsNullOrWhiteSpace([string]$first.$field)) {
    Fail "Linha processavel sem campo obrigatorio do patch: $field"
  }
}
Pass "NDJSON real contem campos do patch Java: event, itemId, mediaType, openTs, closeTs, userId"

if (-not $SkipDatabaseCheck) {
  $count = Wait-ForDbEvents -StartedUtc $startedUtc -Timeout $TimeoutSeconds
  Pass "Banco recebeu $count evento(s) IPED real(is) em events_raw"
} else {
  Write-Host "[WARN] Verificacao de banco ignorada por -SkipDatabaseCheck." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "ACEITE IPED REAL: APROVADO" -ForegroundColor Green
exit 0
