#!/usr/bin/env bash
# Wait for the V100 extension matrix, then perform its one strict audit.
# The V100 data is deliberately separate from the canonical paper16 result.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/watch_c2p_v100_extension_closeout.sh [--interval SEC] [--once]

Poll every expected main/L2=50 mode root for the V100 ISPASS/Pannotia
extension.  When all are present, run the strict extension audit once.  A
strict-audit failure is terminal and is recorded for diagnosis; it is never
silently retried.
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

manifest="$repo_root/configs/c2p-cache/v100_extension_workloads.tsv"
# A clean repair campaign supersedes the two roots that were exposed to a
# duplicate scheduler race.  It is searched first, while valid v1 results for
# all other cases remain usable without mixing this extension into paper16.
main_roots=(
  "$repo_root/hw_run/c2p-v100-main-matrix-repair-v1-20260822"
  "$repo_root/hw_run/c2p-v100-main-matrix-v1-20260822"
)
fast_roots=(
  "$repo_root/hw_run/c2p-v100-l2-50-matrix-repair-v1-20260822"
  "$repo_root/hw_run/c2p-v100-l2-50-matrix-v1-20260822"
)
baseline_root="$repo_root/hw_run/c2p-v100-baseline-full-v1-20260822"
archive_root="/workspace/worktrees/accel-sim-decoupled-l2/hw_run/tls-c2p-v100-20260822/archives"
trace_stage_root="$repo_root/hw_run/c2p-v100-baseline-compat-smoke-v2-20260822/stage"
out_dir="$repo_root/hw_run/c2p-v100-extension-audit-v1-20260822"
lock_dir="$repo_root/hw_run/.c2p-v100-extension-closeout.lock"
log="$repo_root/hw_run/c2p-v100-extension-closeout.log"
modes=(baseline oracle ideal c2p ata ccd ring)
repair_cases=(
  c2p-ispass-lib
  c2p-pannotia-mis
  c2p-pannotia-color-max
  c2p-pannotia-pagerank
)

missing=()
collect_missing() {
  missing=()
  local case_name _ mode
  while IFS=$'\t' read -r case_name _; do
    [[ -z "$case_name" || "$case_name" == case || "$case_name" == \#* ]] && continue
    [[ -f "$baseline_root/$case_name/baseline/summary.txt" ]] ||
      missing+=("uncapped-baseline:$case_name")
    for mode in "${modes[@]}"; do
      if [[ " ${repair_cases[*]} " == *" $case_name "* ]]; then
        [[ -f "${main_roots[0]}/$case_name/$mode/summary.txt" ]] ||
          missing+=("repair-main:$case_name/$mode")
        [[ -f "${fast_roots[0]}/$case_name/$mode/summary.txt" ]] ||
          missing+=("repair-l2-50:$case_name/$mode")
      else
        has_summary "$case_name" "$mode" "${main_roots[@]}" ||
          missing+=("main:$case_name/$mode")
        has_summary "$case_name" "$mode" "${fast_roots[@]}" ||
          missing+=("l2-50:$case_name/$mode")
      fi
    done
  done < "$manifest"
}

has_summary() {
  local case_name="$1" mode="$2" root
  shift 2
  for root in "$@"; do
    [[ -f "$root/$case_name/$mode/summary.txt" ]] && return 0
  done
  return 1
}

while :; do
  collect_missing
  if (( ${#missing[@]} == 0 )); then
    if ! mkdir "$lock_dir" 2>/dev/null; then
      printf 'closeout lock exists: %s\n' "$lock_dir"
      exit 0
    fi
    {
      printf 'all V100 extension roots found at %s\n' "$(date -Is)"
      audit_args=(
        --manifest "$manifest"
        --trace-stage-root "$trace_stage_root"
        --baseline-root "$baseline_root"
        --archive-root "$archive_root"
        --out-dir "$out_dir"
      )
      for root in "${main_roots[@]}"; do audit_args+=(--main-root "$root"); done
      for root in "${fast_roots[@]}"; do audit_args+=(--l2-50-root "$root"); done
      for case_name in "${repair_cases[@]}"; do audit_args+=(--require-primary-case "$case_name"); done
      python3 "$repo_root/scripts/analyze_c2p_v100_extension.py" "${audit_args[@]}" \
        --strict
    } >>"$log" 2>&1
    printf 'strict V100 extension audit passed: %s/extension_status.md\n' "$out_dir" | tee -a "$log"
    exit 0
  fi
  printf '%s waiting for %u V100 extension roots; first: %s\n' \
    "$(date -Is)" "${#missing[@]}" "${missing[0]}"
  if (( once )); then
    exit 1
  fi
  sleep "$interval"
done
