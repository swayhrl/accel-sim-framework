#!/usr/bin/env bash
# Future-only closeout monitor for the BICG coupled FAST64.2 diagnostic.  It
# does not launch, signal, stop, or otherwise control a simulator; only a
# published immutable terminal receipt triggers strict collection.
set -euo pipefail

usage() { echo "usage: $0 [--log FILE] [--poll-seconds N] [--once]" >&2; exit 2; }
repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs=/workspace/fast64-runs
namespace=fast64_2_precomputed_bicg_io_coupled_cap512_pib1_a1_r2
run="$runs/$namespace"
collector="$repo/util/dtc_l1/collect_fast64_2_coupled_stress_bicg_alias_v2.sh"
evidence="$repo/docs/dtc_l1/fast64/generated/fast64_2_coupled_stress_bicg_alias_v2/FAST64_2_COUPLED_STRESS_BICG_ALIAS_V2.tsv"
log="$runs/fast64_2_bicg_coupled_closeout_v2.log"
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
exec 8>"$runs/.fast64_2_bicg_coupled_closeout_v2.lock"
flock -n 8 || { echo FAST64_2_BICG_COUPLED_CLOSEOUT_LOCK_HELD >&2; exit 1; }
emit() { printf '%s\tutc=%s\t%s\n' "$1" "$(date -u +%FT%TZ)" "$2" | tee -a "$log"; }

while :; do
  if [ -f "$evidence" ]; then
    emit FAST64_2_BICG_COUPLED_CLOSEOUT_EVIDENCE_PRESENT "namespace=$namespace"
    exit 0
  fi
  if [ -f "$run/RUN_TERMINAL.tsv" ]; then
    emit FAST64_2_BICG_COUPLED_TERMINAL_OBSERVED "namespace=$namespace"
    "$collector"
    test -f "$evidence" || { emit FAST64_2_BICG_COUPLED_COLLECTOR_MISSING_EVIDENCE "namespace=$namespace"; exit 1; }
    emit FAST64_2_BICG_COUPLED_STRICT_COLLECTED "namespace=$namespace"
    exit 0
  fi
  emit FAST64_2_BICG_COUPLED_WAIT_TERMINAL "namespace=$namespace"
  [ "$once" = 1 ] && exit 0
  sleep "$poll"
done
