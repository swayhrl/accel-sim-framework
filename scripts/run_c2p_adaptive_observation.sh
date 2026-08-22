#!/usr/bin/env bash
set -euo pipefail

# First-stage evidence only: every replay retains exhaustive C2P+ candidate
# confirmation.  The backend emits observations but does not consult them, so
# this is intentionally separate from both paper16 and any adaptive policy.

usage() {
  cat <<'EOF'
Usage: scripts/run_c2p_adaptive_observation.sh [--out-root DIR] [--jobs N]

Run the seven-workload C2P+ observation matrix.  C2P_GPGPUSIM_ROOT must name
the matching C2P backend.  Build that backend and accel-sim before launching.
EOF
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out_root="$repo_root/hw_run/c2p-adaptive-observe-v1-20260822"
jobs=7
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out-root) out_root="$2"; shift 2 ;;
    --jobs) jobs="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ "$jobs" =~ ^[1-9][0-9]*$ ]] || { echo "error: --jobs must be positive" >&2; exit 2; }
[[ -n "${C2P_GPGPUSIM_ROOT:-}" ]] || {
  echo "error: set C2P_GPGPUSIM_ROOT to the C2P backend worktree" >&2; exit 2;
}

base_config="$repo_root/gpu-simulator/gpgpu-sim/configs/tested-cfgs/SM7_QV100/gpgpusim.config"
trace_config="$repo_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
paper_config="$repo_root/configs/c2p-cache/paper-table.config"
plus_config="$repo_root/configs/c2p-cache/c2p-separate-target-tag-port.config"
trace_root="/workspace/worktrees/accel-sim-decoupled-l2/hw_run"
v100_stage="$repo_root/hw_run/c2p-v100-baseline-compat-smoke-v2-20260822/stage"

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
printf '%s\n' "# C2P+ adaptive observation campaign" > "$out_root/README.md"
printf '%s\n' >> "$out_root/README.md" \
  "All C2P runs use exhaustive confirmation plus the separate target-tag port." \
  "Statistics are observational; no adaptive choice is enabled." \
  "Backend commit: $(git -C "$C2P_GPGPUSIM_ROOT" rev-parse HEAD)" \
  "Frontend commit: $(git -C "$repo_root" rev-parse HEAD)"

run_case() {
  local case_name="$1" trace="$2"
  [[ -f "$trace" ]] || { echo "missing trace for $case_name: $trace" >&2; return 2; }
  "$repo_root/scripts/run_c2p_cache_cases.sh" \
      --trace "$trace" \
      --config "$base_config" \
      --config-extra "$trace_config" \
      --config-extra "$paper_config" \
      --mode-config-extra "$plus_config" \
      --strip-mem-addr-mapping \
      --skip-complete \
      --modes c2p \
      --out-dir "$out_root/$case_name"
}

pids=()
status=0
for spec in "${cases[@]}"; do
  IFS='|' read -r case_name trace <<< "$spec"
  run_case "$case_name" "$trace" >"$out_root/$case_name.driver.log" 2>&1 &
  pids+=("$!")
  if (( ${#pids[@]} >= jobs )); then
    wait "${pids[0]}" || status=1
    pids=("${pids[@]:1}")
  fi
done
for pid in "${pids[@]}"; do
  wait "$pid" || status=1
done
(( status == 0 )) || exit "$status"

python3 "$repo_root/scripts/analyze_c2p_probe_policy_observation.py" \
    --root "$out_root" \
    --csv "$out_root/observation_summary.csv" \
    --pc-csv "$out_root/observation_pc_buckets.csv" \
    --markdown "$out_root/observation_summary.md"
