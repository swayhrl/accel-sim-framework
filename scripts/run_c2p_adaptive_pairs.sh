#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_c2p_adaptive_pairs.sh [--out-root DIR] [--pair-jobs N]
       [--control-config FILE] [--adaptive-config FILE] [--build]

Run same-binary exhaustive C2P+ controls and adaptive C2P+ pairs for the
seven-workload diagnostic set.  Build the selected C2P backend and accel-sim
before launching with --build when its public headers changed.
C2P_GPGPUSIM_ROOT must name that backend.
EOF
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out_root="$repo_root/hw_run/c2p-adaptive-pairs-v1-20260822"
pair_jobs=7
control_config=""
adaptive_config=""
build=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out-root) out_root="$2"; shift 2 ;;
    --pair-jobs) pair_jobs="$2"; shift 2 ;;
    --control-config) control_config="$2"; shift 2 ;;
    --adaptive-config) adaptive_config="$2"; shift 2 ;;
    --build) build=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ "$pair_jobs" =~ ^[1-9][0-9]*$ ]] || { echo "error: positive --pair-jobs required" >&2; exit 2; }
[[ -n "${C2P_GPGPUSIM_ROOT:-}" ]] || { echo "error: set C2P_GPGPUSIM_ROOT" >&2; exit 2; }

base_config="$repo_root/gpu-simulator/gpgpu-sim/configs/tested-cfgs/SM7_QV100/gpgpusim.config"
trace_config="$repo_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
paper_config="$repo_root/configs/c2p-cache/paper-table.config"
control_config="${control_config:-$repo_root/configs/c2p-cache/c2p-adaptive-probe-control.config}"
adaptive_config="${adaptive_config:-$repo_root/configs/c2p-cache/c2p-adaptive-probe-policy.config}"
trace_root="/workspace/worktrees/accel-sim-decoupled-l2/hw_run"
v100_stage="$repo_root/hw_run/c2p-v100-baseline-compat-smoke-v2-20260822/stage"
observe_root="$repo_root/hw_run/c2p-adaptive-observe-v1-20260822"

declare -a cases=(
  "2DConvolution|$trace_root/c2p-polybench-full-20260821/polybench/11.0/polybench-2DConvolution/NO_ARGS/traces/kernelslist.g"
  "lps|$v100_stage/c2p-ispass-lps/c2p-ispass-lps/traces/kernelslist.g"
  "btree|$trace_root/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/b+tree-rodinia-3.1/file___data_mil_txt_command___data_command_txt/traces/kernelslist.g"
  "bfs|$v100_stage/c2p-ispass-bfs/c2p-ispass-bfs/traces/kernelslist.g"
  "sgemm|$trace_root/decoupled-l2-extract/parboil.current.small8.stage/parboil/11.0/parboil-sgemm/_i___data_medium_input_matrix1_txt___data_medium_input_matrix2t_txt___data_medium_input_matrix2t_txt__o_matrix3_txt/traces/kernelslist.g"
  "gaussian|$trace_root/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/gaussian-rodinia-3.1/_s_256/traces/kernelslist.g"
  "nn|$trace_root/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/nn-rodinia-3.1/__data_filelist_4__r_5__lat_30__lng_90/traces/kernelslist.g"
)

mkdir -p "$out_root"
[[ -f "$control_config" ]] || { echo "missing control config: $control_config" >&2; exit 2; }
[[ -f "$adaptive_config" ]] || { echo "missing adaptive config: $adaptive_config" >&2; exit 2; }
if (( build )); then
  # c2p_cache is a public C++ configuration type.  Rebuild the front end once
  # here, before the paired children copy their simulator images; otherwise a
  # stale accel-sim binary can misparse a newer backend's class layout.
  (
    export GPGPUSIM_ROOT="$C2P_GPGPUSIM_ROOT"
    set +u
    source "$C2P_GPGPUSIM_ROOT/setup_environment" >/dev/null
    export GPGPUSIM_SETUP_ENVIRONMENT_WAS_RUN=1
    source "$repo_root/gpu-simulator/setup_environment.sh" >/dev/null
    set -u
    make -C "$repo_root/gpu-simulator" -j1
  )
fi
run_one() {
  local case_name="$1" trace="$2" variant="$3" mode_config="$4"
  "$repo_root/scripts/run_c2p_cache_cases.sh" --trace "$trace" --config "$base_config" \
      --config-extra "$trace_config" --config-extra "$paper_config" \
      --mode-config-extra "$mode_config" --strip-mem-addr-mapping \
      --skip-complete --modes c2p --out-dir "$out_root/$case_name/$variant"
}
run_pair() {
  local case_name="$1" trace="$2" status=0
  [[ -f "$trace" ]] || { echo "missing trace: $trace" >&2; return 2; }
  run_one "$case_name" "$trace" control "$control_config" >"$out_root/$case_name.control.driver.log" 2>&1 &
  local control_pid=$!
  run_one "$case_name" "$trace" adaptive "$adaptive_config" >"$out_root/$case_name.adaptive.driver.log" 2>&1 &
  local adaptive_pid=$!
  wait "$control_pid" || status=1
  wait "$adaptive_pid" || status=1
  return "$status"
}

pids=()
status=0
for spec in "${cases[@]}"; do
  IFS='|' read -r case_name trace <<< "$spec"
  run_pair "$case_name" "$trace" &
  pids+=("$!")
  if (( ${#pids[@]} >= pair_jobs )); then
    wait "${pids[0]}" || status=1
    pids=("${pids[@]:1}")
  fi
done
for pid in "${pids[@]}"; do wait "$pid" || status=1; done
(( status == 0 )) || exit "$status"

python3 "$repo_root/scripts/analyze_c2p_adaptive_pairs.py" --root "$out_root" \
    --observation-root "$observe_root" --csv "$out_root/pair_summary.csv" \
    --markdown "$out_root/pair_summary.md" \
    --tail-csv "$out_root/tail_observation.csv" \
    --tail-markdown "$out_root/tail_observation.md"
