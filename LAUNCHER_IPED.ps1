param(
    [string]$UserId = "",
    [string]$CasePath = "",
    [switch]$SkipForms
)

# SUPREME V4 - Launcher IPED
# Fluxo: formularios pre-sessao -> IPED abre -> eventos capturados -> PANAS pos-sessao -> SUPREME -> SENTINELA
# Execute a partir de supreme_final\: .\LAUNCHER_IPED.ps1

Add-Type -AssemblyName Microsoft.VisualBasic
Add-Type -AssemblyName System.Windows.Forms

$IPED_HOME = $env:IPED_HOME
if (-not $IPED_HOME) {
    $candidates = @(
        "$PSScriptRoot\IPED-local",
        "$PSScriptRoot\IPED-local\iped",
        "C:\iped-test-case", "C:\iped", "C:\IPED", "C:\iped-4.2", "C:\iped-4.1",
        "$env:ProgramFiles\IPED", "$env:LOCALAPPDATA\IPED"
    )
    foreach ($c in $candidates) {
        $hasExe  = (Test-Path "$c\iped.exe") -or (Test-Path "$c\IPED-SearchApp.exe") -or (Test-Path "$c\bin\IPED-SearchApp.exe")
        $hasJar  = Test-Path "$c\iped.jar"
        $hasJar2 = Test-Path "$c\iped-searchapp.jar"
        if ($hasExe -or $hasJar -or $hasJar2) { $IPED_HOME = $c; break }
    }
}

if (-not $IPED_HOME -or -not (Test-Path $IPED_HOME)) {
    $IPED_HOME = [Microsoft.VisualBasic.Interaction]::InputBox(
        "Informe o caminho completo da pasta do IPED:",
        "SUPREME V4 - Caminho do IPED", "C:\iped-test-case")
    if (-not $IPED_HOME -or -not (Test-Path $IPED_HOME)) {
        [System.Windows.Forms.MessageBox]::Show("Caminho invalido.", "Erro", "OK", "Error") | Out-Null
        exit 1
    }
}

function Test-ServiceUrl {
    param([string]$BaseUrl, [string]$HealthPath = "/health")
    if (-not $BaseUrl) { return $false }
    try {
        $raw = curl.exe -sk --max-time 2 ($BaseUrl.TrimEnd("/") + $HealthPath) 2>&1
        return ($LASTEXITCODE -eq 0 -and (($raw -join "") -match '"status"\s*:\s*"ok"|status\s*[:=]\s*ok'))
    } catch {
        return $false
    }
}

function Resolve-ServiceUrl {
    param([string]$EnvUrl, [string[]]$Candidates, [string]$HealthPath = "/health")
    if ($EnvUrl -and (Test-ServiceUrl $EnvUrl $HealthPath)) { return $EnvUrl.TrimEnd("/") }
    foreach ($candidate in $Candidates) {
        if (Test-ServiceUrl $candidate $HealthPath) { return $candidate.TrimEnd("/") }
    }
    if ($EnvUrl) { return $EnvUrl.TrimEnd("/") }
    return $Candidates[0].TrimEnd("/")
}

$SUPREME_URL = Resolve-ServiceUrl $env:SUPREME_URL @("http://localhost:18000", "http://localhost:18100")
$SENTINELA_URL = Resolve-ServiceUrl $env:SENTINELA_URL @("http://localhost:18001", "http://localhost:18101")

$scriptDir    = Split-Path -Parent $MyInvocation.MyCommand.Path
$envFile      = Join-Path $scriptDir "supreme-backend\.env.production"
if (-not (Test-Path $envFile)) {
    [System.Windows.Forms.MessageBox]::Show("Rode SUBIR_LOCAL.ps1 primeiro.", "Erro", "OK", "Error") | Out-Null
    exit 1
}

function Get-EnvVal($file, $key) {
    if (-not (Test-Path -LiteralPath $file)) { return $null }
    $line = Get-Content $file | Where-Object { $_ -match "^${key}=" } | Select-Object -First 1
    if ($line) { return ($line -split "=", 2)[1] }
    return $null
}

