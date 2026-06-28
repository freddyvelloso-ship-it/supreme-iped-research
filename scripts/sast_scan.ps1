param(
  [string]$Root = ".",
  [string]$ReportPath = "reports/security/sast_scan.json"
)

$ErrorActionPreference = "Stop"
$rootPath = (Resolve-Path -LiteralPath $Root).Path
$reportFullPath = Join-Path $rootPath $ReportPath
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $reportFullPath) | Out-Null
$findings = New-Object System.Collections.Generic.List[object]

$rules = @(
  @{ Id = "python-eval"; Regex = "\beval\s*\("; Severity = "critical" },
  @{ Id = "python-exec"; Regex = "\bexec\s*\("; Severity = "critical" },
  @{ Id = "shell-true"; Regex = "shell\s*=\s*True"; Severity = "critical" },
  @{ Id = "pickle-loads"; Regex = "pickle\.(loads|load)\s*\("; Severity = "critical" },
  @{ Id = "url-token"; Regex = "[?&](token|ticket|api_key|api-key)="; Severity = "critical" }
)

foreach ($dir in @("sentinela/src", "sentinela/static", "supreme-backend/src", "scripts")) {
  $path = Join-Path $rootPath $dir
  if (-not (Test-Path -LiteralPath $path)) { continue }
  Get-ChildItem -LiteralPath $path -Recurse -File | Where-Object {
    $_.Extension -in @(".py", ".ps1", ".html", ".js", ".ts", ".tsx")
  } | ForEach-Object {
    $relative = $_.FullName.Substring($rootPath.Length).TrimStart("\", "/")
    if ($relative -in @("scripts\sast_scan.ps1", "scripts\phase2_security_check.ps1")) { return }
    $text = Get-Content -LiteralPath $_.FullName -Raw
    foreach ($rule in $rules) {
      if ($text -match $rule.Regex) {
        $findings.Add([pscustomobject]@{
          severity = $rule.Severity
          rule = $rule.Id
          file = $relative
        }) | Out-Null
      }
    }
  }
}

$report = [pscustomobject]@{
  status = $(if ($findings.Count -eq 0) { "pass" } else { "fail" })
  critical_findings = $findings.Count
  scanner = "offline-sast-baseline"
  findings = $findings
}
$report | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 -LiteralPath $reportFullPath
Write-Host "SAST scan: $($findings.Count) critical finding(s). Report: $ReportPath"
if ($findings.Count -gt 0) { exit 1 }
