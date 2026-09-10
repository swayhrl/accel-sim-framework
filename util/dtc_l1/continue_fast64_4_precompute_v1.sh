#!/usr/bin/env bash
# Future-only, one-worker physical-acquisition continuation for FAST64.4.  It
# starts only after the separately monitored ATAX/IO strict evidence exists.
# All rows remain PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE until FAST64.3 closes.
set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs=/workspace/fast64-runs
evidence="$repo/docs/dtc_l1/fast64/generated/fast64_4_precomputed_rows_v1"
adopted="$evidence/fast64_4_atax_io_cap8192_a1_v3.json"
log="$runs/fast64_4_precompute_continuation_v1.log"
lock="$runs/.fast64_4_precompute_continuation_v1.lock"
dispatcher="$repo/util/dtc_l1/dispatch_fast64_precomputed_row_v2.sh"
validator="$repo/util/dtc_l1/validate_fast64_trace_row_alias_v3.py"
payload="$repo/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
core=bbcbb5e7565417102087bc80b14c349b4e568c05
framework=037f008b330eb230353b60edf126d6be9f45afdc
runtime=6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
classification=PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE
cpu=3
poll=120

test -x "$dispatcher" && test -x "$validator" && test -r "$payload"
mkdir -p "$evidence"
exec 9>"$lock"
flock -n 9 || { echo FAST64_4_PRECOMPUTE_CONTINUATION_V1_ALREADY_ACTIVE >&2; exit 1; }
emit() { printf '%s\tutc=%s\t%s\n' "$1" "$(date -u +%FT%TZ)" "$2" | tee -a "$log"; }
config_for() {
  case "$1" in
    IO) printf '%s\n' "$repo/configs/dtc_l1/fast64/FAST64_IO.config" ;;
    OO) printf '%s\n' "$repo/configs/dtc_l1/fast64/FAST64_OO.config" ;;
    *) return 2 ;;
  esac
}
config_id_for() { printf 'FAST64_%s_A1\n' "$1"; }
value() { awk -F '\t' -v k="$2" '$1==k {n++;v=$2} END {if(n==1)print v;else exit 1}' "$1"; }

# Existing exact R2 BICG IO/OO and GESUMMV IO rows are intentionally omitted.
# All names are fresh and are checked absent before immutable dispatch.
tasks=(
  'ATAX|OO|fast64_4_atax_oo_cap8192_a1_v3'
  'GESUMMV|OO|fast64_4_gesummv_oo_cap8192_a1_v3'
  'GEMM|IO|fast64_4_gemm_io_cap8192_a1_v3'
  'GEMM|OO|fast64_4_gemm_oo_cap8192_a1_v3'
  '2DConvolution|IO|fast64_4_2DConvolution_io_cap8192_a1_v3'
  '2DConvolution|OO|fast64_4_2DConvolution_oo_cap8192_a1_v3'
  'Btree|IO|fast64_4_btree_io_cap8192_a1_v3'
  'Btree|OO|fast64_4_btree_oo_cap8192_a1_v3'
  'DWT2D|IO|fast64_4_dwt2d_io_cap8192_a1_v3'
  'DWT2D|OO|fast64_4_dwt2d_oo_cap8192_a1_v3'
  'Gaussian|IO|fast64_4_gaussian_io_cap8192_a1_v3'
  'Gaussian|OO|fast64_4_gaussian_oo_cap8192_a1_v3'
  'Hotspot1|IO|fast64_4_hotspot1_io_cap8192_a1_v3'
  'Hotspot1|OO|fast64_4_hotspot1_oo_cap8192_a1_v3'
  'LUD|IO|fast64_4_lud_io_cap8192_a1_v3'
  'LUD|OO|fast64_4_lud_oo_cap8192_a1_v3'
  'NN|IO|fast64_4_nn_io_cap8192_a1_v3'
  'NN|OO|fast64_4_nn_oo_cap8192_a1_v3'
  'MRI-Q|IO|fast64_4_mri-q_io_cap8192_a1_v3'
  'MRI-Q|OO|fast64_4_mri-q_oo_cap8192_a1_v3'
)

while ! test -f "$adopted"; do
  emit FAST64_4_PRECOMPUTE_V1_WAIT_ADOPTED_ATAX_IO "evidence=$adopted"
  sleep "$poll"
done
emit FAST64_4_PRECOMPUTE_V1_ADOPTED_ATAX_IO "evidence=$adopted"

for item in "${tasks[@]}"; do
  IFS='|' read -r workload mode row <<<"$item"
  run="$runs/$row"
  output="$evidence/$row.json"
  config=$(config_for "$mode")
  test -r "$config" && test ! -e "$output" || { emit FAST64_4_PRECOMPUTE_V1_REFUSE_EXISTING "row=$row"; exit 1; }
  for path in "$run" "$run.launcher.log" "$run.supervisor.tsv"; do
    test ! -e "$path" || { emit FAST64_4_PRECOMPUTE_V1_REFUSE_NAMESPACE "row=$row path=$path"; exit 1; }
  done
  "$dispatcher" --name "$row" --workload "$workload" --mode "$mode" --config "$config" --cpu "$cpu" \
    --classification "$classification" --framework-scientific-config-source-sha "$framework"
  emit FAST64_4_PRECOMPUTE_V1_DISPATCHED "row=$row workload=$workload mode=$mode cpu=$cpu"
  while ! test -f "$run/RUN_TERMINAL.tsv"; do
    emit FAST64_4_PRECOMPUTE_V1_WAIT_TERMINAL "row=$row"
    sleep "$poll"
  done
  test "$(value "$run/RUN_TERMINAL.tsv" simulator_exit_status)" = 0 || {
    emit FAST64_4_PRECOMPUTE_V1_NONZERO_TERMINAL "row=$row"; exit 1;
  }
  "$validator" --run-dir "$run" --workload-id "$workload" --mode "$mode" --config-id "$(config_id_for "$mode")" \
    --config-file "$config" --core-sha "$core" --framework-sha "$framework" --observer-sha "$observer" \
    --runtime-sha "$runtime" --payload-manifest "$payload" --classification "$classification" \
    --require-immutable-attempt --output "$output"
  if rg -n -i 'assertion failed|fatal error|deadlock detected|output mismatch|checker.*fail|segmentation fault|core dumped' \
      "$run/simulator.stdout" "$run/simulator.stderr" "$run.launcher.log"; then
    emit FAST64_4_PRECOMPUTE_V1_FORBIDDEN_FAILURE_SIGNATURE "row=$row"; exit 1
  fi
  emit FAST64_4_PRECOMPUTE_V1_STRICT_VALID "row=$row evidence=$output"
done
emit FAST64_4_PRECOMPUTE_V1_COMPLETE "rows=${#tasks[@]}"
