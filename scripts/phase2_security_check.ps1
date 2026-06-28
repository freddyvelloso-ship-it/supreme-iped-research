param(
  [string]$Root = "."
)

$ErrorActionPreference = "Stop"
$rootPath = (Resolve-Path -LiteralPath $Root).Path
$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure([string]$Message) {
  $failures.Add($Message) | Out-Null
  Write-Host "[FAIL] $Message" -ForegroundColor Red
}

function Add-Pass([string]$Message) {
  Write-Host "[ OK ] $Message" -ForegroundColor Green
}

function Test-NoPattern([string]$Name, [string]$Path, [string]$Pattern) {
  $fullPath = Join-Path $rootPath $Path
  if (-not (Test-Path -LiteralPath $fullPath)) {
    Add-Failure "${Name}: path ausente $Path"
    return
  }
  $matches = Get-ChildItem -LiteralPath $fullPath -Recurse -File | Where-Object {
    $_.Extension -in @(".py", ".html", ".js", ".ts", ".tsx", ".ps1", ".yml", ".yaml")
  } | Select-String -Pattern $Pattern -CaseSensitive:$false
  if ($matches) {
    Add-Failure "$Name encontrou $($matches.Count) ocorrencia(s)"
  } else {
    Add-Pass "$Name sem ocorrencias"
  }
}

Test-NoPattern -Name "token em localStorage/sessionStorage" -Path "sentinela/static" -Pattern "localStorage|sessionStorage|sentinela_token"
Test-NoPattern -Name "token/ticket/API key em query string" -Path "supreme-backend/src" -Pattern "[?&](token|ticket|api_key|api-key)="

$authPath = Join-Path $rootPath "sentinela/src/app/auth.py"
$authText = Get-Content -LiteralPath $authPath -Raw
$authRouterText = Get-Content -LiteralPath (Join-Path $rootPath "sentinela/src/app/api/auth_router.py") -Raw
foreach ($role in @("master", "pesquisador", "auditor", "operador", "leitura_agregada")) {
  if ($authText -notmatch [regex]::Escape($role)) { Add-Failure "RBAC nao declara role $role" }
}
if ($authText -match "SESSION_COOKIE_NAME" -and $authRouterText -match "httponly\s*=\s*True") {
  Add-Pass "sessao por cookie HttpOnly implementada"
} else {
  Add-Failure "sessao por cookie HttpOnly nao evidenciada"
}

$migrationText = Get-Content -LiteralPath (Join-Path $rootPath "sentinela/migrations/004_security_rbac_scopes.sql") -Raw
foreach ($term in @("institutions", "studies", "cases", "participant_registry", "user_scope_assignments")) {
  if ($migrationText -match $term) { Add-Pass "escopo $term modelado" } else { Add-Failure "escopo $term ausente" }
}

foreach ($dockerfile in @("sentinela/Dockerfile", "supreme-backend/Dockerfile")) {
  $text = Get-Content -LiteralPath (Join-Path $rootPath $dockerfile) -Raw
  if ($text -match "FROM python:3\.11\.9-slim" -and $text -match "USER appuser") {
    Add-Pass "$dockerfile usa base pinada e usuario nao-root"
  } else {
    Add-Failure "$dockerfile sem base pinada ou usuario nao-root"
  }
}

$composeText = Get-Content -LiteralPath (Join-Path $rootPath "docker-compose.production.yml") -Raw
if ($composeText -match ":latest") { Add-Failure "docker-compose.production.yml usa tag latest" } else { Add-Pass "docker compose sem latest" }
if ($composeText -match "healthcheck:") { Add-Pass "docker compose contem healthchecks" } else { Add-Failure "docker compose sem healthchecks" }

$ciText = Get-Content -LiteralPath (Join-Path $rootPath ".github/workflows/ci.yml") -Raw
foreach ($script in @("secret_scan.ps1", "dependency_scan.ps1", "sast_scan.ps1", "generate_sbom.ps1", "phase2_security_check.ps1")) {
  if ($ciText -match [regex]::Escape($script)) { Add-Pass "CI executa $script" } else { Add-Failure "CI nao executa $script" }
}

& (Join-Path $rootPath "scripts/secret_scan.ps1") -Root $rootPath
& (Join-Path $rootPath "scripts/dependency_scan.ps1") -Root $rootPath
& (Join-Path $rootPath "scripts/sast_scan.ps1") -Root $rootPath
& (Join-Path $rootPath "scripts/generate_sbom.ps1") -Root $rootPath

Write-Host ""
Write-Host "Resumo Fase 2 security check: $($failures.Count) falha(s)."
if ($failures.Count -gt 0) { exit 1 }
