#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: render_cards.sh <cards.json> <output-dir> <profile.json> [--allow-draft]" >&2
  exit 2
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
  python_cmd="python3"
elif command -v python >/dev/null 2>&1; then
  python_cmd="python"
else
  echo "ERROR: Python 3 was not found." >&2
  exit 5
fi

exec "$python_cmd" "$script_dir/render_cards.py" "$@"
