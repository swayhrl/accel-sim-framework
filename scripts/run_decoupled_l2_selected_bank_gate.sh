#!/usr/bin/env bash
# Run the bounded validation gate for the single bank candidate selected from
# the five-workload four-bank diagnosis.  This deliberately stops before the
# broad suite campaign: a candidate must first demonstrate a real mechanism
# on bandwidth and atomic pressure, then remain safe on the same five traces
# that selected it.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_decoupled_l2_selected_bank_gate.sh --selection FILE [options]

Options:
  --selection FILE       JSON emitted by select_decoupled_l2_bank_candidate.py
  --primary-root DIR     Five-workload diagnosis root; required unless the
                         default hw_run/decoupled-l2-bank-diagnosis/... exists
  --run-root DIR         Output root (required)
  --config FILE          Accel-Sim GPU configuration
  --trace-config FILE    Accel-Sim trace configuration
  --no-build             Reuse the selected simulator binary; default rebuilds
                         through the selected DECOUPLED_L2_GPGPUSIM_ROOT.

The script currently accepts only the evidence-selected bank_count_8
candidate.  It runs a bandwidth/atomic pressure gate followed by bicg, atax,
mvt, syrk, and gesummv.  Every invocation is a sequential matched
baseline/default/optimized three-arm experiment and retains the generic
bank-conservation and candidate-bank checks from run_decoupled_l2_bank_diagnosis.sh.
EOF
}

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
selection=""
primary_root="$repo_root/hw_run/decoupled-l2-bank-diagnosis/20260825-b07c0ad-full"
run_root=""
config="$repo_root/gpu-simulator/gpgpu-sim/configs/tested-cfgs/SM7_QV100/gpgpusim.config"
trace_config="$repo_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
build=1

while (( $# )); do
  case "$1" in
    --selection) selection="$2"; shift 2 ;;
    --primary-root) primary_root="$2"; shift 2 ;;
    --run-root) run_root="$2"; shift 2 ;;
    --config) config="$2"; shift 2 ;;
    --trace-config) trace_config="$2"; shift 2 ;;
    --no-build) build=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown option $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -n "$selection" && -n "$run_root" ]] || {
  echo 'error: --selection and --run-root are required' >&2; usage >&2; exit 2;
}
for path in "$selection" "$config" "$trace_config"; do
  [[ -f "$path" ]] || { echo "error: missing file $path" >&2; exit 2; }
done

candidate="$(python3 - "$selection" <<'PY'
import json
import sys
with open(sys.argv[1]) as source:
    print(json.load(source).get("candidate", ""))
PY
)"
[[ "$candidate" == bank_count_8 ]] || {
  echo "error: selection candidate must be bank_count_8, got $candidate" >&2; exit 1;
}

overlay="$repo_root/experiments/decoupled_l2_overlays/bank_count_8.cfg"
[[ -f "$overlay" ]] || { echo "error: missing candidate overlay $overlay" >&2; exit 2; }

# Reuse the precise traces already provenance-gated by the main diagnosis.
declare -A primary_trace=(
  [bicg]="$primary_root/bicg/baseline/traces/kernelslist.g"
  [atax]="$primary_root/parallel/atax/atax/baseline/traces/kernelslist.g"
  [mvt]="$primary_root/parallel/mvt/mvt/baseline/traces/kernelslist.g"
  [syrk]="$primary_root/parallel/syrk/syrk/baseline/traces/kernelslist.g"
  [gesummv]="$primary_root/parallel/gesummv/gesummv/baseline/traces/kernelslist.g"
)
for name in bicg atax mvt syrk gesummv; do
  [[ -f "${primary_trace[$name]}" ]] || {
    echo "error: missing primary trace for $name: ${primary_trace[$name]}" >&2; exit 2;
  }
done

pretrace_root="$repo_root/hw_run/decoupled-l2-pretraces/ubench/9.1"
bw_trace="$pretrace_root/l2_bw_32f/NO_ARGS/traces/kernelslist.g"
atomic_trace="$pretrace_root/atomic_add_lat/NO_ARGS/traces/kernelslist.g"
[[ -f "$bw_trace" && -f "$atomic_trace" ]] || {
  echo 'error: missing bandwidth or atomic preflight trace' >&2; exit 2;
}

mkdir -p "$run_root"
printf 'selection=%s\ncandidate=%s\noverlay=%s\nprimary_root=%s\n' \
  "$(realpath "$selection")" "$candidate" "$(realpath "$overlay")" \
  "$(realpath "$primary_root")" > "$run_root/gate_manifest.txt"

common=(--config "$config" --trace-config "$trace_config"
        --optimized-config-extra "$overlay" --candidate-label "$candidate"
        --expected-candidate-bank-hash mod --expected-candidate-internal-banks 8)
(( build == 0 )) || common+=(--build)

"$repo_root/scripts/run_decoupled_l2_bank_diagnosis.sh" \
  --case l2_bw_32f "$bw_trace" \
  --case atomic_add_lat "$atomic_trace" \
  --run-root "$run_root/preflight" "${common[@]}"

rg -q 'decoupled_l2\[.*atomic=[1-9]' \
  "$run_root/preflight/atomic_add_lat/decoupled/smoke.out"
rg -q 'decoupled_l2\[.*atomic=[1-9]' \
  "$run_root/preflight/atomic_add_lat/optimized/smoke.out"

"$repo_root/scripts/run_decoupled_l2_bank_diagnosis.sh" \
  --case bicg "${primary_trace[bicg]}" \
  --case atax "${primary_trace[atax]}" \
  --case mvt "${primary_trace[mvt]}" \
  --case syrk "${primary_trace[syrk]}" \
  --case gesummv "${primary_trace[gesummv]}" \
  --run-root "$run_root/primary" "${common[@]}"

python3 "$repo_root/scripts/gate_decoupled_l2_selected_bank_candidate.py" \
  --preflight-csv "$run_root/preflight/optimized_bank_observability.csv" \
  --primary-csv "$run_root/primary/optimized_bank_observability.csv" \
  --atomic-default-log "$run_root/preflight/atomic_add_lat/decoupled/smoke.out" \
  --atomic-optimized-log "$run_root/preflight/atomic_add_lat/optimized/smoke.out" \
  --json "$run_root/admission.json" --markdown "$run_root/admission.md"

printf 'PASS candidate=%s preflight=%s primary=%s\n' "$candidate" \
  "$run_root/preflight" "$run_root/primary" > "$run_root/gate.status"
