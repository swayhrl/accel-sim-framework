#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_c2p_addr_topology_observe.sh [--out-root DIR] [--jobs N]
       [--build]

Run read-only exhaustive-C2P+ address/topology observations for BFS, LPS, and
Btree. C2P_GPGPUSIM_ROOT must name the isolated matching backend worktree.
EOF
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out_root="$repo_root/hw_run/c2p-addr-topology-observe-v1-20260823"
jobs=3
build=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out-root) out_root="$2"; shift 2 ;;
    --jobs) jobs="$2"; shift 2 ;;
    --build) build=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ "$jobs" =~ ^[1-9][0-9]*$ ]] || { echo "error: positive --jobs required" >&2; exit 2; }
[[ -n "${C2P_GPGPUSIM_ROOT:-}" ]] || { echo "error: set C2P_GPGPUSIM_ROOT" >&2; exit 2; }

base_config="$repo_root/gpu-simulator/gpgpu-sim/configs/tested-cfgs/SM7_QV100/gpgpusim.config"
trace_config="$repo_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
paper_config="$repo_root/configs/c2p-cache/paper-table.config"
observe_config="$repo_root/configs/c2p-cache/c2p-addr-topology-observe.config"
trace_root="/workspace/worktrees/accel-sim-decoupled-l2/hw_run"
v100_stage="$repo_root/hw_run/c2p-v100-baseline-compat-smoke-v2-20260822/stage"

declare -a cases=(
  "bfs|$v100_stage/c2p-ispass-bfs/c2p-ispass-bfs/traces/kernelslist.g"
  "lps|$v100_stage/c2p-ispass-lps/c2p-ispass-lps/traces/kernelslist.g"
  "btree|$trace_root/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/b+tree-rodinia-3.1/file___data_mil_txt_command___data_command_txt/traces/kernelslist.g"
)

mkdir -p "$out_root"
[[ -f "$observe_config" ]] || { echo "missing config: $observe_config" >&2; exit 2; }
if (( build )); then
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
  local case_name="$1" trace="$2"
  [[ -f "$trace" ]] || { echo "missing trace: $trace" >&2; return 2; }
  "$repo_root/scripts/run_c2p_cache_cases.sh" --trace "$trace" --config "$base_config" \
      --config-extra "$trace_config" --config-extra "$paper_config" \
      --mode-config-extra "$observe_config" --strip-mem-addr-mapping \
      --skip-complete --modes c2p --out-dir "$out_root/$case_name"
}

pids=()
status=0
for spec in "${cases[@]}"; do
  IFS='|' read -r case_name trace <<< "$spec"
  run_one "$case_name" "$trace" >"$out_root/$case_name.driver.log" 2>&1 &
  pids+=("$!")
  if (( ${#pids[@]} >= jobs )); then
    wait "${pids[0]}" || status=1
    pids=("${pids[@]:1}")
  fi
done
for pid in "${pids[@]}"; do wait "$pid" || status=1; done
(( status == 0 )) || exit "$status"

python3 "$repo_root/scripts/analyze_c2p_addr_topology_observe.py" \
    --root "$out_root" --csv "$out_root/addr_topology.csv" \
    --markdown "$out_root/addr_topology.md"
