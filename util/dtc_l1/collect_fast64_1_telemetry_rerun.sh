#!/usr/bin/env bash
# Non-invasive closeout for the new-Core FAST64.1 telemetry rerun.  It waits
# only for natural exit-0 rows and emits compact, strict-validated evidence.
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs_root=/workspace/fast64-runs
core_sha=bbcbb5e7565417102087bc80b14c349b4e568c05
runtime_sha=6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041
observer_sha=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
# Immutable source snapshot that dispatched the live r1 rows.  A later
# review/checkpoint commit must never become their execution identity.
framework_sha=037f008b330eb230353b60edf126d6be9f45afdc
output_dir="$repo_root/docs/dtc_l1/fast64/generated/qualification_r1"
payload_manifest="$repo_root/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
validator="$repo_root/util/dtc_l1/validate_fast64_trace_row.py"
comparator="$repo_root/util/dtc_l1/compare_fast64_nonbinding_cap.py"

rows=(
  'fast64_1r1_bicg_base_cap8192_a1|BICG|BASE|FAST64_BASE_A1|FAST64_BASE.config|FAST64_1_SMOKE'
  'fast64_1r1_bicg_io_cap8192_a1|BICG|IO|FAST64_IO_A1|FAST64_IO.config|FAST64_1_NONBINDING_CAP'
  'fast64_1r1_bicg_oo_cap8192_a1|BICG|OO|FAST64_OO_A1|FAST64_OO.config|FAST64_1_NONBINDING_CAP'
  'fast64_1r1_bicg_io_cap1048576_a1|BICG|IO|FAST64_IO_CAP1048576_A1|FAST64_IO_CAP1048576.config|FAST64_1_NONBINDING_CAP'
  'fast64_1r1_bicg_oo_cap1048576_a1|BICG|OO|FAST64_OO_CAP1048576_A1|FAST64_OO_CAP1048576.config|FAST64_1_NONBINDING_CAP'
  'fast64_1r1_gesummv_io_cap8192_a1|GESUMMV|IO|FAST64_IO_A1|FAST64_IO.config|FAST64_1_NONBINDING_CAP'
  'fast64_1r1_gesummv_io_cap1048576_a1|GESUMMV|IO|FAST64_IO_CAP1048576_A1|FAST64_IO_CAP1048576.config|FAST64_1_NONBINDING_CAP'
)

run_value() {
  awk -F '\t' -v key="$2" '$1 == key { value=$2 } END { print value }' "$1/RUN_MANIFEST.tsv"
}

while :; do
  pending=0
  for row in "${rows[@]}"; do
    IFS='|' read -r name _ <<<"$row"
    run_dir="$runs_root/$name"
    status=$(run_value "$run_dir" simulator_exit_status 2>/dev/null || true)
    if [ -z "$status" ]; then
      pending=1
      continue
    fi
    test "$status" = 0 || { echo "NONZERO_TERMINAL $name status=$status" >&2; exit 1; }
  done
  [ "$pending" -eq 0 ] && break
  sleep 60
done

mkdir -p "$output_dir"
printf 'run_id\tworkload\tmode\trun_dir\tstdout_bytes\tstdout_sha256\texit_status\n' \
  >"$output_dir/FAST64_1_R1_RUN_INDEX.tsv"
for row in "${rows[@]}"; do
  IFS='|' read -r name workload mode config_id config_file classification <<<"$row"
  run_dir="$runs_root/$name"
  manifest_runtime=$(run_value "$run_dir" simulator_sha256)
  test "$manifest_runtime" = "$runtime_sha" || {
    echo "RUNTIME_IDENTITY_MISMATCH $name $manifest_runtime" >&2
    exit 1
  }
  test "$(run_value "$run_dir" core_source_head)" = "$core_sha" || {
    echo "CORE_SOURCE_IDENTITY_MISMATCH $name" >&2
    exit 1
  }
  test "$(run_value "$run_dir" observer_overlay_sha256)" = "$observer_sha" || {
    echo "OBSERVER_IDENTITY_MISMATCH $name" >&2
    exit 1
  }
  row_framework_sha=$(run_value "$run_dir" framework_source_head)
  test "$row_framework_sha" = "$framework_sha" || {
    echo "FRAMEWORK_SOURCE_IDENTITY_MISMATCH $name $row_framework_sha" >&2
    exit 1
  }
  test "$(run_value "$run_dir" config_sha256)" = "$(sha256sum "$repo_root/configs/dtc_l1/fast64/$config_file" | awk '{print $1}')" || {
    echo "CONFIG_IDENTITY_MISMATCH $name" >&2
    exit 1
  }
  "$validator" --run-dir "$run_dir" --workload-id "$workload" --mode "$mode" \
    --config-id "$config_id" --config-file "$repo_root/configs/dtc_l1/fast64/$config_file" \
    --core-sha "$core_sha" --framework-sha "$framework_sha" \
    --payload-manifest "$payload_manifest" --classification "$classification" \
    --output "$output_dir/$name.json"
  stdout="$run_dir/simulator.stdout"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t0\n' "$name" "$workload" "$mode" "$run_dir" \
    "$(stat -c %s "$stdout")" "$(sha256sum "$stdout" | awk '{print $1}')" \
    >>"$output_dir/FAST64_1_R1_RUN_INDEX.tsv"
done

"$comparator" --candidate "$output_dir/fast64_1r1_bicg_io_cap8192_a1.json" \
  --high "$output_dir/fast64_1r1_bicg_io_cap1048576_a1.json" \
  --output "$output_dir/FAST64_1_R1_BICG_IO_CAP_COMPARISON.tsv"
"$comparator" --candidate "$output_dir/fast64_1r1_bicg_oo_cap8192_a1.json" \
  --high "$output_dir/fast64_1r1_bicg_oo_cap1048576_a1.json" \
  --output "$output_dir/FAST64_1_R1_BICG_OO_CAP_COMPARISON.tsv"
"$comparator" --candidate "$output_dir/fast64_1r1_gesummv_io_cap8192_a1.json" \
  --high "$output_dir/fast64_1r1_gesummv_io_cap1048576_a1.json" \
  --output "$output_dir/FAST64_1_R1_GESUMMV_IO_CAP_COMPARISON.tsv"

python3 - "$output_dir" <<'PY'
import json
import pathlib
import sys

out = pathlib.Path(sys.argv[1])
for name in (
    'fast64_1r1_bicg_base_cap8192_a1',
    'fast64_1r1_bicg_io_cap8192_a1',
    'fast64_1r1_bicg_oo_cap8192_a1',
    'fast64_1r1_gesummv_io_cap8192_a1',
):
    metrics = json.loads((out / f'{name}.json').read_text())['metrics']
    if metrics.get('DTC_L1_lower_cap_full_events') != 0:
        raise SystemExit(
            f'{name}: lower cap full events={metrics.get("DTC_L1_lower_cap_full_events")!r}'
        )
(out / 'FAST64_1_R1_NONBINDING_CAP_QUALIFICATION_PASS.txt').write_text(
    'FAST64_1_R1_NONBINDING_CAP_QUALIFICATION_PASS\n', encoding='utf-8'
)
PY
