#!/usr/bin/env bash
# Wait for the independently scheduled paper16 replays, then run one strict
# closeout.  This script never starts, stops, or modifies a simulator run.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/watch_c2p_paper16_closeout.sh [--interval SEC] [--once]

Poll the canonical/parallel C2P paper16 result roots.  Once every required
seven-mode, L2=50, CCD, and m/k summary exists, run finalize_c2p_paper16.sh
exactly once.  A strict-analysis failure is recorded and returned; it is not
retried, because it requires diagnosis rather than another blind replay.
EOF
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
interval=120
once=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --interval) interval="$2"; shift 2 ;;
    --once) once=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ "$interval" =~ ^[1-9][0-9]*$ ]] || {
  echo "error: --interval must be a positive integer" >&2; exit 2;
}

main_root="$repo_root/hw_run/c2p-paper16-v7-20260821"
main_supplemental=(
  "$repo_root/hw_run/c2p-paper16-v7-parallel-v2-20260821"
  "$repo_root/hw_run/c2p-paper16-v7-parallel-v3-20260821"
)
fast_root="$repo_root/hw_run/c2p-paper16-l2-50-v7-20260821"
fast_supplemental=("$repo_root/hw_run/c2p-paper16-l2-50-v7-parallel-v2-20260821")
# CCD's counter training was corrected after the initial campaign.  A fresh,
# exclusive root prevents the strict closeout from silently accepting any
# pre-fix CCD mode or metric replay.
ccd_root="$repo_root/hw_run/c2p-paper16-ccd-refresh-v2-20260821"
ccd_supplemental=()
sweep_root="$repo_root/hw_run/c2p-paper16-fp-sweep-v1-20260821"
sweep_supplemental=("$repo_root/hw_run/c2p-paper16-fp-sweep-parallel-v2-20260821")
queue_root="$repo_root/hw_run/c2p-btree-query-sensitivity-v1-20260821"
analysis_dir="$repo_root/hw_run/c2p-paper16-analysis-final-v7-20260821"
figures_dir="$repo_root/hw_run/c2p-paper16-figures-final-v7-20260821"
report="$repo_root/hw_run/c2p-paper16-report-final-v7-20260821.md"
lock_dir="$repo_root/hw_run/.c2p-paper16-final-closeout.lock"
log="$repo_root/hw_run/c2p-paper16-final-closeout.log"
manifest="$repo_root/configs/c2p-cache/paper16_workloads.tsv"

has_summary() {
  local case_name="$1" mode="$2" root
  shift 2
  for root in "$@"; do
    [[ -f "$root/$case_name/$mode/summary.txt" ]] && return 0
  done
  return 1
}

missing=()
collect_missing() {
  missing=()
  local case_name mode point
  while IFS=$'\t' read -r case_name _; do
    [[ -z "$case_name" || "$case_name" == case || "$case_name" == \#* ]] && continue
    for mode in baseline oracle ideal c2p ata ccd ring; do
      if [[ "$mode" == ccd ]]; then
        has_summary "$case_name" "$mode" "$ccd_root" "${ccd_supplemental[@]}" ||
          missing+=("main:$case_name/$mode")
      elif ! has_summary "$case_name" "$mode" "$main_root" "${main_supplemental[@]}"; then
        missing+=("main:$case_name/$mode")
      fi
    done
    has_summary "$case_name" baseline "$fast_root" "${fast_supplemental[@]}" ||
      missing+=("l2-50:$case_name/baseline")
    has_summary "$case_name" ccd "$ccd_root" "${ccd_supplemental[@]}" ||
      missing+=("ccd:$case_name/ccd")
    for point in m2048-k2 m3072-k3 m5120-k4 m9216-k5; do
      has_summary "$case_name" c2p "$sweep_root/$point" \
        "${sweep_supplemental[@]/%/$point}" ||
        missing+=("$point:$case_name/c2p")
    done
  done < "$manifest"
}

while :; do
  collect_missing
  if (( ${#missing[@]} == 0 )); then
    if ! mkdir "$lock_dir" 2>/dev/null; then
      printf 'closeout lock exists: %s\n' "$lock_dir"
      exit 0
    fi
    {
      printf 'all required summaries found at %s\n' "$(date -Is)"
      PYTHONPATH=/tmp/c2p-matplotlib-py311 \
      "$repo_root/scripts/finalize_c2p_paper16.sh" \
        --results-root "$main_root" \
        --supplemental-results-root "${main_supplemental[0]}" \
        --supplemental-results-root "${main_supplemental[1]}" \
        --l2-fast-root "$fast_root" \
        --supplemental-l2-fast-root "${fast_supplemental[0]}" \
        --ccd-metrics-root "$ccd_root" \
        --ccd-mode-root "$ccd_root" \
        --sweep-root "$sweep_root" \
        --supplemental-sweep-root "${sweep_supplemental[0]}" \
        --queue-sensitivity-root "$queue_root" \
        --analysis-dir "$analysis_dir" \
        --figures-dir "$figures_dir" \
        --report "$report" \
        --python /scratch/root/oss-eda/oss-cad-suite/py3bin/python3
    } >>"$log" 2>&1
    printf 'strict closeout passed: %s\n' "$report" | tee -a "$log"
    exit 0
  fi
  printf '%s waiting for %u summaries; first: %s\n' \
    "$(date -Is)" "${#missing[@]}" "${missing[0]}"
  (( once )) && exit 1
  sleep "$interval"
done