function Resolve-AuditLog($rootDir) {
    $rootEnv = Join-Path $rootDir ".env"
    $auditDir = Get-EnvVal $rootEnv "IPED_AUDIT_DIR"
    if ($auditDir) {
        if (-not [System.IO.Path]::IsPathRooted($auditDir)) {
            $auditDir = Join-Path $rootDir $auditDir
        }
        New-Item -ItemType Directory -Force -Path $auditDir | Out-Null
        return (Join-Path $auditDir "supreme_audit.ndjson")
    }
    return "$env:USERPROFILE\supreme_audit.ndjson"
}

$API_INGEST_TOKEN = Get-EnvVal $envFile "API_INGEST_TOKEN"
$API_SECRET_KEY   = Get-EnvVal $envFile "API_SECRET_KEY"
$SUPREME_SALT     = Get-EnvVal $envFile "SUPREME_SALT"

if (-not $API_INGEST_TOKEN -or -not $API_SECRET_KEY -or -not $SUPREME_SALT) {
    [System.Windows.Forms.MessageBox]::Show("API_INGEST_TOKEN, API_SECRET_KEY ou SUPREME_SALT nao encontrado.", "Erro", "OK", "Error") | Out-Null
    exit 1
}

# Pedir ID funcional, salvo em modo assistido/automatizado.
$userId = $UserId
if (-not $userId) {
    $userId = [Microsoft.VisualBasic.Interaction]::InputBox(
        "Digite seu ID funcional para iniciar a sessao SUPREME V4:",
        "SUPREME V4 - Identificacao do Perito", "")
    if ($userId -eq "") { exit }
}

# Calcular id_hash
$sha256 = [System.Security.Cryptography.SHA256]::Create()
$bytes  = [System.Text.Encoding]::UTF8.GetBytes($userId + $SUPREME_SALT)
$hash   = $sha256.ComputeHash($bytes)
$idHash = ($hash | ForEach-Object { $_.ToString("x2") }) -join ""
$sha256.Dispose()

$env:SUPREME_USER_ID = $userId
$auditLog = Resolve-AuditLog $scriptDir

function Open-Url {
    param([string]$Url)
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $Url
    $psi.UseShellExecute = $true
    [System.Diagnostics.Process]::Start($psi) | Out-Null
}

