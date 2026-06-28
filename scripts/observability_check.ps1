param(
  [string]$PrometheusUrl = $(if ($env:PROMETHEUS_URL) { $env:PROMETHEUS_URL } else { "http://localhost:9190" }),
  [string]$LokiUrl = $(if ($env:LOKI_URL) { $env:LOKI_URL } else { "http://localhost:3111" }),
  [string]$GrafanaUrl = $(if ($env:GRAFANA_URL) { $env:GRAFANA_URL } else { "http://localhost:3300" })
)

$ErrorActionPreference = "Stop"

function Invoke-Text {
  param([string]$Url)
  try {
    return (Invoke-WebRequest -UseBasicParsing -TimeoutSec 10 -Uri $Url).Content
  } catch {
    throw "Falha ao acessar $Url`: $($_.Exception.Message)"
  }
}

Invoke-Text "$PrometheusUrl/-/ready" | Out-Null
$targets = Invoke-Text "$PrometheusUrl/api/v1/targets?state=active" | ConvertFrom-Json
$requiredJobs = @("supreme-api", "postgres-exporter", "redis-exporter")
foreach ($job in $requiredJobs) {
  $up = @($targets.data.activeTargets | Where-Object { $_.labels.job -eq $job -and $_.health -eq "up" })
  if ($up.Count -lt 1) {
    throw "Prometheus sem target UP para job=$job"
  }
}

$lokiReady = Invoke-Text "$LokiUrl/ready"
if ($lokiReady -notmatch "ready") {
  throw "Loki nao respondeu ready."
}

$grafanaHealth = Invoke-Text "$GrafanaUrl/api/health" | ConvertFrom-Json
if ($grafanaHealth.database -ne "ok") {
  throw "Grafana database health nao esta ok."
}

Write-Host "OK observabilidade validada."
