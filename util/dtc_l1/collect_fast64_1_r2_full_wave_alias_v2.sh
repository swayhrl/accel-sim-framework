#!/usr/bin/env bash
# Future-only strict R2 collector.  It never modifies the frozen live closeout
# controller, its marker, validator, parser, comparator, config, or payload.
set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs=/workspace/fast64-runs
out="$repo/docs/dtc_l1/fast64/generated/qualification_r2_full_wave_alias_v2"
validator="$repo/util/dtc_l1/validate_fast64_trace_row_alias_v2.py"
comparator="$repo/util/dtc_l1/compare_fast64_nonbinding_cap.py"
payload="$repo/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
core=bbcbb5e7565417102087bc80b14c349b4e568c05
framework=037f008b330eb230353b60edf126d6be9f45afdc
runtime=6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
rows=(
  'fast64_1r2_bicg_base_cap8192_a1|BICG|BASE|FAST64_BASE_A1|FAST64_BASE.config|8192'
  'fast64_1r2_bicg_io_cap8192_a1|BICG|IO|FAST64_IO_A1|FAST64_IO.config|8192'
  'fast64_1r2_bicg_oo_cap8192_a1|BICG|OO|FAST64_OO_A1|FAST64_OO.config|8192'
  'fast64_1r2_bicg_io_cap1048576_a1|BICG|IO|FAST64_IO_CAP1048576_A1|FAST64_IO_CAP1048576.config|1048576'
  'fast64_1r2_bicg_oo_cap1048576_a1|BICG|OO|FAST64_OO_CAP1048576_A1|FAST64_OO_CAP1048576.config|1048576'
  'fast64_1r2_gesummv_io_cap8192_a1|GESUMMV|IO|FAST64_IO_A1|FAST64_IO.config|8192'
  'fast64_1r2_gesummv_io_cap1048576_a1|GESUMMV|IO|FAST64_IO_CAP1048576_A1|FAST64_IO_CAP1048576.config|1048576'
)

value() { awk -F '\t' -v k="$2" '$1==k {n++;v=$2} END {if(n==1)print v;else exit 1}' "$1/RUN_MANIFEST.tsv"; }
for row in "${rows[@]}"; do
  IFS='|' read -r name _ _ _ config cap <<<"$row"
  d="$runs/$name"; f="$repo/configs/dtc_l1/fast64/$config"
  test "$(value "$d" simulator_exit_status)" = 0
  test "$(value "$d" core_source_head)" = "$core"
  test "$(value "$d" framework_scientific_config_source_sha)" = "$framework"
  test "$(value "$d" observer_overlay_sha256)" = "$observer"
  test "$(value "$d" simulator_sha256)" = "$runtime"
  test "$(value "$d" config_sha256)" = "$(sha256sum "$f" | awk '{print $1}')"
  test "$(grep -F -- '-gpgpu_dtc_l1_lower_outstanding_cap ' "$f" | tail -1)" = "-gpgpu_dtc_l1_lower_outstanding_cap $cap"
done
test ! -e "$out"; mkdir -p "$out"
for row in "${rows[@]}"; do
  IFS='|' read -r name workload mode config_id config _ <<<"$row"
  "$validator" --run-dir "$runs/$name" --workload-id "$workload" --mode "$mode" --config-id "$config_id" --config-file "$repo/configs/dtc_l1/fast64/$config" --core-sha "$core" --framework-sha "$framework" --observer-sha "$observer" --runtime-sha "$runtime" --payload-manifest "$payload" --classification FAST64_1_R2_FULL_WAVE --output "$out/$name.json" --require-immutable-attempt
done
"$comparator" --candidate "$out/fast64_1r2_bicg_io_cap8192_a1.json" --high "$out/fast64_1r2_bicg_io_cap1048576_a1.json" --output "$out/FAST64_1_R2_BICG_IO_CAP_COMPARISON.tsv"
"$comparator" --candidate "$out/fast64_1r2_bicg_oo_cap8192_a1.json" --high "$out/fast64_1r2_bicg_oo_cap1048576_a1.json" --output "$out/FAST64_1_R2_BICG_OO_CAP_COMPARISON.tsv"
"$comparator" --candidate "$out/fast64_1r2_gesummv_io_cap8192_a1.json" --high "$out/fast64_1r2_gesummv_io_cap1048576_a1.json" --output "$out/FAST64_1_R2_GESUMMV_IO_CAP_COMPARISON.tsv"
python3 - "$out" <<'PY'
import json, pathlib, sys
out = pathlib.Path(sys.argv[1])
for name in ('fast64_1r2_bicg_base_cap8192_a1','fast64_1r2_bicg_io_cap8192_a1','fast64_1r2_bicg_oo_cap8192_a1','fast64_1r2_gesummv_io_cap8192_a1'):
    if json.loads((out / (name + '.json')).read_text())['metrics'].get('DTC_L1_lower_cap_full_events') != 0:
        raise SystemExit(name + ': lower cap unexpectedly bound')
(out / 'FAST64_1_R2_FULL_WAVE_ALIAS_V2_PASS.txt').write_text('FAST64_1_R2_FULL_WAVE_ALIAS_V2_PASS\n')
PY
echo FAST64_1_R2_FULL_WAVE_ALIAS_V2_ROWS_VALIDATED
