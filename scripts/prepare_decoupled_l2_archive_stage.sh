#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/prepare_decoupled_l2_archive_stage.sh --archive SUITE.tgz
       --case-list CASES.csv --stage-dir DIR [--min-free-gib N]

Extract selected trace directories into a persistent reusable stage.  A marker
is written only after the complete tar extraction succeeds, so a later batch
can distinguish a complete case from a concurrent or partial extraction.
EOF
}

archive=""; case_list=""; stage_dir=""; min_free_gib=40
while [[ $# -gt 0 ]]; do
  case "$1" in
    --archive) archive="$2"; shift 2 ;;
    --case-list) case_list="$2"; shift 2 ;;
    --stage-dir) stage_dir="$2"; shift 2 ;;
    --min-free-gib) min_free_gib="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ -f "$archive" && -f "$case_list" && -n "$stage_dir" ]] || {
  echo "error: archive, case-list, and stage-dir are required" >&2; exit 2;
}
[[ "$min_free_gib" =~ ^[0-9]+$ ]] || { echo "error: invalid reserve" >&2; exit 2; }
mkdir -p "$stage_dir"
stage_dir="$(cd "$stage_dir" && pwd)"
selected="$(mktemp)"; patterns="$(mktemp)"
trap 'rm -f "$selected" "$patterns"' EXIT
awk -F, 'NF && $1 != "case" { sub(/^\.\//, "", $1); print $1 }' "$case_list" | sort -u > "$selected"
[[ -s "$selected" ]] || { echo "error: no selected cases" >&2; exit 2; }
size_kib="$(awk -F, 'NR > 1 { bytes += $2 } END { print int((bytes + 1023) / 1024) }' "$case_list")"
avail_kib="$(df -Pk "$stage_dir" | awk 'NR == 2 { print $4 }')"
reserve_kib=$((min_free_gib * 1024 * 1024))
(( avail_kib >= reserve_kib + size_kib )) || {
  echo "error: selected stage exceeds disk reserve" >&2; exit 1;
}
# Legacy archives are inconsistent: some preserve a leading "./" and some
# start directly at the suite directory.  Keep both spellings so the stage
# result is determined by the selected case, not that packaging detail.
awk '{ printf "%s/traces/*\n./%s/traces/*\n", $0, $0 }' "$selected" > "$patterns"
if command -v pigz >/dev/null 2>&1; then
  tar --use-compress-program=pigz --extract --wildcards --directory "$stage_dir" --files-from="$patterns" --file "$archive"
else
  tar --gzip --extract --wildcards --directory "$stage_dir" --files-from="$patterns" --file "$archive"
fi
mkdir -p "$stage_dir/.decoupled_l2_stage_complete"
while IFS= read -r case_path; do
  [[ -f "$stage_dir/$case_path/traces/kernelslist.g" ]] || {
    echo "error: extraction lost $case_path" >&2; exit 1;
  }
  : > "$stage_dir/.decoupled_l2_stage_complete/${case_path//\//__}"
done < "$selected"
printf 'PASS stage=%s cases=%s\n' "$stage_dir" "$(wc -l < "$selected")"
