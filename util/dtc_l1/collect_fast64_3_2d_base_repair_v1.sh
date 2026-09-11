#!/usr/bin/env bash
# Future-only strict closeout for the formal Core-41 2DConvolution Base retry.
set -euo pipefail
test "${1:-}" = --collect && test "$#" -eq 1 || { echo "usage: $0 --collect" >&2; exit 2; }

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
run=/workspace/fast64-stage3-repair/fast64_3_2DConvolution_base_core41d740e8_a1_v1
output="$repo/docs/dtc_l1/fast64/generated/fast64_3_repair_v1/fast64_3_2DConvolution_base_core41d740e8_a1_v1.json"
config="$repo/configs/dtc_l1/fast64/FAST64_BASE.config"
validator="$repo/util/dtc_l1/validate_fast64_trace_row_alias_v3.py"
payload="$repo/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"

test -d "$run" && test -r "$config" && test -r "$validator" && test -r "$payload"
test ! -e "$output" || { echo "FAST64_3_2D_REPAIR_OUTPUT_EXISTS $output" >&2; exit 1; }
mkdir -p "$(dirname "$output")"
exec 9>"${output}.lock"
flock -n 9 || { echo FAST64_3_2D_REPAIR_MONITOR_ALREADY_ACTIVE >&2; exit 1; }
test -f "$run/RUN_TERMINAL.tsv" || { echo FAST64_3_2D_REPAIR_WAIT_TERMINAL; exit 0; }
value() { awk -F '\t' -v key="$2" '$1==key {n++;v=$2} END {if(n==1) print v; else exit 1}' "$1"; }
test "$(value "$run/RUN_TERMINAL.tsv" simulator_exit_status)" = 0 || { echo FAST64_3_2D_REPAIR_NONZERO_TERMINAL >&2; exit 1; }
temporary=$(mktemp "$(dirname "$output")/.${output##*/}.tmp.XXXXXX")
trap 'rm -f -- "$temporary"' EXIT
python3 "$validator" --run-dir "$run" --workload-id 2DConvolution --mode BASE \
  --config-id FAST64_BASE_A1 --config-file "$config" \
  --core-sha 41d740e862a6ad89ab0fc32b7b927ec787752862 \
  --framework-sha 037f008b330eb230353b60edf126d6be9f45afdc \
  --observer-sha 2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e \
  --runtime-sha 6e72d36665cde18e2845914ee9c2a9f2e65b37b7b3c216edf4b676ad17e2c21c \
  --payload-manifest "$payload" --classification PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE \
  --require-immutable-attempt --output "$temporary"
if rg -n -i 'assertion failed|fatal error|deadlock detected|output mismatch|checker.*fail|segmentation fault|core dumped' \
    "$run/simulator.stdout" "$run/simulator.stderr" "$run.launcher.log"; then
  echo FAST64_3_2D_REPAIR_FORBIDDEN_FAILURE_SIGNATURE >&2
  exit 1
fi
chmod 444 "$temporary"
mv -n -- "$temporary" "$output"
test -f "$output" || { echo FAST64_3_2D_REPAIR_ATOMIC_PUBLISH_FAILED >&2; exit 1; }
trap - EXIT
printf 'FAST64_3_2D_REPAIR_COLLECTOR_PASS\toutput=%s\n' "$output"
