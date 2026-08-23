#!/usr/bin/env bash
# Run the compact C2P+ policy diagnosis set without changing the mechanism.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_c2p_confirmation_diagnostics.sh --out-root DIR
       [--phase observe|experiment] [--jobs N] [--build]

observe:    exhaustive control, matched PC-hash, and matched AddrTopo.
experiment: matched PC-hash with <=4-candidate completion and reset scores 6/7.

The fixed diagnosis set is Btree, BFS, and LPS.  Each run copies the same
frontend/backend binary and records normal run provenance.
EOF
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out_root=""
phase="observe"
jobs=1
build=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out-root) out_root="$2"; shift 2 ;;
    --phase) phase="$2"; shift 2 ;;
    --jobs) jobs="$2"; shift 2 ;;
    --build) build=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ -n "$out_root" ]] || { echo "error: --out-root is required" >&2; exit 2; }
[[ "$phase" == observe || "$phase" == experiment ]] || {
  echo "error: --phase must be observe or experiment" >&2; exit 2; }
[[ "$jobs" =~ ^[1-9][0-9]*$ ]] || { echo "error: positive --jobs required" >&2; exit 2; }
[[ -n "${C2P_GPGPUSIM_ROOT:-}" ]] || {
  echo "error: set C2P_GPGPUSIM_ROOT to the matching backend worktree" >&2; exit 2;
}

base_config="$C2P_GPGPUSIM_ROOT/configs/tested-cfgs/SM7_QV100/gpgpusim.config"
trace_config="$repo_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
paper_config="$repo_root/configs/c2p-cache/paper-table.config"
trace_root="/workspace/worktrees/accel-sim-decoupled-l2/hw_run"
v100_stage="/workspace/worktrees/accel-sim-c2p-cache/hw_run/c2p-v100-baseline-compat-smoke-v2-20260822/stage"

control_config="$repo_root/configs/c2p-cache/c2p-adaptive-package-control.config"
pc_config="$repo_root/configs/c2p-cache/c2p-adaptive-package-policy.config"
addr_config="$repo_root/configs/c2p-cache/c2p-adaptive-package-addr-topology-policy.config"
smallfull_config="$repo_root/configs/c2p-cache/c2p-adaptive-package-small-full-policy.config"
initial6_config="$repo_root/configs/c2p-cache/c2p-adaptive-package-initial6-policy.config"
initial7_config="$repo_root/configs/c2p-cache/c2p-adaptive-package-initial7-policy.config"
for path in "$base_config" "$trace_config" "$paper_config" "$control_config" \
            "$pc_config" "$addr_config" "$smallfull_config" "$initial6_config" \
            "$initial7_config"; do
  [[ -f "$path" ]] || { echo "error: missing required input: $path" >&2; exit 2; }
done

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
  local case_name="$1" trace="$2" variant="$3" overlay="$4"
  "$repo_root/scripts/run_c2p_cache_cases.sh" --trace "$trace" --config "$base_config" \
      --config-extra "$trace_config" --config-extra "$paper_config" \
      --mode-config-extra "$overlay" --strip-mem-addr-mapping --skip-complete \
      --modes c2p --out-dir "$out_root/$phase/$case_name/$variant"
}

run_case() {
  local case_name="$1" trace="$2" status=0
  [[ -f "$trace" ]] || { echo "missing trace: $trace" >&2; return 2; }
  local -a variants overlays pids
  if [[ "$phase" == observe ]]; then
    variants=(control pc addr)
    overlays=("$control_config" "$pc_config" "$addr_config")
  else
    variants=(smallfull initial6 initial7)
    overlays=("$smallfull_config" "$initial6_config" "$initial7_config")
  fi
  for i in "${!variants[@]}"; do
    run_one "$case_name" "$trace" "${variants[$i]}" "${overlays[$i]}" \
        >"$out_root/$phase/$case_name.${variants[$i]}.driver.log" 2>&1 &
    pids+=("$!")
  done
  for pid in "${pids[@]}"; do wait "$pid" || status=1; done
  return "$status"
}

mkdir -p "$out_root/$phase"
declare -a cases=(
  "btree|$trace_root/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/b+tree-rodinia-3.1/file___data_mil_txt_command___data_command_txt/traces/kernelslist.g"
  "c2p-ispass-bfs|$v100_stage/c2p-ispass-bfs/c2p-ispass-bfs/traces/kernelslist.g"
  "c2p-ispass-lps|$v100_stage/c2p-ispass-lps/c2p-ispass-lps/traces/kernelslist.g"
)

status=0
active=0
for spec in "${cases[@]}"; do
  IFS='|' read -r case_name trace <<< "$spec"
  run_case "$case_name" "$trace" &
  ((++active))
  if (( active >= jobs )); then
    wait -n || status=1
    active=$((active - 1))
  fi
done
while (( active )); do
  wait -n || status=1
  active=$((active - 1))
done
exit "$status"
