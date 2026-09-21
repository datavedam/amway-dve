#!/usr/bin/env bash
set -uo pipefail

RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
NC=$'\033[0m'

check() {
  local name="$1" cmd="$2" version_flag="$3"
  if command -v "$cmd" >/dev/null 2>&1; then
    local version
    version=$("$cmd" $version_flag 2>&1 | grep -vE '^-*$' | head -n 1)
    printf "${GREEN}[OK]${NC}   %-8s installed -> %s\n" "$name" "$version"
  else
    printf "${RED}[MISS]${NC} %-8s not found in PATH\n" "$name"
  fi
}

check "Java"   java   -version
check "Python" python3 --version
check "Podman" podman --version
check "Claude" claude --version
check "Gradle" gradle --version

