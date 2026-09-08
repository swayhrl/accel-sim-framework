#!/usr/bin/env bash
# Future-only structural-metric companion monitor.  It is independent of the
# active v3/v4 Base collectors and all frozen FAST64.1 R2 closeout bytes.
set -euo pipefail

usage() { echo "usage: $0 --log FILE [--poll-seconds N] [--once]" >&2; exit 2; }
log= poll=120 once=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --log) log=${2:-}; shift 2 ;;
    --poll-seconds) poll=${2:-}; shift 2 ;;
    --once) once=1; shift ;;
    *) usage ;;
  esac
done
test -n "$log" && [[ "$poll" =~ ^[1-9][0-9]*$ ]] || usage

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs=/workspace/fast64-runs
rows=(atax gesummv dwt2d gemm)
exec 9>"$runs/.fast64_3_base_structural_companion_v1.lock"
flock -n 9 || { echo FAST64_3_BASE_STRUCTURAL_COMPANION_V1_ALREADY_ACTIVE >&2; exit 1; }
emit() { printf '%s\tutc=%s\t%s\n' "$1" "$(date -u +%FT%TZ)" "$2" >>"$log"; }

paths() {
  local workload=$1 flavor=v3
  [ "$workload" = gemm ] && flavor=v4
  row="fast64_3_precomputed_${workload}_base_cap8192_a1_r2"
  run="$runs/$row"
  dir="$repo/docs/dtc_l1/fast64/generated/fast64_3_${workload}_base_alias_$flavor"
  upper=$(printf '%s' "$workload" | tr '[:lower:]-' '[:upper:]_')
  summary="$dir/${row}.json"
  output="$dir/FAST64_3_${upper}_BASE_STRUCTURAL_METRICS_V1.json"
}

while :; do
  completed=0
  for workload in "${rows[@]}"; do
    paths "$workload"
    if test -f "$output"; then
      completed=$((completed + 1))
      continue
    fi
    if ! test -f "$run/RUN_TERMINAL.tsv"; then
      emit FAST64_3_BASE_STRUCTURAL_COMPANION_V1_WAIT_TERMINAL "workload=$workload namespace=$row"
      continue
    fi
    if ! test -f "$summary"; then
      emit FAST64_3_BASE_STRUCTURAL_COMPANION_V1_WAIT_STRICT_SUMMARY "workload=$workload namespace=$row"
      continue
    fi
    perf=$(find "$run" -maxdepth 1 -type f -name 'perf_counter_*.csv.gz' | sort | head -1)
    test -n "$perf" || { emit FAST64_3_BASE_STRUCTURAL_COMPANION_V1_MISSING_PERF "workload=$workload namespace=$row"; exit 1; }
    emit FAST64_3_BASE_STRUCTURAL_COMPANION_V1_EXTRACT "workload=$workload namespace=$row"
    "$repo/util/dtc_l1/extract_fast64_3_base_structural_metrics_v1.py" \
      --summary "$summary" --perf "$perf" --output "$output"
    test -f "$output" || { emit FAST64_3_BASE_STRUCTURAL_COMPANION_V1_MISSING_OUTPUT "workload=$workload"; exit 1; }
    emit FAST64_3_BASE_STRUCTURAL_COMPANION_V1_COLLECTED "workload=$workload namespace=$row"
    completed=$((completed + 1))
  done
  [ "$completed" -eq "${#rows[@]}" ] && { emit FAST64_3_BASE_STRUCTURAL_COMPANION_V1_COMPLETE "rows=$completed"; exit 0; }
  [ "$once" = 1 ] && exit 0
  sleep "$poll"
done
