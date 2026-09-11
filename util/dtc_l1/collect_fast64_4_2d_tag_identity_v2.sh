#!/usr/bin/env bash
# Future-only strict collector for a Core-658 2DConvolution IO or OO row.
set -euo pipefail
test "${1:-}" = --collect || { echo "usage: $0 --collect --mode IO|OO" >&2; exit 2; }
shift
test "${1:-}" = --mode && test "$#" -eq 2 || { echo "usage: $0 --collect --mode IO|OO" >&2; exit 2; }
mode=$2
case "$mode" in IO|OO) ;; *) echo MODE_REQUIRED >&2; exit 2 ;; esac

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
lower=${mode,,}
row="fast64_4_primary_2DConvolution_${lower}_core6587238c_a1_v1"
run=/workspace/fast64-primary-r4-tag-identity-v2/$row
output_dir="$repo/docs/dtc_l1/fast64/generated/fast64_4_2d_tag_identity_v2"
output="$output_dir/$row.json"
validator="$repo/util/dtc_l1/validate_fast64_trace_row_alias_v3.py"
payload="$repo/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
core=6587238c60214d99491f4048e28ce8a3458c1509
runtime=29a3dd9f57a5accb89822ca3fcf06b11c437bfe864ee43d2ff5f26c8c056f3c1
framework=037f008b330eb230353b60edf126d6be9f45afdc
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
case "$mode" in
  IO) config="$repo/configs/dtc_l1/fast64/FAST64_IO.config"; config_id=FAST64_IO_A1 ;;
  OO) config="$repo/configs/dtc_l1/fast64/FAST64_OO.config"; config_id=FAST64_OO_A1 ;;
esac
test -d "$run" && test -r "$config" && test -r "$validator" && test -r "$payload"
test ! -e "$output" || { echo OUTPUT_EXISTS >&2; exit 1; }
test -f "$run/RUN_TERMINAL.tsv" || { echo FAST64_4_2D_TAG_IDENTITY_WAIT_TERMINAL; exit 0; }
status=$(awk -F '\t' '$1=="simulator_exit_status" {n++;v=$2} END {if(n==1) print v; else exit 1}' "$run/RUN_TERMINAL.tsv")
test "$status" = 0 || { echo FAST64_4_2D_TAG_IDENTITY_NONZERO_TERMINAL >&2; exit 1; }
mkdir -p "$output_dir"
exec 9>"$output_dir/.${row}.lock"
flock -n 9 || { echo COLLECTOR_ALREADY_ACTIVE >&2; exit 1; }
tmp=$(mktemp "$output_dir/.${row}.tmp.XXXXXX")
trap 'rm -f -- "$tmp"' EXIT
python3 "$validator" --run-dir "$run" --workload-id 2DConvolution --mode "$mode" --config-id "$config_id" \
  --config-file "$config" --core-sha "$core" --framework-sha "$framework" --observer-sha "$observer" \
  --runtime-sha "$runtime" --payload-manifest "$payload" --classification PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE \
  --require-immutable-attempt --output "$tmp"
if rg -n -i 'assertion failed|fatal error|deadlock detected|output mismatch|checker.*fail|segmentation fault|core dumped' \
    "$run/simulator.stdout" "$run/simulator.stderr" "$run.launcher.log"; then
  echo FORBIDDEN_FAILURE_SIGNATURE >&2
  exit 1
fi
chmod 444 "$tmp"
mv -n -- "$tmp" "$output"
test -f "$output" || { echo ATOMIC_PUBLISH_FAILED >&2; exit 1; }
trap - EXIT
printf 'FAST64_4_2D_TAG_IDENTITY_COLLECTOR_PASS\tmode=%s\toutput=%s\n' "$mode" "$output"
