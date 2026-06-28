param(
    [string]$BaseUrl = $(if ($env:BASE_URL) { $env:BASE_URL } else { "https://localhost" }),
    [string]$PythonExe = $env:PYTHON_EXE,
    [int]$TimeoutSeconds = 180
)

$ErrorActionPreference = "Stop"

$pythonPrefix = @()
if (-not $PythonExe) {
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $PythonExe = "python"
    } elseif (Get-Command py -ErrorAction SilentlyContinue) {
        $PythonExe = "py"
        $pythonPrefix = @("-3")
    } else {
        throw "Python 3 nao encontrado. Instale Python 3, habilite o py launcher, ou defina PYTHON_EXE."
    }
}

& $PythonExe @pythonPrefix "scripts\local_e2e_iped_to_sentinela.py" `
    --base-url $BaseUrl `
    --timeout-seconds $TimeoutSeconds

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
