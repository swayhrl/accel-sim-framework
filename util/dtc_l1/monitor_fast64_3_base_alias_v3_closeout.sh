#!/usr/bin/env bash
# Future-only closeout monitor for the three pending immutable Base rows.
set -euo pipefail

usage() { echo "usage: $0 --log FILE [--poll-seconds N] [--once]" >&2; exit 2; }
log= poll=120 once=0
while [ "$#" -gt 0 ]; do
  case "$1" in --log) log=${2:-};shift 2;; --poll-seconds) poll=${2:-};shift 2;; --once) once=1;shift;; *) usage;; esac
done
test -n "$log" && [[ "$poll" =~ ^[1-9][0-9]*$ ]] || usage

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs=/workspace/fast64-runs
lock="$runs/.fast64_3_base_alias_v3_closeout.lock"
rows=(atax gesummv dwt2d)
exec 9>"$lock"
flock -n 9 || { echo FAST64_3_BASE_ALIAS_V3_MONITOR_ALREADY_ACTIVE >&2; exit 1; }
emit() { printf '%s\tutc=%s\t%s\n' "$1" "$(date -u +%FT%TZ)" "$2" | tee -a "$log"; }

while :; do
  complete=0
  for workload in "${rows[@]}"; do
    row="fast64_3_precomputed_${workload}_base_cap8192_a1_r2"
    run="$runs/$row"
    evidence="$repo/docs/dtc_l1/fast64/generated/fast64_3_${workload}_base_alias_v3/FAST64_3_$(printf '%s' "$workload" | tr '[:lower:]' '[:upper:]')_BASE_ALIAS_V3.tsv"
    if test -f "$evidence"; then complete=$((complete + 1)); continue; fi
    if test -f "$run/RUN_TERMINAL.tsv"; then
      emit FAST64_3_BASE_ALIAS_V3_TERMINAL_OBSERVED "workload=$workload namespace=$row"
      "$repo/util/dtc_l1/collect_fast64_3_base_alias_v3.sh" --workload "$workload"
      test -f "$evidence" || { emit FAST64_3_BASE_ALIAS_V3_MISSING_EVIDENCE "workload=$workload"; exit 1; }
      emit FAST64_3_BASE_ALIAS_V3_PENDING_COLLECTED "workload=$workload namespace=$row"
      complete=$((complete + 1))
    else
      emit FAST64_3_BASE_ALIAS_V3_WAIT_TERMINAL "workload=$workload namespace=$row"
    fi
  done
  [ "$complete" -eq "${#rows[@]}" ] && { emit FAST64_3_BASE_ALIAS_V3_CLOSEOUT_COMPLETE "rows=$complete"; exit 0; }
  [ "$once" = 1 ] && exit 0
  sleep "$poll"
done
