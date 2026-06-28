param(
    [ValidateSet("setup", "up", "reset", "health", "seed-clean", "seed-demo", "test", "simulate", "all", "down", "status")]
    [string]$Action = "all",

    [switch]$RegenerateSecrets,

    [string]$PythonExe = $env:PYTHON_EXE,

    [int]$TimeoutSeconds = 180
)

$ErrorActionPreference = "Stop"

$ComposeProjectName = if ($env:COMPOSE_PROJECT_NAME) { $env:COMPOSE_PROJECT_NAME } else { "supreme-v4-test-clone" }

$Compose = @(
    "compose",
    "-p", $ComposeProjectName,
    "-f", "docker-compose.production.yml",
    "-f", "docker-compose.local.yml"
)

function Invoke-LocalSetup {
    if ($RegenerateSecrets -or -not (Test-Path -LiteralPath ".env") -or
        -not (Test-Path -LiteralPath "supreme-backend\.env.production") -or
        -not (Test-Path -LiteralPath "sentinela\.env.production")) {
        & ".\scripts\setup_env_local.ps1"
    } else {
        Write-Host "Local env files already exist. Use -RegenerateSecrets to replace them."
    }

    New-Item -ItemType Directory -Force ".\tmp\iped-audit" | Out-Null

    if (-not (Test-Path -LiteralPath ".\certs\fullchain.pem") -or
        -not (Test-Path -LiteralPath ".\certs\privkey.pem")) {
        & ".\scripts\gerar_cert_local.ps1"
    } else {
        Write-Host "Local TLS certificate already exists."
    }

    docker @Compose config | Out-Null
    Write-Host "Compose config OK."
}

function Invoke-ComposeUp {
    docker @Compose up -d --build
}

function Invoke-ComposeDown {
    docker @Compose down --remove-orphans
}

function Invoke-ComposeReset {
    docker @Compose down -v --remove-orphans
}

switch ($Action) {
    "setup" {
        Invoke-LocalSetup
    }
    "up" {
        Invoke-LocalSetup
        Invoke-ComposeUp
        & ".\scripts\validate_local_health.ps1" -TimeoutSeconds $TimeoutSeconds -PythonExe $PythonExe
    }
    "reset" {
        Invoke-LocalSetup
        Invoke-ComposeReset
        Invoke-ComposeUp
        & ".\scripts\validate_local_health.ps1" -TimeoutSeconds $TimeoutSeconds -PythonExe $PythonExe
        & ".\scripts\apply_local_seed.ps1" -Mode clean
    }
    "health" {
        & ".\scripts\validate_local_health.ps1" -TimeoutSeconds $TimeoutSeconds -PythonExe $PythonExe
    }
    "seed-clean" {
        & ".\scripts\apply_local_seed.ps1" -Mode clean
    }
    "seed-demo" {
        & ".\scripts\apply_local_seed.ps1" -Mode demo
    }
    "test" {
        & ".\scripts\validate_local_health.ps1" -TimeoutSeconds $TimeoutSeconds -PythonExe $PythonExe
        & ".\scripts\local_e2e_iped_to_sentinela.ps1" -TimeoutSeconds $TimeoutSeconds -PythonExe $PythonExe
    }
    "simulate" {
        & ".\scripts\local_e2e_iped_to_sentinela.ps1" -TimeoutSeconds $TimeoutSeconds -PythonExe $PythonExe
    }
    "all" {
        Invoke-LocalSetup
        Invoke-ComposeReset
        Invoke-ComposeUp
        & ".\scripts\validate_local_health.ps1" -TimeoutSeconds $TimeoutSeconds -PythonExe $PythonExe
        & ".\scripts\apply_local_seed.ps1" -Mode clean
        & ".\scripts\local_e2e_iped_to_sentinela.ps1" -TimeoutSeconds $TimeoutSeconds -PythonExe $PythonExe
    }
    "down" {
        Invoke-ComposeDown
    }
    "status" {
        docker @Compose ps
    }
}
