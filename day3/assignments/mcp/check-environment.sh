#!/usr/bin/env bash
# Checks that everything needed for the assignments is installed.
# Run it with:  bash assignments/check-environment.sh
set -uo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
RESET='\033[0m'

ok=0
missing=0

check() {
  local name="$1"
  local cmd="$2"
  local hint="$3"
  if command -v "$cmd" >/dev/null 2>&1; then
    printf "${GREEN}[OK]${RESET}      %s -> %s\n" "$name" "$("$cmd" --version 2>&1 | head -n1)"
    ok=$((ok + 1))
  else
    printf "${RED}[MISSING]${RESET} %s -> %s\n" "$name" "$hint"
    missing=$((missing + 1))
  fi
}

check "Claude Code CLI" "claude" "https://docs.claude.com/en/docs/claude-code"
check "uv (Python package/venv manager)" "uv" "curl -LsSf https://astral.sh/uv/install.sh | sh"
check "python3" "python3" "https://www.python.org/downloads/ (or install via uv: 'uv python install')"
check "pip" "pip3" "usually ships with python3; if missing: 'python3 -m ensurepip'"
check "node/npx (needed for the MCP Inspector devtools)" "npx" "https://nodejs.org/"

echo
echo "$ok found, $missing missing."
if [ "$missing" -gt 0 ]; then
  printf "${RED}Install the missing tools above before starting the assignments.${RESET}\n"
  exit 1
fi
printf "${GREEN}You're ready to start the assignments.${RESET}\n"
