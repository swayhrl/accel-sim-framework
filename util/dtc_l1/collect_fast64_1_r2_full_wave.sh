#!/usr/bin/env bash
# Strict closeout for the complete immutable FAST64.1 r2 qualification wave.
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs_root=/workspace/fast64-runs
core_sha=bbcbb5e7565417102087bc80b14c349b4e568c05
framework_scientific_sha=037f008b330eb230353b60edf126d6be9f45afdc
runtime_sha=6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041
observer_sha=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
payload_manifest="$repo_root/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
validator="$repo_root/util/dtc_l1/validate_fast64_trace_row.py"
comparator="$repo_root/util/dtc_l1/compare_fast64_nonbinding_cap.py"
output_dir="$repo_root/docs/dtc_l1/fast64/generated/qualification_r2_full_wave"
rows=(
  'fast64_1r2_bicg_base_cap8192_a1|BICG|BASE|FAST64_BASE_A1|FAST64_BASE.config'
  'fast64_1r2_bicg_io_cap8192_a1|BICG|IO|FAST64_IO_A1|FAST64_IO.config'
  'fast64_1r2_bicg_oo_cap8192_a1|BICG|OO|FAST64_OO_A1|FAST64_OO.config'
  'fast64_1r2_bicg_io_cap1048576_a1|BICG|IO|FAST64_IO_CAP1048576_A1|FAST64_IO_CAP1048576.config'
  'fast64_1r2_bicg_oo_cap1048576_a1|BICG|OO|FAST64_OO_CAP1048576_A1|FAST64_OO_CAP1048576.config'
  'fast64_1r2_gesummv_io_cap8192_a1|GESUMMV|IO|FAST64_IO_A1|FAST64_IO.config'
  'fast64_1r2_gesummv_io_cap1048576_a1|GESUMMV|IO|FAST64_IO_CAP1048576_A1|FAST64_IO_CAP1048576.config'
)

run_value() { awk -F '\t' -v key="$2" '$1 == key { count++; value=$2 } END { if (count == 1) print value; else exit 1 }' "$1/RUN_MANIFEST.tsv"; }
verify_identity() {
  local dir=$1 config_file=$2
  test "$(run_value "$dir" simulator_sha256)" = "$runtime_sha"
  test "$(run_value "$dir" core_source_head)" = "$core_sha"
  test "$(run_value "$dir" observer_overlay_sha256)" = "$observer_sha"
  test "$(run_value "$dir" framework_scientific_config_source_sha)" = "$framework_scientific_sha"
  test "$(run_value "$dir" config_sha256)" = "$(sha256sum "$repo_root/configs/dtc_l1/fast64/$config_file" | awk '{print $1}')"
}

for row in "${rows[@]}"; do
  IFS='|' read -r name _ <<<"$row"
  dir="$runs_root/$name"
  test -f "$dir/RUN_MANIFEST.tsv" || { echo "ROW_NOT_STARTED $name" >&2; exit 1; }
  test "$(run_value "$dir" simulator_exit_status)" = 0 || { echo "ROW_NOT_NATURAL_EXIT0 $name" >&2; exit 1; }
  test -n "$(run_value "$dir" terminal_utc)" || { echo "ROW_NO_TERMINAL_TIME $name" >&2; exit 1; }
done

mkdir -p "$output_dir"
for row in "${rows[@]}"; do
  IFS='|' read -r name workload mode config_id config_file <<<"$row"
  dir="$runs_root/$name"
  verify_identity "$dir" "$config_file" || { echo "ROW_IDENTITY_MISMATCH $name" >&2; exit 1; }
  "$validator" --run-dir "$dir" --workload-id "$workload" --mode "$mode" \
    --config-id "$config_id" --config-file "$repo_root/configs/dtc_l1/fast64/$config_file" \
    --core-sha "$core_sha" --framework-sha "$framework_scientific_sha" --observer-sha "$observer_sha" --runtime-sha "$runtime_sha" \
    --payload-manifest "$payload_manifest" --classification FAST64_1_R2_FULL_WAVE \
    --output "$output_dir/$name.json" --require-immutable-attempt
done

"$comparator" --candidate "$output_dir/fast64_1r2_bicg_io_cap8192_a1.json" \
  --high "$output_dir/fast64_1r2_bicg_io_cap1048576_a1.json" \
  --output "$output_dir/FAST64_1_R2_BICG_IO_CAP_COMPARISON.tsv"
"$comparator" --candidate "$output_dir/fast64_1r2_bicg_oo_cap8192_a1.json" \
  --high "$output_dir/fast64_1r2_bicg_oo_cap1048576_a1.json" \
  --output "$output_dir/FAST64_1_R2_BICG_OO_CAP_COMPARISON.tsv"
"$comparator" --candidate "$output_dir/fast64_1r2_gesummv_io_cap8192_a1.json" \
  --high "$output_dir/fast64_1r2_gesummv_io_cap1048576_a1.json" \
  --output "$output_dir/FAST64_1_R2_GESUMMV_IO_CAP_COMPARISON.tsv"
python3 - "$output_dir" <<'PY'
import json
import pathlib
import sys

out = pathlib.Path(sys.argv[1])
for name in (
    'fast64_1r2_bicg_base_cap8192_a1',
    'fast64_1r2_bicg_io_cap8192_a1',
    'fast64_1r2_bicg_oo_cap8192_a1',
    'fast64_1r2_gesummv_io_cap8192_a1',
):
    value = json.loads((out / f'{name}.json').read_text())['metrics'].get(
        'DTC_L1_lower_cap_full_events'
    )
    if value != 0:
        raise SystemExit(f'{name}: lower cap full events={value!r}')
(out / 'FAST64_1_R2_FULL_WAVE_NONBINDING_CAP_QUALIFICATION_PASS.txt').write_text(
    'FAST64_1_R2_FULL_WAVE_NONBINDING_CAP_QUALIFICATION_PASS\n', encoding='utf-8'
)
PY
echo "FAST64_1_R2_FULL_WAVE_ROWS_VALIDATED"
