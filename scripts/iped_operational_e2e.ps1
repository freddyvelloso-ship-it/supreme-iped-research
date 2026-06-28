param(
  [string]$BaseUrl = $(if ($env:BASE_URL) { $env:BASE_URL } else { "https://localhost" }),
  [string]$PythonExe = $(if ($env:PYTHON_EXE) { $env:PYTHON_EXE } else { "python" }),
  [switch]$RequireSentinela
)

$ErrorActionPreference = "Stop"

$argsList = @("scripts\iped_operational_e2e.py", "--base-url", $BaseUrl)
if ($RequireSentinela) {
  $argsList += "--require-sentinela"
}

& $PythonExe @argsList
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}
