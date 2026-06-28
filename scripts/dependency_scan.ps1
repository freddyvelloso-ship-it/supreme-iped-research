param(
  [string]$Root = ".",
  [string]$ReportPath = "reports/security/dependency_scan.json"
)

$ErrorActionPreference = "Stop"
$rootPath = (Resolve-Path -LiteralPath $Root).Path
$reportFullPath = Join-Path $rootPath $ReportPath
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $reportFullPath) | Out-Null

$knownCritical = @{
  "python-multipart" = @{ max_safe_exclusive = [version]"0.0.7"; cve = "CVE-2024-24762 baseline" }
  "bcrypt" = @{ max_safe_exclusive = [version]"3.2.0"; cve = "legacy bcrypt baseline" }
}
$findings = New-Object System.Collections.Generic.List[object]

function Test-RequirementLine {
  param([string]$Line, [string]$Source)
  $trimmed = $Line.Trim()
  if ($trimmed.Length -eq 0 -or $trimmed.StartsWith("#") -or $trimmed -notmatch "==") { return }
  $parts = $trimmed -split "==", 2
  $name = $parts[0].Trim().ToLowerInvariant()
  $versionText = ($parts[1] -split "[ ;#]", 2)[0]
  if (-not $knownCritical.ContainsKey($name)) { return }
  $version = [version]$versionText
  if ($version -lt $knownCritical[$name].max_safe_exclusive) {
    $findings.Add([pscustomobject]@{
      severity = "critical"
      package = $name
      version = $versionText
      source = $Source
      note = $knownCritical[$name].cve
    }) | Out-Null
  }
}

foreach ($file in @("sentinela/requirements.txt")) {
  $path = Join-Path $rootPath $file
  if (Test-Path -LiteralPath $path) {
    Get-Content -LiteralPath $path | ForEach-Object { Test-RequirementLine -Line $_ -Source $file }
  }
}

$report = [pscustomobject]@{
  status = $(if ($findings.Count -eq 0) { "pass" } else { "fail" })
  critical_findings = $findings.Count
  scanner = "offline-critical-baseline"
  findings = $findings
}
$report | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 -LiteralPath $reportFullPath
Write-Host "Dependency scan: $($findings.Count) critical finding(s). Report: $ReportPath"
if ($findings.Count -gt 0) { exit 1 }
