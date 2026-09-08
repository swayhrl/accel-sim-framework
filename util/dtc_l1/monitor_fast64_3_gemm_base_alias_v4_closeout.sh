#!/usr/bin/env bash
# Future-only monitor for the GEMM/Base row.  It cannot operate on R2 or v3.
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
row=fast64_3_precomputed_gemm_base_cap8192_a1_r2
run="$runs/$row"
evidence="$repo/docs/dtc_l1/fast64/generated/fast64_3_gemm_base_alias_v4/FAST64_3_GEMM_BASE_ALIAS_V4.tsv"
exec 9>"$runs/.fast64_3_gemm_base_alias_v4_closeout.lock"
flock -n 9 || { echo FAST64_3_GEMM_BASE_ALIAS_V4_MONITOR_ALREADY_ACTIVE >&2; exit 1; }
emit() { printf '%s\tutc=%s\t%s\n' "$1" "$(date -u +%FT%TZ)" "$2" | tee -a "$log"; }

while :; do
  if test -f "$evidence"; then
    emit FAST64_3_GEMM_BASE_ALIAS_V4_CLOSEOUT_COMPLETE "namespace=$row"
    exit 0
  fi
  if test -f "$run/RUN_TERMINAL.tsv"; then
    emit FAST64_3_GEMM_BASE_ALIAS_V4_TERMINAL_OBSERVED "namespace=$row"
    "$repo/util/dtc_l1/collect_fast64_3_gemm_base_alias_v4.sh"
    test -f "$evidence" || { emit FAST64_3_GEMM_BASE_ALIAS_V4_MISSING_EVIDENCE "namespace=$row"; exit 1; }
    emit FAST64_3_GEMM_BASE_ALIAS_V4_PENDING_COLLECTED "namespace=$row"
    exit 0
  fi
  emit FAST64_3_GEMM_BASE_ALIAS_V4_WAIT_TERMINAL "namespace=$row"
  [ "$once" = 1 ] && exit 0
  sleep "$poll"
done
