param(
    [ValidateSet("clean", "demo")]
    [string]$Mode = "clean"
)

$ErrorActionPreference = "Stop"

$ComposeProjectName = if ($env:COMPOSE_PROJECT_NAME) { $env:COMPOSE_PROJECT_NAME } else { "supreme-v4-test-clone" }

$Compose = @(
    "compose",
    "-p", $ComposeProjectName,
    "-f", "docker-compose.production.yml",
    "-f", "docker-compose.local.yml"
)

function Invoke-SeedSql {
    param(
        [string]$Service,
        [string]$User,
        [string]$Database,
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Seed file not found: $Path"
    }

    Write-Host "Applying $Path to $Service/$Database..."
    $sql = Get-Content -LiteralPath $Path -Raw
    $sql | docker @Compose exec -T $Service psql -U $User -d $Database -v ON_ERROR_STOP=1
}

Invoke-SeedSql -Service "supreme-db" -User "supreme" -Database "supreme" -Path "seeds\local\clean\supreme.sql"
Invoke-SeedSql -Service "sentinela-db" -User "sentinela" -Database "sentinela" -Path "seeds\local\clean\sentinela.sql"

if ($Mode -eq "demo") {
    Invoke-SeedSql -Service "supreme-db" -User "supreme" -Database "supreme" -Path "seeds\local\demo\supreme.sql"
    Invoke-SeedSql -Service "sentinela-db" -User "sentinela" -Database "sentinela" -Path "seeds\local\demo\sentinela.sql"
}

Write-Host "Local seed '$Mode' applied."
