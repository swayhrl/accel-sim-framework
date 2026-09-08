#!/usr/bin/env bash
# Future-only monitor for pending FAST64.3 Base acquisition.  It never starts,
# stops, signals, or waits on a simulator; a published terminal receipt is the
# only trigger for the corresponding strict collector.
set -euo pipefail

usage() { echo "usage: $0 [--log FILE] [--poll-seconds N] [--once]" >&2; exit 2; }
repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs=/workspace/fast64-runs
log="$runs/fast64_3_precompute_closeout_v2.log"
poll=120
once=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --log) log=${2:-}; shift 2 ;;
    --poll-seconds) poll=${2:-}; shift 2 ;;
    --once) once=1; shift ;;
    *) usage ;;
  esac
done
[[ "$poll" =~ ^[1-9][0-9]*$ ]] || usage

mkdir -p "$runs"
exec 8>"$runs/.fast64_3_precompute_closeout_v2.lock"
flock -n 8 || { echo FAST64_3_PRECOMPUTE_CLOSEOUT_LOCK_HELD >&2; exit 1; }
timestamp() { date -u +%FT%TZ; }
emit() { printf '%s\tutc=%s\t%s\n' "$1" "$(timestamp)" "$2" | tee -a "$log"; }

rows=(
  "atax|fast64_3_precomputed_atax_base_cap8192_a1_r2|collect_fast64_3_atax_base_alias_v2.sh|fast64_3_atax_base_alias_v2|FAST64_3_ATAX_BASE_ALIAS_V2.tsv"
  "gesummv|fast64_3_precomputed_gesummv_base_cap8192_a1_r2|collect_fast64_3_gesummv_base_alias_v2.sh|fast64_3_gesummv_base_alias_v2|FAST64_3_GESUMMV_BASE_ALIAS_V2.tsv"
)

while :; do
  complete=0
  for row in "${rows[@]}"; do
    IFS='|' read -r workload namespace collector output_dir evidence <<<"$row"
    run="$runs/$namespace"
    output="$repo/docs/dtc_l1/fast64/generated/$output_dir/$evidence"
    if [ -f "$output" ]; then
      complete=$((complete + 1))
      continue
    fi
    if [ -f "$run/RUN_TERMINAL.tsv" ]; then
      emit FAST64_3_PRECOMPUTE_TERMINAL_OBSERVED "workload=$workload namespace=$namespace"
      "$repo/util/dtc_l1/$collector"
      test -f "$output" || { emit FAST64_3_PRECOMPUTE_COLLECTOR_MISSING_EVIDENCE "workload=$workload"; exit 1; }
      emit FAST64_3_PRECOMPUTE_STRICT_PENDING_COLLECTED "workload=$workload namespace=$namespace"
      complete=$((complete + 1))
    else
      emit FAST64_3_PRECOMPUTE_WAIT_TERMINAL "workload=$workload namespace=$namespace"
    fi
  done
  [ "$complete" -eq "${#rows[@]}" ] && { emit FAST64_3_PRECOMPUTE_CLOSEOUT_COMPLETE "rows=$complete"; exit 0; }
  [ "$once" = 1 ] && exit 0
  sleep "$poll"
done
