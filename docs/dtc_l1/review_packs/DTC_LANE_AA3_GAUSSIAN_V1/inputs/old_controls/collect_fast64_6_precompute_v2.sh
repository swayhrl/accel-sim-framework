#!/usr/bin/env bash
# Future-only strict collector for the post-v1 Btree/24-KiB/IO precompute.
# It is deliberately separate from the live v1 collector.  It never launches,
# signals, pauses, or otherwise interacts with the simulator process tree.
set -euo pipefail

case "${1:-}" in
  --collect) collect=1 ;;
  --dry-run) collect=0 ;;
  *) echo "usage: $0 --collect|--dry-run" >&2; exit 2 ;;
esac

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
name=fast64_sens_v1_btree_physical24_io
workload=Btree
mode=IO
config_rel=configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_24/FAST64_SENS_PHYSICAL_24KB_IO.config
config_id=FAST64_SENS_PHYSICAL_24KB_IO
run=/workspace/fast64-sensitivity-v1/$name
output_root="$repo/docs/dtc_l1/fast64/generated/fast64_6_precomputed_v1"
output="$output_root/$name.json"
config="$repo/$config_rel"
validator="$repo/util/dtc_l1/validate_fast64_trace_row_alias_v3.py"
payload="$repo/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
core=95ccdb7a056f2d53f740d90869785cac6d4ee0f5
runtime=462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
scientific=037f008b330eb230353b60edf126d6be9f45afdc
classification=PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE

test -r "$validator" && test -r "$payload" && test -r "$config"
if test -e "$output"; then
  printf 'FAST64_6_V2_COLLECT_SKIP_PRESENT\trow=%s\n' "$name"
  exit 0
fi
if ! test -f "$run/RUN_TERMINAL.tsv"; then
  printf 'FAST64_6_V2_COLLECT_WAIT_TERMINAL\trow=%s\n' "$name"
  exit 0
fi
if test "$collect" -eq 0; then
  printf 'FAST64_6_V2_COLLECT_DRY_TERMINAL\trow=%s\n' "$name"
  exit 0
fi
expected_config_sha=$(awk -F '\t' '$1 == "config_sha256" {print $2; exit}' "$run/RUN_MANIFEST.tsv")
if test -z "$expected_config_sha" || test "$(sha256sum "$config" | awk '{print $1}')" != "$expected_config_sha"; then
  printf 'FAST64_6_V2_COLLECT_CONFIG_HASH_FAIL\trow=%s\n' "$name" >&2
  exit 1
fi
logs=("$run/simulator.stdout")
for optional in "$run/simulator.stderr" "$run/launcher.log"; do
  test -f "$optional" && logs+=("$optional")
done
if rg -n -i 'assertion failed|fatal error|deadlock detected|output mismatch|checker.*fail|segmentation fault|core dumped' "${logs[@]}"; then
  printf 'FAST64_6_V2_COLLECT_FORBIDDEN_SIGNATURE\trow=%s\n' "$name" >&2
  exit 1
fi
mkdir -p "$output_root"
tmp="$output.tmp.$$"
test ! -e "$tmp" || { echo "FAST64_6_V2_COLLECT_TEMP_EXISTS $tmp" >&2; exit 1; }
python3 "$validator" --run-dir "$run" --workload-id "$workload" --mode "$mode" \
  --config-id "$config_id" --config-file "$config" --core-sha "$core" \
  --framework-sha "$scientific" --observer-sha "$observer" --runtime-sha "$runtime" \
  --payload-manifest "$payload" --classification "$classification" \
  --require-immutable-attempt --output "$tmp"
mv "$tmp" "$output"
printf 'FAST64_6_V2_COLLECT_PUBLISHED\trow=%s\toutput=%s\n' "$name" "$output"
