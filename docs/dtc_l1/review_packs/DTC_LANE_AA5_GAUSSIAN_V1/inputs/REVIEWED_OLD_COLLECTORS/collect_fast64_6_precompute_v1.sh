#!/usr/bin/env bash
# Future-only terminal collector for the FAST64.6 physical-precompute wave.
# It never launches, signals, or otherwise touches a simulator.  A compact
# record is published only after its immutable terminal receipt is present and
# the generic strict validator succeeds in a temporary output followed by an
# atomic rename.
set -euo pipefail

usage() {
  echo "usage: $0 --collect|--dry-run" >&2
  exit 2
}

test "$#" -eq 1 || usage
case "$1" in
  --collect) collect=1 ;;
  --dry-run) collect=0 ;;
  *) usage ;;
esac

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs=/workspace/fast64-sensitivity-v1
output_root="$repo/docs/dtc_l1/fast64/generated/fast64_6_precomputed_v1"
# The immutable runner maintains a compatibility symlink
# `perf_counter.csv.gz` beside the one timestamped stream.  Alias-v3 verifies
# that this is exactly that symlink before delegating to the frozen validator.
validator="$repo/util/dtc_l1/validate_fast64_trace_row_alias_v3.py"
payload="$repo/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
core=95ccdb7a056f2d53f740d90869785cac6d4ee0f5
runtime=462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
scientific=037f008b330eb230353b60edf126d6be9f45afdc
classification=PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE

test -r "$validator" && test -r "$payload"

# name|workload|mode|repo-relative config|stable config id
rows=(
  'fast64_sens_v1_bicg_physical16p5_io|BICG|IO|configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_16.5/FAST64_SENS_PHYSICAL_16p5KB_IO.config|FAST64_SENS_PHYSICAL_16p5KB_IO'
  'fast64_sens_v1_bicg_physical16p5_oo|BICG|OO|configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_16.5/FAST64_SENS_PHYSICAL_16p5KB_OO.config|FAST64_SENS_PHYSICAL_16p5KB_OO'
  'fast64_sens_v1_gesummv_physical16p5_io|GESUMMV|IO|configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_16.5/FAST64_SENS_PHYSICAL_16p5KB_IO.config|FAST64_SENS_PHYSICAL_16p5KB_IO'
  'fast64_sens_v1_gesummv_physical16p5_oo|GESUMMV|OO|configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_16.5/FAST64_SENS_PHYSICAL_16p5KB_OO.config|FAST64_SENS_PHYSICAL_16p5KB_OO'
  'fast64_sens_v1_btree_physical16p5_io|Btree|IO|configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_16.5/FAST64_SENS_PHYSICAL_16p5KB_IO.config|FAST64_SENS_PHYSICAL_16p5KB_IO'
  'fast64_sens_v1_btree_physical16p5_oo|Btree|OO|configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_16.5/FAST64_SENS_PHYSICAL_16p5KB_OO.config|FAST64_SENS_PHYSICAL_16p5KB_OO'
  'fast64_sens_v1_bicg_physical24_io|BICG|IO|configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_24/FAST64_SENS_PHYSICAL_24KB_IO.config|FAST64_SENS_PHYSICAL_24KB_IO'
  'fast64_sens_v1_bicg_physical24_oo|BICG|OO|configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_24/FAST64_SENS_PHYSICAL_24KB_OO.config|FAST64_SENS_PHYSICAL_24KB_OO'
  'fast64_sens_v1_gesummv_physical24_io|GESUMMV|IO|configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_24/FAST64_SENS_PHYSICAL_24KB_IO.config|FAST64_SENS_PHYSICAL_24KB_IO'
  'fast64_sens_v1_gesummv_physical24_oo|GESUMMV|OO|configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_24/FAST64_SENS_PHYSICAL_24KB_OO.config|FAST64_SENS_PHYSICAL_24KB_OO'
)

waiting=0
published=0
failed=0
for row in "${rows[@]}"; do
  IFS='|' read -r name workload mode config_rel config_id <<<"$row"
  run="$runs/$name"
  output="$output_root/$name.json"
  config="$repo/$config_rel"
  if test -e "$output"; then
    printf 'FAST64_6_COLLECT_SKIP_PRESENT\trow=%s\n' "$name"
    continue
  fi
  if ! test -f "$run/RUN_TERMINAL.tsv"; then
    printf 'FAST64_6_COLLECT_WAIT_TERMINAL\trow=%s\n' "$name"
    waiting=$((waiting + 1))
    continue
  fi
  if test "$collect" -eq 0; then
    printf 'FAST64_6_COLLECT_DRY_TERMINAL\trow=%s\n' "$name"
    continue
  fi
  expected_config_sha=$(awk -F '\t' '$1 == "config_sha256" {print $2; exit}' "$run/RUN_MANIFEST.tsv")
  if test -z "$expected_config_sha" || test "$(sha256sum "$config" | awk '{print $1}')" != "$expected_config_sha"; then
    printf 'FAST64_6_COLLECT_CONFIG_HASH_FAIL\trow=%s\n' "$name" >&2
    failed=$((failed + 1))
    continue
  fi
  logs=("$run/simulator.stdout")
  for optional in "$run/simulator.stderr" "$run/launcher.log"; do
    test -f "$optional" && logs+=("$optional")
  done
  if rg -n -i 'assertion failed|fatal error|deadlock detected|output mismatch|checker.*fail|segmentation fault|core dumped' "${logs[@]}"; then
    printf 'FAST64_6_COLLECT_FORBIDDEN_SIGNATURE\trow=%s\n' "$name" >&2
    failed=$((failed + 1))
    continue
  fi
  mkdir -p "$output_root"
  tmp="$output.tmp.$$"
  test ! -e "$tmp" || { echo "FAST64_6_COLLECT_TEMP_EXISTS $tmp" >&2; exit 1; }
  if python3 "$validator" --run-dir "$run" --workload-id "$workload" --mode "$mode" \
      --config-id "$config_id" --config-file "$config" --core-sha "$core" \
      --framework-sha "$scientific" --observer-sha "$observer" --runtime-sha "$runtime" \
      --payload-manifest "$payload" --classification "$classification" \
      --require-immutable-attempt --output "$tmp"; then
    mv "$tmp" "$output"
    printf 'FAST64_6_COLLECT_PUBLISHED\trow=%s\toutput=%s\n' "$name" "$output"
    published=$((published + 1))
  else
    printf 'FAST64_6_COLLECT_VALIDATION_FAIL\trow=%s\n' "$name" >&2
    failed=$((failed + 1))
  fi
done

printf 'FAST64_6_COLLECT_SUMMARY\tpublished=%u\twaiting=%u\tfailed=%u\n' \
  "$published" "$waiting" "$failed"
test "$failed" -eq 0
