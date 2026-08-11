#!/bin/zsh
set -euo pipefail

if [[ $# -lt 3 ]]; then
  print -u2 "Usage: render_cards.sh <cards.json> <output-dir> <profile.json> [--allow-draft]"
  exit 2
fi

script_dir="${0:A:h}"
input_json="${1:A}"
output_dir="${2:A}"
profile_json="${3:A}"
build_root="${TMPDIR:-/tmp}/xhs-ip-cards-renderer"
allow_draft="${4:-}"

mkdir -p "$output_dir" "$build_root/module-cache"
swiftc -module-cache-path "$build_root/module-cache" "$script_dir/render_cards.swift" -o "$build_root/render_cards"

if [[ "$allow_draft" == "--allow-draft" ]]; then
  "$build_root/render_cards" "$input_json" "$output_dir" "$profile_json" --allow-draft
else
  "$build_root/render_cards" "$input_json" "$output_dir" "$profile_json"
fi

