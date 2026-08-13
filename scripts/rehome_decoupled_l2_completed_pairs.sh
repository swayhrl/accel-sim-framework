#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/rehome_decoupled_l2_completed_pairs.sh --source-root DIR --dest-root DIR
       [--manifest FILE]

Move a completed baseline/decoupled workload pair from SOURCE-ROOT to the
matching case path below DEST-ROOT. A pair is eligible only after both
simulators wrote the normal GPGPU-Sim exit marker and no live process still
has a current working directory below the source case.
EOF
}

source_root=""
dest_root=""
manifest=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --source-root) source_root="$2"; shift 2 ;;
    --dest-root) dest_root="$2"; shift 2 ;;
    --manifest) manifest="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -d "$source_root" && -d "$dest_root" ]] || {
  echo "error: --source-root and --dest-root must be existing directories" >&2
  exit 2
}
source_root="$(cd "$source_root" && pwd)"
dest_root="$(cd "$dest_root" && pwd)"
if [[ -z "$manifest" ]]; then
  manifest="$dest_root/rehome_completed_pairs.csv"
fi
mkdir -p "$(dirname "$manifest")"
if [[ ! -f "$manifest" ]]; then
  printf 'time,case,source,destination\n' > "$manifest"
fi

pair_complete() {
  local case_dir="$1" backend out
  for backend in baseline decoupled; do
    out="$case_dir/NO_ARGS/$backend/smoke.out"
    [[ -f "$out" ]] || return 1
    rg -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$out" || return 1
    [[ -f "$case_dir/NO_ARGS/$backend/simulator_provenance.txt" ]] || return 1
  done
}

pair_is_live() {
  local case_dir="$1" pid cwd
  while read -r pid; do
    cwd="$(readlink "/proc/$pid/cwd" 2>/dev/null || true)"
    [[ "$cwd" == "$case_dir" || "$cwd" == "$case_dir"/* ]] && return 0
  done < <(pgrep -f 'accel-sim\.out' || true)
  return 1
}

shopt -s nullglob
for case_dir in "$source_root"/polybench-*; do
  case_name="$(basename "$case_dir")"
  dest_case="$dest_root/$case_name"
  [[ -d "$case_dir/NO_ARGS" ]] || continue
  if [[ -e "$dest_case" ]]; then
    echo "SKIP destination_exists case=$case_name destination=$dest_case" >&2
    continue
  fi
  if ! pair_complete "$case_dir"; then
    echo "WAIT incomplete case=$case_name" >&2
    continue
  fi
  if pair_is_live "$case_dir"; then
    echo "WAIT live_process case=$case_name" >&2
    continue
  fi
  mv "$case_dir" "$dest_case"
  printf '%s,%s,%s,%s\n' "$(date --iso-8601=seconds)" "$case_name" \
    "$case_dir" "$dest_case" >> "$manifest"
  echo "MOVED case=$case_name destination=$dest_case"
done
