param(
    [string]$BaseUrl = $(if ($env:BASE_URL) { $env:BASE_URL } else { "https://localhost" }),
    [string]$PrometheusUrl = $(if ($env:PROMETHEUS_URL) { $env:PROMETHEUS_URL } else { "http://localhost:9090" }),
    [string]$ApiSecretKey = $env:API_SECRET_KEY,
    [string]$PythonExe = $env:PYTHON_EXE
)

$ErrorActionPreference = "Stop"

function Get-EnvVal {
    param([string]$Path, [string]$Key)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    $line = Get-Content -LiteralPath $Path | Where-Object { $_ -match "^${Key}=" } | Select-Object -First 1
    if ($line) { return ($line -split "=", 2)[1] }
    return $null
}

if (-not $ApiSecretKey) {
    $ApiSecretKey = Get-EnvVal ".\supreme-backend\.env.production" "API_SECRET_KEY"
}
if (-not $ApiSecretKey) {
    throw "API_SECRET_KEY nao informado e nao encontrado em supreme-backend\.env.production."
}

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }

function Invoke-HttpText {
    param(
        [string]$Url,
        [hashtable]$Headers = @{}
    )
    try {
        $response = Invoke-WebRequest -UseBasicParsing -TimeoutSec 10 -Uri $Url -Headers $Headers
        return $response.Content
    } catch {
        if (-not $PythonExe) {
            throw "Falha ao acessar $Url`: $($_.Exception.Message). Se for TLS local no Windows, informe -PythonExe ou PYTHON_EXE."
        }
        return Invoke-PythonHttpText -Url $Url -Headers $Headers
    }
}

function Invoke-PythonHttpText {
    param(
        [string]$Url,
        [hashtable]$Headers = @{}
    )
    $headersJson = $Headers | ConvertTo-Json -Compress
    if (-not $headersJson) { $headersJson = "{}" }
    $headersEncoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($headersJson))
    $tmp = New-TemporaryFile
    try {
        @'
import json
import base64
import ssl
import sys
import urllib.request

url = sys.argv[1]
headers = json.loads(base64.b64decode(sys.argv[2]).decode("utf-8"))
request = urllib.request.Request(url, headers=headers)
context = ssl._create_unverified_context()
with urllib.request.urlopen(request, context=context, timeout=10) as response:
    sys.stdout.buffer.write(response.read())
'@ | Set-Content -Encoding ASCII -LiteralPath $tmp
        $previousErrorActionPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        $output = & $PythonExe $tmp $Url $headersEncoded 2>&1
        $ErrorActionPreference = $previousErrorActionPreference
        if ($LASTEXITCODE -ne 0) {
            throw "Falha ao acessar $Url via Python: $output"
        }
        return ($output -join "`n")
    } finally {
        Remove-Item -LiteralPath $tmp -ErrorAction SilentlyContinue
    }
}

Write-Host "Smoke SUPREME em $BaseUrl"

Invoke-HttpText "$BaseUrl/" | Out-Null
Invoke-HttpText "$BaseUrl/health" | Out-Null
Invoke-HttpText "$BaseUrl/v1/health" -Headers @{ Authorization = "Bearer $ApiSecretKey" } | Out-Null
Invoke-HttpText "$PrometheusUrl/-/ready" | Out-Null

$targetsJson = Invoke-HttpText "$PrometheusUrl/api/v1/targets?state=active"
$targets = $targetsJson | ConvertFrom-Json
$supremeTarget = @($targets.data.activeTargets | Where-Object {
    $_.labels.job -eq "supreme-api" -and $_.health -eq "up"
})
if ($supremeTarget.Count -lt 1) {
    throw "Prometheus nao tem target supreme-api UP."
}

Write-Host "OK smoke test concluido."
