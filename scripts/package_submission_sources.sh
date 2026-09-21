#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
paper_dir="$repo_root/paper"
out_dir="${1:-$repo_root/dist}"
manifest="$paper_dir/SUBMISSION_SOURCE_MANIFEST.txt"
zip_path="$out_dir/adaptive-pc-fmcw-isac-ieee-sources.zip"

mkdir -p "$out_dir"
rm -f "$zip_path"

while IFS= read -r rel; do
  [[ -z "$rel" ]] && continue
  [[ -f "$paper_dir/$rel" ]] || { echo "Missing required source: $rel" >&2; exit 1; }
done < "$manifest"

(
  cd "$paper_dir"
  mapfile -t files < <(grep -v '^[[:space:]]*$' SUBMISSION_SOURCE_MANIFEST.txt)
  zip -X -q "$zip_path" "${files[@]}"
)

echo "$zip_path"
