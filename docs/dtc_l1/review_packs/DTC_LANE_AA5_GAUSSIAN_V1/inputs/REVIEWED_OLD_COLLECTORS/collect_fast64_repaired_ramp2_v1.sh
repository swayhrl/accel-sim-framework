#!/usr/bin/env bash
# Terminal-only closeout for the second repaired-Core FAST64 ramp.
# Default mode is read-only; --collect may parse only immutable terminal rows.
set -euo pipefail

case "${1:-}" in
  '') collect=no ;;
  --collect) collect=yes ;;
  *) echo "usage: $0 [--collect]" >&2; exit 2 ;;
esac

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
collector="$repo/util/dtc_l1/monitor_fast64_repaired_core_row_v2.sh"
root=/workspace/fast64-repaired-ramp2
out_root="$repo/docs/dtc_l1/fast64/generated/fast64_repaired_ramp2_v1"
core=95ccdb7a056f2d53f740d90869785cac6d4ee0f5
runtime=462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9
classification=PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE
test -x "$collector" && test -d "$root"
mkdir -p "$out_root"

# workload|mode|config-id|config-file|namespace
rows=(
  "BICG|BASE|FAST64_BASE_A1|$repo/configs/dtc_l1/fast64/FAST64_BASE.config|fast64_bicg_base_core95ccdb7a_a1_r1"
  "BICG|IO|FAST64_IO_A1|$repo/configs/dtc_l1/fast64/FAST64_IO.config|fast64_bicg_io_core95ccdb7a_a1_r1"
  "BICG|OO|FAST64_OO_A1|$repo/configs/dtc_l1/fast64/FAST64_OO.config|fast64_bicg_oo_core95ccdb7a_a1_r1"
  "GESUMMV|BASE|FAST64_BASE_A1|$repo/configs/dtc_l1/fast64/FAST64_BASE.config|fast64_gesummv_base_core95ccdb7a_a1_r1"
)

printf 'schema\tFAST64_REPAIRED_RAMP2_CLOSEOUT_V1\ncollect\t%s\n' "$collect"
for row in "${rows[@]}"; do
  IFS='|' read -r workload mode config_id config name <<<"$row"
  run="$root/$name"; out="$out_root/$name.json"
  if test -e "$out"; then
    printf 'ROW\t%s\t%s\tEXISTS\t%s\n' "$workload" "$mode" "$out"; continue
  fi
  if ! test -f "$run/RUN_TERMINAL.tsv"; then
    printf 'ROW\t%s\t%s\tWAIT_TERMINAL\t%s\n' "$workload" "$mode" "$run"; continue
  fi
  if test "$collect" = no; then
    printf 'ROW\t%s\t%s\tTERMINAL_PENDING_COLLECT\t%s\n' "$workload" "$mode" "$run"; continue
  fi
  printf 'ROW\t%s\t%s\tCOLLECT\t%s\n' "$workload" "$mode" "$run"
  "$collector" --run-dir "$run" --workload-id "$workload" --mode "$mode" \
    --config-id "$config_id" --config-file "$config" --core-sha "$core" \
    --runtime-sha "$runtime" --classification "$classification" --output "$out" \
    --log "$run/repaired_ramp2_closeout_v1.log" --poll-seconds 1
done
