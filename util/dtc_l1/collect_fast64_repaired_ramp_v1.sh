#!/usr/bin/env bash
# Terminal-only closeout for the first repaired-Core FAST64 ramp.
# It never launches, signals, or changes a simulator.  Without --collect it
# is a read-only status audit; with --collect it invokes the versioned strict
# collector only after an immutable terminal receipt exists.
set -euo pipefail

usage() {
  echo "usage: $0 [--collect]" >&2
  exit 2
}

collect=no
case "${1:-}" in
  '') ;;
  --collect) collect=yes ;;
  *) usage ;;
esac

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
collector="$repo/util/dtc_l1/monitor_fast64_repaired_core_row_v2.sh"
root=/workspace/fast64-repaired-ramp
out_root="$repo/docs/dtc_l1/fast64/generated/fast64_repaired_ramp_v1"
core=95ccdb7a056f2d53f740d90869785cac6d4ee0f5
runtime=462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9
classification=PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE

test -x "$collector" && test -d "$root"
mkdir -p "$out_root"

# workload|mode|config-id|config-file|namespace
rows=(
  "Btree|BASE|FAST64_BASE_A1|$repo/configs/dtc_l1/fast64/FAST64_BASE.config|fast64_btree_base_core95ccdb7a_a1_r1"
  "Btree|IO|FAST64_IO_A1|$repo/configs/dtc_l1/fast64/FAST64_IO.config|fast64_btree_io_core95ccdb7a_a1_r1"
  "Btree|OO|FAST64_OO_A1|$repo/configs/dtc_l1/fast64/FAST64_OO.config|fast64_btree_oo_core95ccdb7a_a1_r1"
  "MRI-Q|BASE|FAST64_BASE_A1|$repo/configs/dtc_l1/fast64/FAST64_BASE.config|fast64_mriq_base_core95ccdb7a_a1_r1"
  "MRI-Q|IO|FAST64_IO_A1|$repo/configs/dtc_l1/fast64/FAST64_IO.config|fast64_mriq_io_core95ccdb7a_a1_r1"
  "MRI-Q|OO|FAST64_OO_A1|$repo/configs/dtc_l1/fast64/FAST64_OO.config|fast64_mriq_oo_core95ccdb7a_a1_r1"
  "ATAX|OO|FAST64_OO_A1|$repo/configs/dtc_l1/fast64/FAST64_OO.config|fast64_atax_oo_core95ccdb7a_a1_r1"
  "GESUMMV|OO|FAST64_OO_A1|$repo/configs/dtc_l1/fast64/FAST64_OO.config|fast64_gesummv_oo_core95ccdb7a_a1_r1"
)

printf 'schema\tFAST64_REPAIRED_RAMP_CLOSEOUT_V1\n'
printf 'collect\t%s\n' "$collect"
for row in "${rows[@]}"; do
  IFS='|' read -r workload mode config_id config name <<<"$row"
  run="$root/$name"
  out="$out_root/$name.json"
  if test -e "$out"; then
    printf 'ROW\t%s\t%s\tEXISTS\t%s\n' "$workload" "$mode" "$out"
    continue
  fi
  if ! test -f "$run/RUN_TERMINAL.tsv"; then
    printf 'ROW\t%s\t%s\tWAIT_TERMINAL\t%s\n' "$workload" "$mode" "$run"
    continue
  fi
  if test "$collect" = no; then
    printf 'ROW\t%s\t%s\tTERMINAL_PENDING_COLLECT\t%s\n' "$workload" "$mode" "$run"
    continue
  fi
  printf 'ROW\t%s\t%s\tCOLLECT\t%s\n' "$workload" "$mode" "$run"
  "$collector" --run-dir "$run" --workload-id "$workload" --mode "$mode" \
    --config-id "$config_id" --config-file "$config" --core-sha "$core" \
    --runtime-sha "$runtime" --classification "$classification" --output "$out" \
    --log "$run/repaired_ramp_closeout_v1.log" --poll-seconds 1
done