function New-FormLink {
    param([string]$Instrument)

    $tmp = New-TemporaryFile
    try {
        @{ id_hash = $idHash; instrument = $Instrument } |
            ConvertTo-Json -Compress |
            Set-Content -Encoding UTF8 -LiteralPath $tmp

        $resp = curl.exe -sk --max-time 8 -X POST ($SUPREME_URL + "/v1/forms/link") `
            -H "Content-Type: application/json" `
            -H "Authorization: Bearer $API_SECRET_KEY" `
            --data-binary "@$tmp" 2>&1

        if ($LASTEXITCODE -ne 0) {
            throw "Falha ao gerar link do formulario ${Instrument}: $resp"
        }

        $obj = ($resp -join "") | ConvertFrom-Json
        $targetUrl = if ($obj.launch_url) { $obj.launch_url } else { $obj.url }
        if (-not $targetUrl) {
            throw "Resposta invalida ao gerar link do formulario $Instrument."
        }
        return $SUPREME_URL + $targetUrl
    } finally {
        Remove-Item -LiteralPath $tmp -ErrorAction SilentlyContinue
    }
}

function Get-DueInstruments {
    $resp = curl.exe -s --max-time 8 -H "Authorization: Bearer $API_SECRET_KEY" $schedUrl 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Schedule API indisponivel. Nao e seguro liberar o IPED sem confirmar os questionarios."
    }
    $raw = ($resp -join "")
    if (-not ($raw -match "due_now")) {
        throw "Schedule API retornou resposta inesperada. Nao e seguro liberar o IPED."
    }
    $obj = $raw | ConvertFrom-Json
    return @($obj.due_now | ForEach-Object { [string]$_ })
}

function Wait-RequiredForms {
    param(
        [array]$RequiredInstruments
    )

    if ($RequiredInstruments.Count -eq 0) { return }

    while ($true) {
        try {
            $due = Get-DueInstruments
            $pending = @($RequiredInstruments | Where-Object { $due -contains $_.key })
        } catch {
            [System.Windows.Forms.MessageBox]::Show(
                $_.Exception.Message,
                "SUPREME V4 - Bloqueio de seguranca", "OK", "Warning") | Out-Null
            Start-Sleep -Seconds 3
            continue
        }

        if ($pending.Count -eq 0) {
            Write-Host "Questionarios pre-sessao concluidos. Liberando IPED." -ForegroundColor Green
            [System.Windows.Forms.MessageBox]::Show(
                "Questionarios pre-sessao concluidos.`n`nClique OK para continuar para o IPED.",
                "SUPREME V4 - IPED liberado",
                "OK",
                "Information") | Out-Null
            return
        }

        $nomesPendentes = ($pending | ForEach-Object { $_.label }) -join ", "
        Write-Host "Aguardando conclusao dos questionarios: $nomesPendentes" -ForegroundColor Yellow
        Write-Host "Os links ja foram abertos uma vez nesta sessao; nao serao reabertos automaticamente." -ForegroundColor DarkYellow

        Start-Sleep -Seconds 3
    }
}

# Verificar quais formularios estao vencidos via API
$preInstruments = @(
    @{ key = "SRQ20";  label = "SRQ-20";  path = "srq20"  }
    @{ key = "DASS21"; label = "DASS-21"; path = "dass21" }
    @{ key = "OLBI";   label = "OLBI";    path = "olbi"   }
)

$toOpen = @()
$schedUrl = $SUPREME_URL + "/v1/schedule/" + $idHash
$schedResp = curl.exe -sk --max-time 8 -H "Authorization: Bearer $API_SECRET_KEY" $schedUrl 2>&1

if ($LASTEXITCODE -eq 0 -and ($schedResp -join "") -match "due_now") {
    try {
        $schedObj = ($schedResp -join "") | ConvertFrom-Json
        $dueNow   = @($schedObj.due_now | ForEach-Object { [string]$_ })
        $toOpen   = $preInstruments | Where-Object { $dueNow -contains $_.key }
        Write-Host "Schedule: vencidos = $($dueNow -join ', ')" -ForegroundColor Cyan
    } catch {
        Write-Host "Schedule parse falhou - abrindo todos." -ForegroundColor Yellow
        $toOpen = $preInstruments
    }
} else {
    Write-Host "Schedule API offline - abrindo todos (primeira sessao)." -ForegroundColor Yellow
    $toOpen = $preInstruments
}

# Formularios pre-IPED
if ($SkipForms) {
    Write-Host "Modo SkipForms: instrumentos psicometricos nao serao abertos antes do IPED." -ForegroundColor Yellow
} elseif ($toOpen.Count -gt 0) {
    $nomes = ($toOpen | ForEach-Object { $_.label }) -join ", "
    Write-Host "Abrindo instrumentos psicometricos automaticamente: $nomes" -ForegroundColor Cyan

    foreach ($inst in $toOpen) {
        $formUrl = New-FormLink $inst.key
        Open-Url $formUrl
        Start-Sleep -Seconds 2
    }

    Wait-RequiredForms -RequiredInstruments $toOpen
}

# Registrar inicio de sessao
$sessionStart = [DateTimeOffset]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
$sessTs       = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$sessBody = '{"events":[{"user_identifier":"' + $idHash + '","timestamp":"' + $sessionStart + '","event_type":"session_start","media_type":"preview","severity":1,"duration_seconds":0,"source_tool":"iped"}]}'
$sessBody | Set-Content -Encoding UTF8 _sess.json
$ingestUrl = $SUPREME_URL + "/v1/events/ingest"
curl.exe -sk -X POST $ingestUrl -H "Content-Type: application/json" -H "Authorization: Bearer $API_INGEST_TOKEN" --data-binary "@_sess.json" 2>&1 | Out-Null
Remove-Item _sess.json -ErrorAction SilentlyContinue

# Registrar linhas antes de abrir IPED
$linesBefore = 0
if (Test-Path $auditLog) {
    $linesBefore = (Get-Content $auditLog | Measure-Object -Line).Lines
}

Write-Host "Abrindo IPED em: $IPED_HOME" -ForegroundColor Cyan

# Detectar executavel do IPED
$ipedExe = $null
$ipedJar = $null
$ipedRuntimeDir = $IPED_HOME
if (Test-Path "$IPED_HOME\iped\lib\iped-search-app.jar") {
    $ipedRuntimeDir = "$IPED_HOME\iped"
}

if (Test-Path "$ipedRuntimeDir\lib\iped-search-app.jar") {
    # Prefer the Java entrypoint for the bundled/instrumented runtime. Some
    # native launchers detach immediately and make the workflow think IPED was
    # closed, which would incorrectly trigger post-session forms.
    $ipedJar = "$ipedRuntimeDir\lib\iped-search-app.jar"
} elseif (Test-Path "$IPED_HOME\iped.exe") {
    $ipedExe = "$IPED_HOME\iped.exe"
} elseif (Test-Path "$IPED_HOME\IPED-SearchApp.exe") {
    $ipedExe = "$IPED_HOME\IPED-SearchApp.exe"
} elseif (Test-Path "$IPED_HOME\bin\IPED-SearchApp.exe") {
    $ipedExe = "$IPED_HOME\bin\IPED-SearchApp.exe"
} elseif (Test-Path "$IPED_HOME\iped-searchapp.jar") {
    $ipedJar = "$IPED_HOME\iped-searchapp.jar"
} elseif (Test-Path "$ipedRuntimeDir\lib\iped-search-app.jar") {
    $ipedJar = "$ipedRuntimeDir\lib\iped-search-app.jar"
} elseif (Test-Path "$IPED_HOME\iped.jar") {
    $ipedJar = "$IPED_HOME\iped.jar"
} else {
    $jars = Get-ChildItem $IPED_HOME -Filter "*.jar" | Where-Object { $_.Name -match "iped" }
    if ($jars) { $ipedJar = $jars[0].FullName }
}

if (-not $ipedExe -and -not [string]::IsNullOrWhiteSpace($CasePath) -and (Test-Path "$ipedRuntimeDir\lib\iped-search-app.jar")) {
    # The native launcher may detach from Java and return before the real UI
    # session ends. For real acceptance with an external case path, run the
    # instrumented JVM entrypoint directly so -case and environment variables
    # are inherited by the process the gate is waiting on.
    $ipedExe = $null
    $ipedJar = "$ipedRuntimeDir\lib\iped-search-app.jar"
}

$patchJar = "$IPED_HOME\plugins\supreme-audit-patch.jar"
if (-not (Test-Path $patchJar) -and (Test-Path "$ipedRuntimeDir\plugins\supreme-audit-patch.jar")) {
    $patchJar = "$ipedRuntimeDir\plugins\supreme-audit-patch.jar"
}
$extraCp  = ""
if (Test-Path $patchJar) {
    $extraCp = ";" + $patchJar
    Write-Host "Patch Java: $patchJar" -ForegroundColor Green
} else {
    Write-Host "Patch Java nao encontrado - duracao sera estimada." -ForegroundColor Yellow
}

$env:SUPREME_AUDIT_LOG = $auditLog
$env:SUPREME_USER_ID   = $userId
$ipedStarted = $false
$minimumVisibleSeconds = 8

if ($ipedExe) {
    $args = @()
    if (-not [string]::IsNullOrWhiteSpace($CasePath)) {
        $args += @("-case", $CasePath)
    }
    $proc = Start-Process $ipedExe -ArgumentList $args -WorkingDirectory $IPED_HOME -PassThru
    Start-Sleep -Seconds $minimumVisibleSeconds
    if ($proc.HasExited) {
        [System.Windows.Forms.MessageBox]::Show(
            "O IPED foi iniciado, mas encerrou imediatamente. O fluxo pos-sessao nao sera aberto.`n`nVerifique o caminho do IPED ou abra novamente pelo atalho.",
            "SUPREME V4 - IPED nao iniciou", "OK", "Error") | Out-Null
        exit 1
    }
    $ipedStarted = $true
    $proc.WaitForExit()
} elseif ($ipedJar) {
    $libCp = ""
    if (Test-Path "$ipedRuntimeDir\lib") {
        $libCp = ";" + (Join-Path $ipedRuntimeDir "lib\*")
    }
    $javaArgs = "-cp `"" + $ipedJar + $libCp + $extraCp + "`" iped.app.ui.AppMain"
    if (-not [string]::IsNullOrWhiteSpace($CasePath)) {
        $javaArgs += " -case `"$CasePath`""
    }
    $javaExe = "java"
    if (Test-Path "$ipedRuntimeDir\jre\bin\java.exe") {
        $javaExe = "$ipedRuntimeDir\jre\bin\java.exe"
    }
    $proc = Start-Process $javaExe -ArgumentList $javaArgs -WorkingDirectory $ipedRuntimeDir -PassThru
    Start-Sleep -Seconds $minimumVisibleSeconds
    if ($proc.HasExited) {
        [System.Windows.Forms.MessageBox]::Show(
            "O IPED foi iniciado, mas encerrou imediatamente. O fluxo pos-sessao nao sera aberto.`n`nVerifique o runtime Java/IPED e tente novamente.",
            "SUPREME V4 - IPED nao iniciou", "OK", "Error") | Out-Null
        exit 1
    }
    $ipedStarted = $true
    $proc.WaitForExit()
} else {
    [System.Windows.Forms.MessageBox]::Show(
        "IPED nao encontrado em: $IPED_HOME",
        "SUPREME V4 - Erro", "OK", "Error") | Out-Null
    exit 1
}

if (-not $ipedStarted) {
    [System.Windows.Forms.MessageBox]::Show(
        "O IPED nao foi iniciado. O fluxo pos-sessao nao sera aberto.",
        "SUPREME V4 - IPED nao iniciou", "OK", "Error") | Out-Null
    exit 1
}

# Pos-sessao
Start-Sleep -Seconds 5

$linesAfter = 0
if (Test-Path $auditLog) {
    $linesAfter = (Get-Content $auditLog | Measure-Object -Line).Lines
}

$houveSessao = $true

# Registrar encerramento
$endTs   = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$endTime = [DateTimeOffset]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
$endBody = '{"events":[{"user_identifier":"' + $idHash + '","timestamp":"' + $endTime + '","event_type":"session_end","media_type":"preview","severity":1,"duration_seconds":0,"source_tool":"iped"}]}'
$endBody | Set-Content -Encoding UTF8 _end.json
curl.exe -sk -X POST $ingestUrl -H "Content-Type: application/json" -H "Authorization: Bearer $API_INGEST_TOKEN" --data-binary "@_end.json" 2>&1 | Out-Null
Remove-Item _end.json -ErrorAction SilentlyContinue

# Verificar se PANAS esta vencido. Em aceite automatizado, -SkipForms precisa
# pular tambem formularios pos-sessao para nao bloquear a validacao IPED.
if ($SkipForms) {
    Write-Host "Modo SkipForms: instrumento pos-sessao nao sera aberto." -ForegroundColor Yellow
} else {
    $panasDue = $true
    $sched2Resp = curl.exe -sk --max-time 8 -H "Authorization: Bearer $API_SECRET_KEY" $schedUrl 2>&1
    if ($LASTEXITCODE -eq 0 -and ($sched2Resp -join "") -match "due_now") {
        try {
            $sched2Obj = ($sched2Resp -join "") | ConvertFrom-Json
            $due2      = @($sched2Obj.due_now | ForEach-Object { [string]$_ })
            $panasDue  = ($due2 -contains "PANAS_SHORT")
        } catch { }
    }

    if ($panasDue) {
        [System.Windows.Forms.MessageBox]::Show(
            "Sessao encerrada. O instrumento PANAS sera aberto para avaliacao pos-exposicao.",
            "SUPREME V4 - Pos-Sessao", "OK", "Information") | Out-Null
        $panasUrl = New-FormLink "PANAS_SHORT"
        Open-Url $panasUrl
    }
}

Write-Host "Sessao encerrada. Dashboard: $SENTINELA_URL" -ForegroundColor Cyan
