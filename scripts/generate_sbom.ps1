param(
  [string]$Root = ".",
  [string]$ReportPath = "reports/security/sbom.cyclonedx.json"
)

$ErrorActionPreference = "Stop"
$rootPath = (Resolve-Path -LiteralPath $Root).Path
$reportFullPath = Join-Path $rootPath $ReportPath
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $reportFullPath) | Out-Null
$components = New-Object System.Collections.Generic.List[object]

function Add-Component {
  param([string]$Name, [string]$Version, [string]$Source)
  $components.Add([pscustomobject]@{
    type = "library"
    name = $Name
    version = $Version
    purl = "pkg:pypi/$($Name.ToLowerInvariant())@$Version"
    properties = @(@{ name = "source"; value = $Source })
  }) | Out-Null
}

$requirements = Join-Path $rootPath "sentinela/requirements.txt"
if (Test-Path -LiteralPath $requirements) {
  Get-Content -LiteralPath $requirements | ForEach-Object {
    $line = $_.Trim()
    if ($line -match "^([A-Za-z0-9_.\-\[\]]+)==([^ ;#]+)") {
      Add-Component -Name $matches[1] -Version $matches[2] -Source "sentinela/requirements.txt"
    }
  }
}

$sbom = [pscustomobject]@{
  bomFormat = "CycloneDX"
  specVersion = "1.5"
  version = 1
  metadata = @{ component = @{ type = "application"; name = "SUPREME V4"; version = "4.0.0" } }
  components = $components
}
$sbom | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 -LiteralPath $reportFullPath
Write-Host "SBOM generated: $ReportPath ($($components.Count) component(s))"
