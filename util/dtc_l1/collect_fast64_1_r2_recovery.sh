#!/usr/bin/env bash
# Compose clean historical r1 rows with the immutable, fresh r2 OO replacement.
# This is a new closeout path; it neither changes nor adopts the live r1 collector.
set -euo pipefail

# Superseded after two independent r1 controller-path contaminations.  Formal
# FAST64.1 closeout must be seven-row R2 only; this path can never compose R1.
echo "FAST64_R1_R2_MIXED_COLLECTOR_SUPERSEDED_USE_FULL_R2_COLLECTOR" >&2
exit 1

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs_root=/workspace/fast64-runs
core_sha=bbcbb5e7565417102087bc80b14c349b4e568c05
framework_scientific_sha=037f008b330eb230353b60edf126d6be9f45afdc
runtime_sha=6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041
observer_sha=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
payload_manifest="$repo_root/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
validator="$repo_root/util/dtc_l1/validate_fast64_trace_row.py"
comparator="$repo_root/util/dtc_l1/compare_fast64_nonbinding_cap.py"
output_dir="$repo_root/docs/dtc_l1/fast64/generated/qualification_r2_recovery"

rows=(
  'fast64_1r1_bicg_base_cap8192_a1|BICG|BASE|FAST64_BASE_A1|FAST64_BASE.config|legacy'
  'fast64_1r1_bicg_io_cap8192_a1|BICG|IO|FAST64_IO_A1|FAST64_IO.config|legacy'
  'fast64_1r2_bicg_oo_cap8192_a1|BICG|OO|FAST64_OO_A1|FAST64_OO.config|immutable'
  'fast64_1r1_bicg_io_cap1048576_a1|BICG|IO|FAST64_IO_CAP1048576_A1|FAST64_IO_CAP1048576.config|legacy'
  'fast64_1r1_bicg_oo_cap1048576_a1|BICG|OO|FAST64_OO_CAP1048576_A1|FAST64_OO_CAP1048576.config|legacy'
  'fast64_1r1_gesummv_io_cap8192_a1|GESUMMV|IO|FAST64_IO_A1|FAST64_IO.config|legacy'
  'fast64_1r1_gesummv_io_cap1048576_a1|GESUMMV|IO|FAST64_IO_CAP1048576.config|legacy'
)

run_value() { awk -F '\t' -v key="$2" '$1 == key { count++; value=$2 } END { if (count == 1) print value; else exit 1 }' "$1/RUN_MANIFEST.tsv"; }
legacy_single_epoch() {
  local dir=$1 log=$2
  test "$(find "$dir" -maxdepth 1 -type f -name 'perf_counter*.csv.gz' | wc -l)" = 1
  test "$(rg -F -c 'GPGPU-Sim uArch: performance model initialization complete.' "$dir/simulator.stdout")" = 1
  test "$(rg -F -c 'GPGPU-Sim: *** exit detected ***' "$dir/simulator.stdout")" = 1
  test ! -s "$log"
}
verify_identity() {
  local dir=$1 provenance=$2 config_file=$3
  test "$(run_value "$dir" simulator_sha256)" = "$runtime_sha"
  test "$(run_value "$dir" core_source_head)" = "$core_sha"
  test "$(run_value "$dir" observer_overlay_sha256)" = "$observer_sha"
  test "$(run_value "$dir" config_sha256)" = "$(sha256sum "$repo_root/configs/dtc_l1/fast64/$config_file" | awk '{print $1}')"
  if [ "$provenance" = immutable ]; then
    test "$(run_value "$dir" framework_scientific_config_source_sha)" = "$framework_scientific_sha"
  else
    test "$(run_value "$dir" framework_source_head)" = "$framework_scientific_sha"
  fi
}

for row in "${rows[@]}"; do
  IFS='|' read -r name _ <<<"$row"
  dir="$runs_root/$name"
  test "$(run_value "$dir" simulator_exit_status)" = 0 || { echo "ROW_NOT_NATURAL_EXIT0 $name" >&2; exit 1; }
  test -n "$(run_value "$dir" terminal_utc)" || { echo "ROW_NO_TERMINAL_TIME $name" >&2; exit 1; }
done

mkdir -p "$output_dir"
for row in "${rows[@]}"; do
  IFS='|' read -r name workload mode config_id config_file provenance <<<"$row"
  dir="$runs_root/$name"
  verify_identity "$dir" "$provenance" "$config_file" || {
    echo "ROW_IDENTITY_MISMATCH $name" >&2
    exit 1
  }
  args=(--run-dir "$dir" --workload-id "$workload" --mode "$mode" --config-id "$config_id"
    --config-file "$repo_root/configs/dtc_l1/fast64/$config_file" --core-sha "$core_sha"
    --framework-sha "$framework_scientific_sha" --observer-sha "$observer_sha" --payload-manifest "$payload_manifest"
    --classification FAST64_1_R2_RECOVERY --output "$output_dir/$name.json")
  if [ "$provenance" = immutable ]; then
    "$validator" "${args[@]}" --require-immutable-attempt
  else
    legacy_single_epoch "$dir" "$runs_root/$name.launcher.log" || { echo "LEGACY_EPOCH_OR_LAUNCHER_ANOMALY $name" >&2; exit 1; }
    "$validator" "${args[@]}"
  fi
done

"$comparator" --candidate "$output_dir/fast64_1r1_bicg_io_cap8192_a1.json" \
  --high "$output_dir/fast64_1r1_bicg_io_cap1048576_a1.json" \
  --output "$output_dir/FAST64_1_R2_BICG_IO_CAP_COMPARISON.tsv"
"$comparator" --candidate "$output_dir/fast64_1r2_bicg_oo_cap8192_a1.json" \
  --high "$output_dir/fast64_1r1_bicg_oo_cap1048576_a1.json" \
  --output "$output_dir/FAST64_1_R2_BICG_OO_CAP_COMPARISON.tsv"
"$comparator" --candidate "$output_dir/fast64_1r1_gesummv_io_cap8192_a1.json" \
  --high "$output_dir/fast64_1r1_gesummv_io_cap1048576_a1.json" \
  --output "$output_dir/FAST64_1_R2_GESUMMV_IO_CAP_COMPARISON.tsv"
python3 - "$output_dir" <<'PY'
import json
import pathlib
import sys

out = pathlib.Path(sys.argv[1])
for name in (
    'fast64_1r1_bicg_base_cap8192_a1',
    'fast64_1r1_bicg_io_cap8192_a1',
    'fast64_1r2_bicg_oo_cap8192_a1',
    'fast64_1r1_gesummv_io_cap8192_a1',
):
    value = json.loads((out / f'{name}.json').read_text())['metrics'].get(
        'DTC_L1_lower_cap_full_events'
    )
    if value != 0:
        raise SystemExit(f'{name}: lower cap full events={value!r}')
(out / 'FAST64_1_R2_NONBINDING_CAP_QUALIFICATION_PASS.txt').write_text(
    'FAST64_1_R2_NONBINDING_CAP_QUALIFICATION_PASS\n', encoding='utf-8'
)
PY
echo "FAST64_1_R2_RECOVERY_ROWS_VALIDATED"
