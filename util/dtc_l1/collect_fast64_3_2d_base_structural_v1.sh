#!/usr/bin/env bash
# Future-only structural companion closeout for the Core-41 2DConvolution
# Base replacement. This is deliberately downstream of the live strict
# collector: it reads only a published immutable summary and terminal perf
# CSV, and has no authority to alter the run, summary, registry, or stage.
set -euo pipefail

test "${1:-}" = --collect && test "$#" -eq 1 || {
  echo "usage: $0 --collect" >&2
  exit 2
}

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
run=/workspace/fast64-stage3-repair/fast64_3_2DConvolution_base_core41d740e8_a1_v1
summary="$repo/docs/dtc_l1/fast64/generated/fast64_3_repair_v1/fast64_3_2DConvolution_base_core41d740e8_a1_v1.json"
output="$repo/docs/dtc_l1/fast64/generated/fast64_3_repair_v1/FAST64_3_2DCONVOLUTION_BASE_STRUCTURAL_METRICS_V1.json"
extractor="$repo/util/dtc_l1/extract_fast64_3_base_structural_metrics_v1.py"

test -d "$run" && test -r "$extractor"
test ! -e "$output" || {
  echo "FAST64_3_2D_STRUCTURAL_OUTPUT_EXISTS $output" >&2
  exit 1
}
mkdir -p "$(dirname "$output")"
exec 9>"${output}.lock"
flock -n 9 || {
  echo FAST64_3_2D_STRUCTURAL_MONITOR_ALREADY_ACTIVE >&2
  exit 1
}

test -f "$run/RUN_TERMINAL.tsv" || {
  echo FAST64_3_2D_STRUCTURAL_WAIT_TERMINAL
  exit 0
}
test -f "$summary" || {
  echo FAST64_3_2D_STRUCTURAL_WAIT_STRICT_SUMMARY
  exit 0
}
status=$(awk -F '\t' '$1 == "simulator_exit_status" {n++; value=$2} END {if (n == 1) print value; else exit 1}' "$run/RUN_TERMINAL.tsv")
test "$status" = 0 || {
  echo FAST64_3_2D_STRUCTURAL_NONZERO_TERMINAL >&2
  exit 1
}

mapfile -t perf_files < <(find "$run" -maxdepth 1 -type f -name 'perf_counter_*.csv.gz' -print | sort)
test "${#perf_files[@]}" -eq 1 || {
  echo "FAST64_3_2D_STRUCTURAL_EXPECTED_ONE_PERF_CSV found=${#perf_files[@]}" >&2
  exit 1
}

temporary=$(mktemp "$(dirname "$output")/.${output##*/}.tmp.XXXXXX")
trap 'rm -f -- "$temporary"' EXIT
python3 "$extractor" --summary "$summary" --perf "${perf_files[0]}" --output "$temporary"
chmod 444 "$temporary"
mv -n -- "$temporary" "$output"
test -f "$output" || {
  echo FAST64_3_2D_STRUCTURAL_ATOMIC_PUBLISH_FAILED >&2
  exit 1
}
trap - EXIT
printf 'FAST64_3_2D_STRUCTURAL_COLLECTOR_PASS\toutput=%s\n' "$output"
