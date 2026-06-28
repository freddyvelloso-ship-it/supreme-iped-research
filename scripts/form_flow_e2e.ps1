param(
  [string]$BaseUrl = $(if ($env:BASE_URL) { $env:BASE_URL } else { "https://localhost" }),
  [string]$ApiSecretKey = $env:API_SECRET_KEY,
  [string]$PythonExe = $(if ($env:PYTHON_EXE) { $env:PYTHON_EXE } else { "python" })
)

$ErrorActionPreference = "Stop"

$argsList = @(
  "scripts\form_flow_e2e.py",
  "--base-url", $BaseUrl,
  "--insecure-tls"
)

if ($ApiSecretKey) {
  $argsList += @("--api-secret-key", $ApiSecretKey)
}

& $PythonExe @argsList
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}
