#!/usr/bin/env bash
# Future-only collector for the V8 BICG physical-40 OO row.  It intentionally
# does not alter the frozen V3/V4/V5 collectors or any live simulator state.
set -euo pipefail
test "${1:-}" = --collect || { echo "usage: $0 --collect" >&2; exit 2; }
repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
run=/workspace/fast64-sensitivity-v1/fast64_sens_v8_bicg_physical40_oo
output="$repo/docs/dtc_l1/fast64/generated/fast64_6_precomputed_v6/fast64_sens_v8_bicg_physical40_oo.json"
config="$repo/configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_40/FAST64_SENS_PHYSICAL_40KB_OO.config"
validator="$repo/util/dtc_l1/validate_fast64_trace_row_alias_v3.py"
payload="$repo/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
test -r "$validator" && test -r "$payload" && test -r "$config"
if test -e "$output"; then printf 'FAST64_6_V6_COLLECT_SKIP_PRESENT\n'; exit 0; fi
if ! test -f "$run/RUN_TERMINAL.tsv"; then printf 'FAST64_6_V6_COLLECT_WAIT_TERMINAL\n'; exit 0; fi
status=$(awk -F '\t' '$1 == "simulator_exit_status" {print $2; exit}' "$run/RUN_TERMINAL.tsv")
if test "$status" != 0; then printf 'FAST64_6_V6_COLLECT_TERMINAL_NONZERO\tstatus=%s\n' "$status" >&2; exit 0; fi
logs=("$run/simulator.stdout"); for optional in "$run/simulator.stderr" "$run/launcher.log"; do test -f "$optional" && logs+=("$optional"); done
if rg -n -i 'assertion failed|fatal error|deadlock detected|output mismatch|checker.*fail|segmentation fault|core dumped' "${logs[@]}"; then printf 'FAST64_6_V6_COLLECT_FORBIDDEN_SIGNATURE\n' >&2; exit 1; fi
expected=$(awk -F '\t' '$1 == "config_sha256" {print $2; exit}' "$run/RUN_MANIFEST.tsv")
test -n "$expected" && test "$(sha256sum "$config" | awk '{print $1}')" = "$expected" || { echo FAST64_6_V6_COLLECT_CONFIG_HASH_FAIL >&2; exit 1; }
mkdir -p "$(dirname "$output")"; tmp="$output.tmp.$$"; test ! -e "$tmp"
python3 "$validator" --run-dir "$run" --workload-id BICG --mode OO --config-id FAST64_SENS_PHYSICAL_40KB_OO --config-file "$config" --core-sha 95ccdb7a056f2d53f740d90869785cac6d4ee0f5 --framework-sha 037f008b330eb230353b60edf126d6be9f45afdc --observer-sha 2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e --runtime-sha 462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9 --payload-manifest "$payload" --classification PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE --require-immutable-attempt --output "$tmp"
test ! -e "$output"; mv -n "$tmp" "$output"; test -f "$output" && test ! -e "$tmp"
printf 'FAST64_6_V6_COLLECT_PUBLISHED\toutput=%s\n' "$output"
