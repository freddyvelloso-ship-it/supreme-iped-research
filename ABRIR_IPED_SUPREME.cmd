@echo off
setlocal

set "PACKAGE_IPED_HOME=%~dp0IPED-local\iped"
set "LOCAL_BUILD_IPED_HOME=C:\Users\nunas\Documents\Codex\2026-06-18\files-mentioned-by-the-user-nexus\work\supreme-v4-audit\tmp\iped-src\target\release\iped-4.4.0-SNAPSHOT"
if exist "%PACKAGE_IPED_HOME%" (
  set "IPED_HOME=%PACKAGE_IPED_HOME%"
) else (
  set "IPED_HOME=%LOCAL_BUILD_IPED_HOME%"
)
set "CASE_PATH=C:\iped-test-case"
set "SUPREME_URL=http://localhost:18100"
set "SENTINELA_URL=http://localhost:18101"

cd /d "%~dp0"

if not exist "%IPED_HOME%\iped.exe" if not exist "%IPED_HOME%\IPED-SearchApp.exe" if not exist "%IPED_HOME%\bin\IPED-SearchApp.exe" if not exist "%IPED_HOME%\lib\iped-search-app.jar" if not exist "%IPED_HOME%\iped.jar" (
  echo ERRO: IPED nao encontrado em "%IPED_HOME%".
  echo.
  pause
  exit /b 1
)

if not exist "%~dp0LAUNCHER_IPED.ps1" (
  echo ERRO: LAUNCHER_IPED.ps1 nao encontrado em "%~dp0".
  echo.
  pause
  exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0LAUNCHER_IPED.ps1" -CasePath "%CASE_PATH%"

if errorlevel 1 (
  echo.
  echo O launcher retornou erro. Copie a mensagem acima para depuracao.
  pause
)

endlocal
