param(
  [string]$Root = ".",
  [string]$ReportPath = "reports/security/secret_scan.json"
)

$ErrorActionPreference = "Stop"
$findings = New-Object System.Collections.Generic.List[object]
$rootPath = (Resolve-Path -LiteralPath $Root).Path
$reportFullPath = Join-Path $rootPath $ReportPath
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $reportFullPath) | Out-Null

$excludedDirs = @("\.git\", "\.local\", "\__pycache__\", "\.pytest_cache\", "\reports\security\")
$excludedFiles = @(".env", ".env.production", ".env.local", ".env.production.example", ".env.example")
$patterns = @(
  @{ Name = "private_key"; Regex = "-----BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY-----" },
  @{ Name = "hardcoded_jwt"; Regex = "eyJ[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}" },
  @{ Name = "aws_access_key"; Regex = "AKIA[0-9A-Z]{16}" },
  @{ Name = "hex_secret_assignment"; Regex = "(?i)(SECRET|TOKEN|PASSWORD|SALT|API_KEY)\s*=\s*[a-f0-9]{32,}" }
)

$scanRoots = @(
  ".github",
  "docs",
  "infra",
  "scripts",
  "sentinela",
  "supreme-backend",
  "supreme-iped-integration",
  "seeds"
)

foreach ($scanRoot in $scanRoots) {
  $scanPath = Join-Path $rootPath $scanRoot
  if (-not (Test-Path -LiteralPath $scanPath)) { continue }
  Get-ChildItem -LiteralPath $scanPath -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
    $fullName = $_.FullName
    $relative = $fullName.Substring($rootPath.Length).TrimStart("\", "/")
    foreach ($dir in $excludedDirs) {
      if ($fullName.Contains($dir)) { return }
    }
    if ($excludedFiles -contains $_.Name -or $relative -match "(^|[\\/])\.env(\.|$)") { return }
    if ($_.Extension -match "\.(png|jpg|jpeg|gif|mp4|zip|pdf|pyc)$") { return }
    $text = Get-Content -LiteralPath $fullName -Raw -ErrorAction SilentlyContinue
    foreach ($pattern in $patterns) {
      if ($text -match $pattern.Regex) {
        $findings.Add([pscustomobject]@{
          severity = "critical"
          rule = $pattern.Name
          file = $relative
        }) | Out-Null
      }
    }
  }
}

$report = [pscustomobject]@{
  status = $(if ($findings.Count -eq 0) { "pass" } else { "fail" })
  critical_findings = $findings.Count
  findings = $findings
}
$json = $report | ConvertTo-Json -Depth 5
[System.IO.File]::WriteAllText($reportFullPath, $json, [System.Text.UTF8Encoding]::new($false))
Write-Host "Secret scan: $($findings.Count) critical finding(s). Report: $ReportPath"
if ($findings.Count -gt 0) { exit 1 }
