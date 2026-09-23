@echo off
REM Checks that everything needed for the assignments is installed.
REM Run it with:  assignments\check-environment.cmd
setlocal enabledelayedexpansion

for /f %%a in ('echo prompt $E^|cmd') do set "ESC=%%a"
set "GREEN=%ESC%[32m"
set "RED=%ESC%[31m"
set "RESET=%ESC%[0m"

set ok=0
set missing=0

call :check "Claude Code CLI" claude "https://docs.claude.com/en/docs/claude-code"
call :check "uv (Python package/venv manager)" uv "https://docs.astral.sh/uv/getting-started/installation/"
call :check "python" python "https://www.python.org/downloads/ (or install via uv: uv python install)"
call :check "pip" pip "usually ships with python; if missing: python -m ensurepip"
call :check "node/npx (needed for the MCP Inspector devtools)" npx "https://nodejs.org/"

echo.
echo %ok% found, %missing% missing.
if %missing% gtr 0 (
    echo %RED%Install the missing tools above before starting the assignments.%RESET%
    exit /b 1
)
echo %GREEN%You're ready to start the assignments.%RESET%
exit /b 0

:check
where %~2 >nul 2>nul
if %errorlevel%==0 (
    echo %GREEN%[OK]%RESET%      %~1
    set /a ok+=1
) else (
    echo %RED%[MISSING]%RESET% %~1 -^> %~3
    set /a missing+=1
)
exit /b 0
