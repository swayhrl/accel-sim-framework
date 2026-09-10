#!/usr/bin/env bash
# Future-only collector for a fresh V15/V16 GESUMMV physical-48 pair.
# It does not reference or alter any currently live collector or namespace.
set -euo pipefail
test "${1:-}" = --collect || { echo "usage: $0 --collect" >&2; exit 2; }
repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
root=/workspace/fast64-sensitivity-v1
outdir="$repo/docs/dtc_l1/fast64/generated/fast64_6_precomputed_v11"
validator="$repo/util/dtc_l1/validate_fast64_trace_row_alias_v3.py"
payload="$repo/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
test -r "$validator" && test -r "$payload"

collect_one() {
  local suffix=$1 mode=$2 config=$3
  local run="$root/fast64_sens_v${suffix}_gesummv_physical48_${mode,,}"
  local output="$outdir/fast64_sens_v${suffix}_gesummv_physical48_${mode,,}.json"
  test -r "$config"
  if test -e "$output"; then printf 'FAST64_6_V11_COLLECT_SKIP_PRESENT\trow=%s\n' "$suffix"; return 0; fi
  if ! test -f "$run/RUN_TERMINAL.tsv"; then printf 'FAST64_6_V11_COLLECT_WAIT_TERMINAL\trow=%s\n' "$suffix"; return 0; fi
  local status
  status=$(awk -F '\t' '$1 == "simulator_exit_status" {print $2; exit}' "$run/RUN_TERMINAL.tsv")
  if test "$status" != 0; then printf 'FAST64_6_V11_COLLECT_TERMINAL_NONZERO\trow=%s\tstatus=%s\n' "$suffix" "$status" >&2; return 0; fi
  local logs=("$run/simulator.stdout") optional expected tmp
  for optional in "$run/simulator.stderr" "$run/launcher.log"; do test -f "$optional" && logs+=("$optional"); done
  if rg -n -i 'assertion failed|fatal error|deadlock detected|output mismatch|checker.*fail|segmentation fault|core dumped' "${logs[@]}"; then printf 'FAST64_6_V11_COLLECT_FORBIDDEN_SIGNATURE\trow=%s\n' "$suffix" >&2; return 1; fi
  expected=$(awk -F '\t' '$1 == "config_sha256" {print $2; exit}' "$run/RUN_MANIFEST.tsv")
  test -n "$expected" && test "$(sha256sum "$config" | awk '{print $1}')" = "$expected" || { printf 'FAST64_6_V11_COLLECT_CONFIG_HASH_FAIL\trow=%s\n' "$suffix" >&2; return 1; }
  mkdir -p "$outdir"; tmp="$output.tmp.$$"; test ! -e "$tmp"
  python3 "$validator" --run-dir "$run" --workload-id GESUMMV --mode "$mode" --config-id "FAST64_SENS_PHYSICAL_48KB_${mode}" --config-file "$config" --core-sha 95ccdb7a056f2d53f740d90869785cac6d4ee0f5 --framework-sha 037f008b330eb230353b60edf126d6be9f45afdc --observer-sha 2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e --runtime-sha 462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9 --payload-manifest "$payload" --classification PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE --require-immutable-attempt --output "$tmp"
  test ! -e "$output"; mv -n "$tmp" "$output"; test -f "$output" && test ! -e "$tmp"
  printf 'FAST64_6_V11_COLLECT_PUBLISHED\trow=%s\toutput=%s\n' "$suffix" "$output"
}

collect_one 15 IO "$repo/configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_48/FAST64_SENS_PHYSICAL_48KB_IO.config"
collect_one 16 OO "$repo/configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_48/FAST64_SENS_PHYSICAL_48KB_OO.config"
