#!/usr/bin/env bash
# Future-only collector for the V6 physical-32 rows. It neither launches nor
# signals simulators and deliberately does not modify the live V3 collector.
set -euo pipefail

test "${1:-}" = --collect || { echo "usage: $0 --collect" >&2; exit 2; }
repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs=/workspace/fast64-sensitivity-v1
output_root="$repo/docs/dtc_l1/fast64/generated/fast64_6_precomputed_v4"
validator="$repo/util/dtc_l1/validate_fast64_trace_row_alias_v3.py"
payload="$repo/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
core=95ccdb7a056f2d53f740d90869785cac6d4ee0f5
runtime=462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
scientific=037f008b330eb230353b60edf126d6be9f45afdc
classification=PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE
test -r "$validator" && test -r "$payload"

rows=(
  'fast64_sens_v6_btree_physical32_io|Btree|IO|FAST64_SENS_PHYSICAL_32KB_IO|configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_32/FAST64_SENS_PHYSICAL_32KB_IO.config'
  'fast64_sens_v6_btree_physical32_oo|Btree|OO|FAST64_SENS_PHYSICAL_32KB_OO|configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_32/FAST64_SENS_PHYSICAL_32KB_OO.config'
  'fast64_sens_v6_bicg_physical32_oo|BICG|OO|FAST64_SENS_PHYSICAL_32KB_OO|configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_32/FAST64_SENS_PHYSICAL_32KB_OO.config'
)
for row in "${rows[@]}"; do
  IFS='|' read -r name workload mode config_id config_rel <<<"$row"
  run="$runs/$name"; output="$output_root/$name.json"; config="$repo/$config_rel"
  test -r "$config"
  if test -e "$output"; then printf 'FAST64_6_V4_COLLECT_SKIP_PRESENT\trow=%s\n' "$name"; continue; fi
  if ! test -f "$run/RUN_TERMINAL.tsv"; then printf 'FAST64_6_V4_COLLECT_WAIT_TERMINAL\trow=%s\n' "$name"; continue; fi
  status=$(awk -F '\t' '$1 == "simulator_exit_status" {print $2; exit}' "$run/RUN_TERMINAL.tsv")
  if test "$status" != 0; then printf 'FAST64_6_V4_COLLECT_TERMINAL_NONZERO\trow=%s\tstatus=%s\n' "$name" "$status" >&2; continue; fi
  logs=("$run/simulator.stdout"); for optional in "$run/simulator.stderr" "$run/launcher.log"; do test -f "$optional" && logs+=("$optional"); done
  if rg -n -i 'assertion failed|fatal error|deadlock detected|output mismatch|checker.*fail|segmentation fault|core dumped' "${logs[@]}"; then printf 'FAST64_6_V4_COLLECT_FORBIDDEN_SIGNATURE\trow=%s\n' "$name" >&2; continue; fi
  expected=$(awk -F '\t' '$1 == "config_sha256" {print $2; exit}' "$run/RUN_MANIFEST.tsv")
  if test -z "$expected" || test "$(sha256sum "$config" | awk '{print $1}')" != "$expected"; then printf 'FAST64_6_V4_COLLECT_CONFIG_HASH_FAIL\trow=%s\n' "$name" >&2; continue; fi
  mkdir -p "$output_root"; tmp="$output.tmp.$$"; test ! -e "$tmp"
  python3 "$validator" --run-dir "$run" --workload-id "$workload" --mode "$mode" --config-id "$config_id" --config-file "$config" --core-sha "$core" --framework-sha "$scientific" --observer-sha "$observer" --runtime-sha "$runtime" --payload-manifest "$payload" --classification "$classification" --require-immutable-attempt --output "$tmp"
  test ! -e "$output"; mv -n "$tmp" "$output"; test -f "$output" && test ! -e "$tmp"
  printf 'FAST64_6_V4_COLLECT_PUBLISHED\trow=%s\toutput=%s\n' "$name" "$output"
done
