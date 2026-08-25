#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_decoupled_l2_bank_diagnosis.sh --case NAME KERNELSLIST [--case NAME KERNELSLIST ...]
       --run-root DIR [--config FILE] [--trace-config FILE] [--build]
       [--common-config-extra FILE] [--optimized-config-extra FILE]

Runs matched baseline/decoupled pairs sequentially, then checks executable,
trace, and non-backend configuration identity while producing CSV/Markdown
bank-observability summaries.  With OPTIMIZED-CONFIG-EXTRA, also runs a third
decoupled arm with that experiment-only override and writes three_arm_summary.csv.
COMMON-CONFIG-EXTRA is appended to every arm (for example, a dirty-workload
cache geometry).  OPTIMIZED-CONFIG-EXTRA is appended only to the third arm.
Use a new run root for every rebuilt binary.
EOF
}

cases=()
run_root=""
config=""
trace_config=""
optimized_config_extra=""
common_config_extra=""
build=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --case) cases+=("$2" "$3"); shift 3 ;;
    --run-root) run_root="$2"; shift 2 ;;
    --config) config="$2"; shift 2 ;;
    --trace-config) trace_config="$2"; shift 2 ;;
    --common-config-extra) common_config_extra="$2"; shift 2 ;;
    --optimized-config-extra) optimized_config_extra="$2"; shift 2 ;;
    --build) build=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

(( ${#cases[@]} > 0 && ${#cases[@]} % 2 == 0 )) || {
  echo 'error: supply one or more --case NAME KERNELSLIST pairs' >&2; exit 2;
}
[[ -n "$run_root" ]] || { echo 'error: --run-root is required' >&2; exit 2; }
[[ -z "$optimized_config_extra" || -f "$optimized_config_extra" ]] || {
  echo 'error: --optimized-config-extra must name an existing file' >&2; exit 2;
}
[[ -z "$common_config_extra" || -f "$common_config_extra" ]] || {
  echo 'error: --common-config-extra must name an existing file' >&2; exit 2;
}
[[ -n "${DECOUPLED_L2_GPGPUSIM_ROOT:-}" ]] || {
  echo 'error: set DECOUPLED_L2_GPGPUSIM_ROOT' >&2; exit 2;
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "$config" ]]; then
  config="$DECOUPLED_L2_GPGPUSIM_ROOT/configs/tested-cfgs/SM7_QV100/gpgpusim.config"
fi
if [[ -z "$trace_config" ]]; then
  trace_config="$repo_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
fi
[[ -f "$config" && -f "$trace_config" ]] || {
  echo 'error: config or trace-config is missing' >&2; exit 2;
}
mkdir -p "$run_root"
run_root="$(cd "$run_root" && pwd)"

first=1
analyze_args=()
optimized_analyze_args=()
three_arm_summary="$run_root/three_arm_summary.csv"
if [[ -n "$optimized_config_extra" ]]; then
  printf 'suite,case,arm,cycles,run_dir\n' > "$three_arm_summary"
fi
for ((index=0; index<${#cases[@]}; index+=2)); do
  name="${cases[index]}"
  trace="${cases[index + 1]}"
  [[ -f "$trace" ]] || { echo "error: missing trace for $name: $trace" >&2; exit 2; }
  for backend in baseline decoupled; do
    args=(--backend "$backend" --trace "$trace" --config "$config"
          --trace-config "$trace_config" --run-dir "$run_root/$name/$backend")
    if [[ -n "$common_config_extra" ]]; then args+=(--config-extra "$common_config_extra"); fi
    if [[ "$first" -eq 1 && "$build" -eq 1 ]]; then args+=(--build); fi
    "$repo_root/scripts/run_decoupled_l2_smoke.sh" "${args[@]}"
    first=0
  done
  if [[ -n "$optimized_config_extra" ]]; then
    optimized_args=(--backend decoupled --trace "$trace" --config "$config"
                    --trace-config "$trace_config")
    if [[ -n "$common_config_extra" ]]; then
      optimized_args+=(--config-extra "$common_config_extra")
    fi
    optimized_args+=(--config-extra "$optimized_config_extra"
                     --run-dir "$run_root/$name/optimized")
    "$repo_root/scripts/run_decoupled_l2_smoke.sh" "${optimized_args[@]}"
    for arm in baseline decoupled optimized; do
      cycles="$(rg 'gpu_tot_sim_cycle =' "$run_root/$name/$arm/smoke.out" | tail -1 | awk '{print $3}')"
      [[ -n "$cycles" ]] || { echo "error: missing cycle count for $name/$arm" >&2; exit 1; }
      printf 'bank_diagnosis,%s,%s,%s,%s\n' "$name" "$arm" "$cycles" \
        "$run_root/$name/$arm" >> "$three_arm_summary"
    done
    optimized_analyze_args+=(--pair "$name" "$run_root/$name/decoupled" \
                            "$run_root/$name/optimized")
  fi
  analyze_args+=(--pair "$name" "$run_root/$name/baseline" "$run_root/$name/decoupled")
done

python3 "$repo_root/scripts/analyze_decoupled_l2_bank_observability.py" \
  "${analyze_args[@]}" --csv "$run_root/bank_observability.csv" \
  --markdown "$run_root/bank_observability.md"
printf 'PASS run_root=%s summary=%s\n' "$run_root" "$run_root/bank_observability.md"
[[ -z "$optimized_config_extra" ]] || printf 'PASS three_arm_summary=%s\n' "$three_arm_summary"
if [[ -n "$optimized_config_extra" ]]; then
  python3 "$repo_root/scripts/analyze_decoupled_l2_bank_optimization.py" \
    "${optimized_analyze_args[@]}" \
    --optimized-config-extra "$optimized_config_extra" \
    --csv "$run_root/optimized_bank_observability.csv" \
    --markdown "$run_root/optimized_bank_observability.md"
  printf 'PASS optimized_bank_summary=%s\n' "$run_root/optimized_bank_observability.md"
fi
