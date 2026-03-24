#!/bin/bash
# Wrapper: load .env then run a Python skill
# Usage: run_skill.sh skills/<name>/run_<name>.py [args...]
REPO="$(cd "$(dirname "$0")/.." && pwd)"

if [ -f "$REPO/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$REPO/.env"
  set +a
else
  echo "[run_skill] WARNING: .env not found at $REPO/.env" >&2
fi

cd "$REPO"
exec python3 "$@"
