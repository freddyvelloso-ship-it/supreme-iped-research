param(
  [string]$IpedHome = $env:IPED_HOME,
  [string]$AuditLog = "",
  [switch]$SkipDocker,
  [switch]$ReportOnly
)

$ErrorActionPreference = "Stop"
if (Get-Variable PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
  $PSNativeCommandUseErrorActionPreference = $false
}

$Failures = New-Object System.Collections.Generic.List[string]
$Warnings = New-Object System.Collections.Generic.List[string]

function Add-Check {
  param(
    [string]$Name,
    [bool]$Ok,
    [string]$Detail,
    [ValidateSet("Required", "Warning")] [string]$Severity = "Required"
  )
  if ($Ok) {
    Write-Host "[ OK ] $Name - $Detail" -ForegroundColor Green
    return
  }
  if ($Severity -eq "Warning") {
    $Warnings.Add("$Name - $Detail") | Out-Null
    Write-Host "[WARN] $Name - $Detail" -ForegroundColor Yellow
  } else {
    $Failures.Add("$Name - $Detail") | Out-Null
    Write-Host "[FAIL] $Name - $Detail" -ForegroundColor Red
  }
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
    return (Join-Path $configuredAuditDir "supreme_audit.ndjson")
  }
  return "$env:USERPROFILE\supreme_audit.ndjson"
}

function Find-IpedHome {
  param([string]$Preferred)
  $candidates = @()
  if (-not [string]::IsNullOrWhiteSpace($Preferred)) {
    $candidates += $Preferred
  }
  $candidates += @(
    "C:\iped-test-case",
    "C:\iped",
    "C:\IPED",
    "C:\iped-4.4",
    "C:\iped-4.3",
    "C:\iped-4.2",
    "C:\iped-4.1",
    "$env:ProgramFiles\IPED",
    "$env:LOCALAPPDATA\IPED",
    ".\IPED-local\iped"
  )

  foreach ($candidate in $candidates) {
    if ([string]::IsNullOrWhiteSpace($candidate) -or -not (Test-Path -LiteralPath $candidate)) {
      continue
    }
    $hasExe = (Test-Path -LiteralPath (Join-Path $candidate "IPED-SearchApp.exe")) -or (Test-Path -LiteralPath (Join-Path $candidate "bin\IPED-SearchApp.exe"))
    $hasJar = Test-Path -LiteralPath (Join-Path $candidate "iped.jar")
    $hasSearchJar = Test-Path -LiteralPath (Join-Path $candidate "iped-searchapp.jar")
    $hasLibSearchJar = Test-Path -LiteralPath (Join-Path $candidate "lib\iped-search-app.jar")
    $hasAppJar = @(Get-ChildItem -LiteralPath $candidate -Recurse -File -Filter "iped-app*.jar" -ErrorAction SilentlyContinue).Count -gt 0
    if ($hasExe -or $hasJar -or $hasSearchJar -or $hasLibSearchJar -or $hasAppJar) {
      return (Resolve-Path -LiteralPath $candidate).Path
    }
  }
  return $null
}

function Get-LineCount {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) {
    return 0
  }
  return (Get-Content -LiteralPath $Path | Measure-Object -Line).Lines
}

Write-Host "SUPREME V4 - verificacao de ambiente IPED real" -ForegroundColor Cyan
Write-Host "Este script nao homologa simulacao; ele procura IPED real, patch e log real." -ForegroundColor DarkGray
Write-Host ""

$AuditLog = Resolve-AuditLog -Explicit $AuditLog

