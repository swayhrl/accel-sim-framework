#!/usr/bin/env bash
# Future-only strict/structural closeout for the isolated Core-658 2D Base row.
set -euo pipefail
test "${1:-}" = --collect && test "$#" -eq 1 || {
  echo "usage: $0 --collect" >&2
  exit 2
}

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
run=/workspace/fast64-stage3-tag-identity-repair-v2/fast64_3_2DConvolution_base_core6587238c_a1_v1
output_dir="$repo/docs/dtc_l1/fast64/generated/fast64_3_tag_identity_repair_v2"
summary="$output_dir/fast64_3_2DConvolution_base_core6587238c_a1_v1.json"
structural="$output_dir/FAST64_3_2DCONVOLUTION_BASE_STRUCTURAL_METRICS_V1.json"
config="$repo/configs/dtc_l1/fast64/FAST64_BASE.config"
validator="$repo/util/dtc_l1/validate_fast64_trace_row_alias_v3.py"
extractor="$repo/util/dtc_l1/extract_fast64_3_base_structural_metrics_v1.py"
payload="$repo/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
core=6587238c60214d99491f4048e28ce8a3458c1509
runtime=29a3dd9f57a5accb89822ca3fcf06b11c437bfe864ee43d2ff5f26c8c056f3c1
framework=037f008b330eb230353b60edf126d6be9f45afdc
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e

test -d "$run" && test -r "$config" && test -r "$validator" && test -r "$extractor" && test -r "$payload"
test ! -e "$summary" && test ! -e "$structural" || { echo FAST64_3_2D_TAG_IDENTITY_OUTPUT_EXISTS >&2; exit 1; }
test -f "$run/RUN_TERMINAL.tsv" || { echo FAST64_3_2D_TAG_IDENTITY_WAIT_TERMINAL; exit 0; }
value() { awk -F '\t' -v key="$2" '$1==key {n++;v=$2} END {if(n==1) print v; else exit 1}' "$1"; }
test "$(value "$run/RUN_TERMINAL.tsv" simulator_exit_status)" = 0 || { echo FAST64_3_2D_TAG_IDENTITY_NONZERO_TERMINAL >&2; exit 1; }
mapfile -t perf_files < <(find "$run" -maxdepth 1 -type f -name 'perf_counter_*.csv.gz' -print | sort)
test "${#perf_files[@]}" -eq 1 || { echo FAST64_3_2D_TAG_IDENTITY_EXPECTED_ONE_PERF_CSV >&2; exit 1; }
mkdir -p "$output_dir"
exec 9>"$output_dir/.fast64_3_2d_tag_identity_v2_collect.lock"
flock -n 9 || { echo FAST64_3_2D_TAG_IDENTITY_COLLECTOR_ALREADY_ACTIVE >&2; exit 1; }
temporary_summary=$(mktemp "$output_dir/.${summary##*/}.tmp.XXXXXX")
temporary_structural=$(mktemp "$output_dir/.${structural##*/}.tmp.XXXXXX")
trap 'rm -f -- "$temporary_summary" "$temporary_structural"' EXIT
python3 "$validator" --run-dir "$run" --workload-id 2DConvolution --mode BASE \
  --config-id FAST64_BASE_A1 --config-file "$config" --core-sha "$core" \
  --framework-sha "$framework" --observer-sha "$observer" --runtime-sha "$runtime" \
  --payload-manifest "$payload" --classification PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE \
  --require-immutable-attempt --output "$temporary_summary"
if rg -n -i 'assertion failed|fatal error|deadlock detected|output mismatch|checker.*fail|segmentation fault|core dumped' \
  "$run/simulator.stdout" "$run/simulator.stderr" "$run.launcher.log"; then
  echo FAST64_3_2D_TAG_IDENTITY_FORBIDDEN_FAILURE_SIGNATURE >&2
  exit 1
fi
python3 "$extractor" --summary "$temporary_summary" --perf "${perf_files[0]}" --output "$temporary_structural"
chmod 444 "$temporary_summary" "$temporary_structural"
mv -n -- "$temporary_summary" "$summary"
mv -n -- "$temporary_structural" "$structural"
test -f "$summary" && test -f "$structural" || { echo FAST64_3_2D_TAG_IDENTITY_ATOMIC_PUBLISH_FAILED >&2; exit 1; }
trap - EXIT
printf 'FAST64_3_2D_TAG_IDENTITY_COLLECTOR_PASS\tsummary=%s\tstructural=%s\n' "$summary" "$structural"
