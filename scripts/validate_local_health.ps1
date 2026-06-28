param(
    [int]$TimeoutSeconds = 180,
    [string]$PythonExe = $env:PYTHON_EXE
)

$ErrorActionPreference = "Stop"

$ComposeProjectName = if ($env:COMPOSE_PROJECT_NAME) { $env:COMPOSE_PROJECT_NAME } else { "supreme-v4-test-clone" }

$Compose = @(
    "compose",
    "-p", $ComposeProjectName,
    "-f", "docker-compose.production.yml",
    "-f", "docker-compose.local.yml"
)

[System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }

function Read-EnvValue {
    param([string]$Path, [string]$Key)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    $line = Get-Content -LiteralPath $Path | Where-Object { $_ -match "^$Key=" } | Select-Object -First 1
    if ($line) { return ($line -split "=", 2)[1].Trim() }
    return $null
}

function Wait-Until {
    param(
        [scriptblock]$Check,
        [string]$Label
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $last = $null
    while ((Get-Date) -lt $deadline) {
        try {
            $last = & $Check
            if ($last) {
                Write-Host "OK $Label"
                return
            }
        } catch {
            $last = $_.Exception.Message
        }
        Start-Sleep -Seconds 3
    }
    throw "Timeout waiting for $Label. Last result: $last"
}

function Test-Http {
    param([string]$Url)
    $response = Invoke-WebRequest -UseBasicParsing -TimeoutSec 10 -Uri $Url
    return ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500)
}

function Resolve-Python {
    function Test-PythonCandidate {
        param([string]$Exe, [string[]]$Prefix = @())
        try {
            & $Exe @Prefix -c "import sys; raise SystemExit(0 if sys.version_info.major == 3 else 1)" 2>$null
            return ($LASTEXITCODE -eq 0)
        } catch {
            return $false
        }
    }
    if ($PythonExe) {
        if (-not (Test-PythonCandidate -Exe $PythonExe)) {
            throw "PYTHON_EXE definido, mas nao executa Python 3 valido: $PythonExe"
        }
        return @{ Exe = $PythonExe; Prefix = @() }
    }
    if ((Get-Command python -ErrorAction SilentlyContinue) -and (Test-PythonCandidate -Exe "python")) {
        return @{ Exe = "python"; Prefix = @() }
    }
    if ((Get-Command py -ErrorAction SilentlyContinue) -and (Test-PythonCandidate -Exe "py" -Prefix @("-3"))) {
        return @{ Exe = "py"; Prefix = @("-3") }
    }
    throw "Python 3 nao encontrado. Defina PYTHON_EXE para validar HTTPS local."
}

function Test-HttpsWithPython {
    param([string]$Url)
    $py = Resolve-Python
    $code = @"
import ssl
import sys
import urllib.request

url = sys.argv[1]
ctx = ssl._create_unverified_context()
with urllib.request.urlopen(url, context=ctx, timeout=10) as response:
    if response.status < 200 or response.status >= 500:
        raise SystemExit(response.status)
"@
    & $py.Exe @($py.Prefix) -c $code $Url
    return ($LASTEXITCODE -eq 0)
}

$redisPassword = Read-EnvValue ".env" "REDIS_PASSWORD"
if (-not $redisPassword) {
    throw "REDIS_PASSWORD not found in .env. Run scripts\setup_env_local.ps1 first."
}

Write-Host "Validating local healthchecks..."

Wait-Until -Label "SUPREME API direct /health" -Check {
    Test-Http "http://localhost:18000/health"
}

Wait-Until -Label "SENTINELA direct /health" -Check {
    Test-Http "http://localhost:18001/health"
}

Wait-Until -Label "NGINX HTTPS /health" -Check {
    Test-HttpsWithPython "https://localhost/health"
}

Wait-Until -Label "SUPREME Postgres" -Check {
    $out = docker @Compose exec -T supreme-db pg_isready -U supreme -d supreme
    return ($LASTEXITCODE -eq 0 -and ($out -join "`n") -match "accepting connections")
}

Wait-Until -Label "SENTINELA Postgres" -Check {
    $out = docker @Compose exec -T sentinela-db pg_isready -U sentinela -d sentinela
    return ($LASTEXITCODE -eq 0 -and ($out -join "`n") -match "accepting connections")
}

Wait-Until -Label "Redis" -Check {
    $out = docker @Compose exec -T supreme-redis redis-cli --no-auth-warning -a $redisPassword ping
    return ($LASTEXITCODE -eq 0 -and (($out -join "`n") -match "PONG"))
}

Write-Host "OK all local healthchecks passed."
