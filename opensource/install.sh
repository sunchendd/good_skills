#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCES_FILE="$ROOT_DIR/sources.txt"

if [[ ! -f "$SOURCES_FILE" ]]; then
  echo "sources.txt not found: $SOURCES_FILE" >&2
  exit 1
fi

while IFS= read -r line || [[ -n "$line" ]]; do
  command="$(printf '%s' "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"

  if [[ -z "$command" ]]; then
    continue
  fi

  if [[ "$command" == \#* ]]; then
    continue
  fi

  echo ">> $command"
  eval "$command"
done < "$SOURCES_FILE"

echo "Open source skill installation completed."
