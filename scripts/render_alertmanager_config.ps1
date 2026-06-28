param(
    [string]$EnvFile = ".env",
    [string]$Output = ".\infra\alertmanager\alertmanager.yml"
)

$ErrorActionPreference = "Stop"

function Get-EnvVal {
    param([string]$Path, [string]$Key, [string]$Default = "")
    if (-not (Test-Path -LiteralPath $Path)) { return $Default }
    $line = Get-Content -LiteralPath $Path | Where-Object { $_ -match "^${Key}=" } | Select-Object -First 1
    if (-not $line) { return $Default }
    return ($line -split "=", 2)[1]
}

function ConvertTo-YamlScalar {
    param([string]$Value)
    return '"' + (($Value -replace '\\', '\\') -replace '"', '\"') + '"'
}

$smtpHost = Get-EnvVal $EnvFile "ALERTMANAGER_SMTP_HOST" "mailpit:1025"
$smtpFrom = Get-EnvVal $EnvFile "ALERTMANAGER_SMTP_FROM" "SUPREME Alertas <alerts@localhost>"
$emailTo = Get-EnvVal $EnvFile "ALERTMANAGER_EMAIL_TO" "alerts@localhost"
$smtpUser = Get-EnvVal $EnvFile "ALERTMANAGER_SMTP_USERNAME" ""
$smtpPassword = Get-EnvVal $EnvFile "ALERTMANAGER_SMTP_PASSWORD" ""
$smtpRequireTls = (Get-EnvVal $EnvFile "ALERTMANAGER_SMTP_REQUIRE_TLS" "false").ToLowerInvariant()

if ($smtpRequireTls -notin @("true", "false")) {
    throw "ALERTMANAGER_SMTP_REQUIRE_TLS deve ser true ou false."
}

$authLines = ""
if ($smtpUser -and $smtpPassword) {
    $authLines = @"
        auth_username: $(ConvertTo-YamlScalar $smtpUser)
        auth_password: $(ConvertTo-YamlScalar $smtpPassword)
"@
}

$config = @"
global:
  resolve_timeout: 5m
  smtp_smarthost: $(ConvertTo-YamlScalar $smtpHost)
  smtp_from: $(ConvertTo-YamlScalar $smtpFrom)
  smtp_require_tls: $smtpRequireTls

route:
  receiver: supreme-email
  group_by: ["alertname", "severity"]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - match:
        severity: critical
      receiver: supreme-email
      repeat_interval: 30m
    - match:
        severity: warning
      receiver: supreme-email
      repeat_interval: 2h

receivers:
  - name: supreme-email
    email_configs:
      - to: $(ConvertTo-YamlScalar $emailTo)
        send_resolved: true
$authLines
inhibit_rules:
  - source_match:
      alertname: APIIndisponivel
    target_match_re:
      alertname: "AltaTaxaErros5xx|LatenciaAltaP95"
    equal: ["job"]

  - source_match:
      alertname: PostgreSQLIndisponivel
    target_match_re:
      alertname: "ConexoesPostgreSQLAltas|PostgreSQLTransacoesLentas|PostgreSQLDeadlocks"
    equal: ["job"]

  - source_match:
      alertname: RedisIndisponivel
    target_match:
      alertname: PipelineParado
"@

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Output) | Out-Null
Set-Content -Encoding ASCII -LiteralPath $Output -Value $config
Write-Host "Alertmanager config renderizada em $Output"