$detectedIpedHome = Find-IpedHome -Preferred $IpedHome
Add-Check `
  -Name "IPED real detectado" `
  -Ok (-not [string]::IsNullOrWhiteSpace($detectedIpedHome)) `
  -Detail $(if ($detectedIpedHome) { $detectedIpedHome } else { "Defina IPED_HOME ou instale IPED em um caminho conhecido." })

if ($detectedIpedHome) {
  $ipedLauncher = $null
  foreach ($candidate in @(
      (Join-Path $detectedIpedHome "IPED-SearchApp.exe"),
      (Join-Path $detectedIpedHome "bin\IPED-SearchApp.exe"),
      (Join-Path $detectedIpedHome "iped-searchapp.jar"),
      (Join-Path $detectedIpedHome "lib\iped-search-app.jar"),
      (Join-Path $detectedIpedHome "iped.jar")
    )) {
    if (Test-Path -LiteralPath $candidate) {
      $ipedLauncher = $candidate
      break
    }
  }
  if (-not $ipedLauncher) {
    $jar = Get-ChildItem -LiteralPath $detectedIpedHome -Recurse -File -Filter "iped-app*.jar" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($jar) {
      $ipedLauncher = $jar.FullName
    }
  }
  $patchJar = Join-Path $detectedIpedHome "plugins\supreme-audit-patch.jar"
  $instrumentedBuild = $false
  foreach ($candidateJar in @(
      (Join-Path $detectedIpedHome "iped.jar"),
      (Join-Path $detectedIpedHome "lib\iped-search-app.jar")
    )) {
    if (Test-Path -LiteralPath $candidateJar) {
      $jarList = & jar tf $candidateJar 2>$null
      if (($jarList | Select-String -SimpleMatch "iped/app/ui/SupremeAuditLogger.class" -Quiet)) {
        $instrumentedBuild = $true
        break
      }
    }
  }
  Add-Check -Name "Launcher/JAR IPED encontrado" -Ok (-not [string]::IsNullOrWhiteSpace($ipedLauncher)) -Detail $(if ($ipedLauncher) { $ipedLauncher } else { "Nao achei executavel ou jar do IPED." })
  Add-Check -Name "Patch Java SUPREME instalado no IPED" -Ok ((Test-Path -LiteralPath $patchJar) -or $instrumentedBuild) -Detail $(if (Test-Path -LiteralPath $patchJar) { $patchJar } elseif ($instrumentedBuild) { "SupremeAuditLogger.class presente na build IPED instrumentada." } else { "Rode .\INSTALAR_PATCH_IPED.ps1 ou use build IPED instrumentada." })
}

$supremeEnvPath = "supreme-backend\.env.production"
$rootEnvPath = ".env"
$supremeEnv = Read-DotEnv -Path $supremeEnvPath
$rootEnv = Read-DotEnv -Path $rootEnvPath

Add-Check -Name "Arquivo SUPREME env" -Ok (Test-Path -LiteralPath $supremeEnvPath) -Detail $supremeEnvPath
foreach ($key in @("API_SECRET_KEY", "API_INGEST_TOKEN", "SUPREME_SALT")) {
  $present = $supremeEnv.ContainsKey($key) -and -not [string]::IsNullOrWhiteSpace($supremeEnv[$key])
  $strong = $present -and $supremeEnv[$key].Length -ge 32
  Add-Check -Name "Secret $key carregado" -Ok $strong -Detail $(if ($present) { "presente com tamanho minimo; valor nao exibido" } else { "ausente ou vazio em $supremeEnvPath" })
}

$configuredAuditDir = $rootEnv["IPED_AUDIT_DIR"]
if ($configuredAuditDir) {
  if (-not [System.IO.Path]::IsPathRooted($configuredAuditDir)) {
    $configuredAuditDir = Join-Path (Get-Location).Path $configuredAuditDir
  }
  $expectedLog = Join-Path $configuredAuditDir "supreme_audit.ndjson"
  Add-Check -Name "IPED_AUDIT_DIR aponta para arquivo esperado" -Ok ($expectedLog -eq $AuditLog) -Severity "Warning" -Detail "compose=$expectedLog; launcher=$AuditLog"
} else {
  Add-Check -Name "IPED_AUDIT_DIR configurado" -Ok $false -Severity "Warning" -Detail "Nao encontrado em .env; watcher local usara default do compose."
}

$auditExists = Test-Path -LiteralPath $AuditLog
$auditLines = Get-LineCount -Path $AuditLog
Add-Check -Name "Arquivo supreme_audit.ndjson" -Ok $auditExists -Severity "Warning" -Detail $(if ($auditExists) { "$AuditLog ($auditLines linha(s))" } else { "ainda nao existe; sera criado pelo IPED patched durante a sessao real" })

if ($auditExists -and $auditLines -gt 0) {
  $lastJsonOk = $false
  try {
    $last = Get-Content -LiteralPath $AuditLog -Tail 1 | ConvertFrom-Json
    $lastJsonOk = ($null -ne $last.event -and $null -ne $last.itemId -and $null -ne $last.openTs)
  } catch {
    $lastJsonOk = $false
  }
  Add-Check -Name "Ultima linha NDJSON tem formato do patch" -Ok $lastJsonOk -Severity "Warning" -Detail "campos esperados: event, itemId, openTs"
}

if (-not $SkipDocker) {
  if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Add-Check -Name "Docker disponivel" -Ok $false -Severity "Warning" -Detail "docker nao encontrado no PATH"
  } else {
    $composeOutput = & docker compose -f docker-compose.production.yml -f docker-compose.local.yml ps 2>&1
    $composeText = ($composeOutput | Out-String)
    Add-Check -Name "Docker compose responde" -Ok ($LASTEXITCODE -eq 0) -Detail "docker compose ps"
    Add-Check -Name "supreme-api em execucao" -Ok ($composeText -match "supreme-api" -and $composeText -match "Up") -Severity "Warning" -Detail "necessario para ingestao"
    Add-Check -Name "supreme-iped-watcher em execucao" -Ok ($composeText -match "supreme-iped-watcher" -and $composeText -match "Up") -Severity "Warning" -Detail "necessario para ler supreme_audit.ndjson"
    Add-Check -Name "supreme-iped-proxy em execucao" -Ok ($composeText -match "supreme-iped-proxy" -and $composeText -match "Up") -Severity "Warning" -Detail "necessario se usar IPED Web API via proxy"
  }
}

Write-Host ""
Write-Host "Resumo: $($Failures.Count) falha(s), $($Warnings.Count) aviso(s)." -ForegroundColor Cyan
if ($Failures.Count -gt 0 -and -not $ReportOnly) {
  exit 1
}
exit 0
