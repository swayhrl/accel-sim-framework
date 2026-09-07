#!/usr/bin/env bash
# Wait non-invasively for the FAST64.1 qualification runs, then strict-parse
# only natural exit-0 logs and emit compact external-artifact indices.
set -euo pipefail

usage() {
  echo "usage: $0 --framework-sha SHA --runs-root PATH" >&2
  exit 2
}

framework_sha=
runs_root=
while [ "$#" -gt 0 ]; do
  case "$1" in
    --framework-sha) framework_sha=${2:-}; shift 2 ;;
    --runs-root) runs_root=${2:-}; shift 2 ;;
    *) usage ;;
  esac
done
test -n "$framework_sha" && test -n "$runs_root" || usage

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
core_sha=15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9
output_dir="$repo_root/docs/dtc_l1/fast64/generated/qualification"
mkdir -p "$output_dir"

rows=(
  'fast64_1_bicg_base_cap8192_a1|BICG|BASE|FAST64_BASE.config|FAST64_1_SMOKE'
  'fast64_1_bicg_io_cap8192_a1|BICG|IO|FAST64_IO.config|FAST64_1_NONBINDING_CAP'
  'fast64_1_bicg_oo_cap8192_a1|BICG|OO|FAST64_OO.config|FAST64_1_NONBINDING_CAP'
  'fast64_1_bicg_io_cap1048576_a1|BICG|IO_CAP1048576|FAST64_IO_CAP1048576.config|FAST64_1_NONBINDING_CAP'
  'fast64_1_bicg_oo_cap1048576_a1|BICG|OO_CAP1048576|FAST64_OO_CAP1048576.config|FAST64_1_NONBINDING_CAP'
  'fast64_1_gesummv_io_cap8192_a1|GESUMMV|IO|FAST64_IO.config|FAST64_1_NONBINDING_CAP'
  'fast64_1_gesummv_io_cap1048576_a1|GESUMMV|IO_CAP1048576|FAST64_IO_CAP1048576.config|FAST64_1_NONBINDING_CAP'
)

terminal_status() {
  awk -F '\t' '$1 == "simulator_exit_status" { print $2 }' "$1/RUN_MANIFEST.tsv" 2>/dev/null | tail -n1
}

while :; do
  all_terminal=1
  for row in "${rows[@]}"; do
    IFS='|' read -r name _ <<<"$row"
    status=$(terminal_status "$runs_root/$name")
    if [ -z "$status" ]; then
      all_terminal=0
      break
    fi
    if [ "$status" != 0 ]; then
      echo "$name terminated with nonzero status $status" >&2
      exit 1
    fi
  done
  [ "$all_terminal" = 1 ] && break
  sleep 30
done

printf 'run_id\tworkload\tmode\trun_dir\tstdout_bytes\tstdout_sha256\texit_status\n' >"$output_dir/FAST64_1_RUN_INDEX.tsv"
for row in "${rows[@]}"; do
  IFS='|' read -r name workload config_id config_file classification <<<"$row"
  run_dir="$runs_root/$name"
  log="$run_dir/simulator.stdout"
  test "$(terminal_status "$run_dir")" = 0
  rg -n 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$log" >/dev/null
  trace_list=$(awk -F '\t' '$1 == "trace_list" { print $2 }' "$run_dir/RUN_MANIFEST.tsv")
  test -r "$trace_list"
  manifest_workload=$(printf '%s' "$workload" | tr '[:upper:]' '[:lower:]')
  expected_list_sha=$(awk -F '\t' -v workload="$manifest_workload" \
    '$1 == workload { print $3; exit }' \
    "$repo_root/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv")
  test -n "$expected_list_sha"
  test "$(sha256sum "$trace_list" | awk '{print $1}')" = "$expected_list_sha"
  expected_trace_paths=$(awk -v root="$(dirname "$trace_list")" \
    '/\.traceg$/ { print root "/" $0 }' "$trace_list")
  actual_trace_paths=$(sed -n 's/^Processing kernel //p' "$log")
  test "$actual_trace_paths" = "$expected_trace_paths"
  if rg -n -i 'assertion failed|fatal error|deadlock detected|segmentation fault|core dumped' "$log" "$run_dir/simulator.stderr"; then
    echo "terminal failure signature in $name" >&2
    exit 1
  fi
  python3 "$repo_root/util/dtc_l1/parse_dtc_l1_summary.py" "$log" \
    --output "$output_dir/${name}.json" \
    --core-sha "$core_sha" --framework-sha "$framework_sha" \
    --config-id "FAST64_${config_id}_A1" \
    --config-file "$repo_root/configs/dtc_l1/fast64/$config_file" \
    --workload-id "$workload" \
    --workload-file "$repo_root/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv" \
    --resource-file "$run_dir/resource.time" \
    --result-classification "$classification" --strict
  printf '%s\t%s\t%s\t%s\t%s\t%s\t0\n' "$name" "$workload" "$config_id" "$run_dir" \
    "$(stat -c %s "$log")" "$(sha256sum "$log" | awk '{print $1}')" >>"$output_dir/FAST64_1_RUN_INDEX.tsv"
done

"$repo_root/util/dtc_l1/compare_fast64_nonbinding_cap.py" \
  --candidate "$output_dir/fast64_1_bicg_io_cap8192_a1.json" \
  --high "$output_dir/fast64_1_bicg_io_cap1048576_a1.json" \
  --output "$output_dir/FAST64_1_BICG_IO_CAP_COMPARISON.tsv"
"$repo_root/util/dtc_l1/compare_fast64_nonbinding_cap.py" \
  --candidate "$output_dir/fast64_1_bicg_oo_cap8192_a1.json" \
  --high "$output_dir/fast64_1_bicg_oo_cap1048576_a1.json" \
  --output "$output_dir/FAST64_1_BICG_OO_CAP_COMPARISON.tsv"
"$repo_root/util/dtc_l1/compare_fast64_nonbinding_cap.py" \
  --candidate "$output_dir/fast64_1_gesummv_io_cap8192_a1.json" \
  --high "$output_dir/fast64_1_gesummv_io_cap1048576_a1.json" \
  --output "$output_dir/FAST64_1_GESUMMV_IO_CAP_COMPARISON.tsv"

python3 - "$output_dir" <<'PY'
import json
import pathlib
import sys
out = pathlib.Path(sys.argv[1])
for name in (
    'fast64_1_bicg_io_cap8192_a1',
    'fast64_1_bicg_oo_cap8192_a1',
    'fast64_1_gesummv_io_cap8192_a1',
):
    metrics = json.loads((out / f'{name}.json').read_text())['metrics']
    for key in ('DTC_L1_lower_cap_full_events',):
        if metrics.get(key) != 0:
            raise SystemExit(f'{name}: {key}={metrics.get(key)!r}, expected 0')
print('FAST64_1_NONBINDING_CAP_QUALIFICATION_PASS')
PY
