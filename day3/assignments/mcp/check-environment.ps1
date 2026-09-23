# Checks that everything needed for the assignments is installed.
# Run it with:  powershell -ExecutionPolicy Bypass -File assignments/check-environment.ps1

$ok = 0
$missing = 0

function Check-Tool {
    param(
        [string]$Name,
        [string]$Command,
        [string]$Hint
    )
    $found = Get-Command $Command -ErrorAction SilentlyContinue
    if ($found) {
        $version = & $Command --version 2>&1 | Select-Object -First 1
        Write-Host "[OK]      $Name -> $version" -ForegroundColor Green
        $script:ok++
    } else {
        Write-Host "[MISSING] $Name -> $Hint" -ForegroundColor Red
        $script:missing++
    }
}

Check-Tool "Claude Code CLI" "claude" "https://docs.claude.com/en/docs/claude-code"
Check-Tool "uv (Python package/venv manager)" "uv" "irm https://astral.sh/uv/install.ps1 | iex"
Check-Tool "python" "python" "https://www.python.org/downloads/ (or install via uv: 'uv python install')"
Check-Tool "pip" "pip" "usually ships with python; if missing: 'python -m ensurepip'"
Check-Tool "node/npx (needed for the MCP Inspector devtools)" "npx" "https://nodejs.org/"

Write-Host ""
Write-Host "$ok found, $missing missing."
if ($missing -gt 0) {
    Write-Host "Install the missing tools above before starting the assignments." -ForegroundColor Red
    exit 1
}
Write-Host "You're ready to start the assignments." -ForegroundColor Green
