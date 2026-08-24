#!/usr/bin/env bash
# Stage, but do not automatically broaden, the first genuine tensor-core C2P
# replay.  The case is intentionally the existing 1/40 instruction trim: it
# retains all seven CUTLASS WMMA kernels and is small enough for a quick
# mechanism smoke before scheduling any larger CUTLASS shape.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_c2p_cutlass_wmma_1of40.sh --out-root DIR [--trace-root DIR]
       [--stage smoke|core|classify|c2pplus-control|c2pplus-addr|all]
       [--skip-complete] [--build]

Stages follow the existing experiment order and never mix result directories:
  smoke            baseline,oracle: trace/runtime compatibility and oracle ceiling
  core             c2p,ideal: default mechanism versus ideal peer service
  classify         baseline with L2=50: only the independent R/S point
  c2pplus-control  four-probe exhaustive C2P+ control (separate target tag port)
  c2pplus-addr     capacity-matched address/topology confirmation policy
  all              runs the five stages in the order above

Set C2P_GPGPUSIM_ROOT to the matching C2P GPGPU-Sim worktree.  This runner
does not run until it is explicitly invoked; it only names already staged
1/40 traces and writes all replay outputs below --out-root.
EOF
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
trace_root="/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-trace-fraction/cutlass-all-1of40-trim-v1"
out_root=""
stage="smoke"
skip_complete=0
build=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out-root) out_root="$2"; shift 2 ;;
    --trace-root) trace_root="$2"; shift 2 ;;
    --stage) stage="$2"; shift 2 ;;
    --skip-complete) skip_complete=1; shift ;;
    --build) build=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -n "$out_root" ]] || { echo "error: --out-root is required" >&2; exit 2; }
case "$stage" in
  smoke|core|classify|c2pplus-control|c2pplus-addr|all) ;;
  *) echo "error: invalid --stage: $stage" >&2; exit 2 ;;
esac
[[ -n "${C2P_GPGPUSIM_ROOT:-}" ]] || {
  echo "error: set C2P_GPGPUSIM_ROOT to the matching backend worktree" >&2; exit 2;
}

manifest="$repo_root/configs/c2p-cache/cutlass_wmma_1of40_workloads.tsv"
base_config="$C2P_GPGPUSIM_ROOT/configs/tested-cfgs/SM7_QV100/gpgpusim.config"
trace_config="$repo_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
paper_config="$repo_root/configs/c2p-cache/paper-table.config"
l2_50_config="$repo_root/configs/c2p-cache/paper-table-l2-50.config"
control_config="$repo_root/configs/c2p-cache/c2p-adaptive-package-control.config"
addr_config="$repo_root/configs/c2p-cache/c2p-adaptive-package-addr-topology-policy.config"
for path in "$manifest" "$base_config" "$trace_config" "$paper_config" \
            "$l2_50_config" "$control_config" "$addr_config"; do
  [[ -f "$path" ]] || { echo "error: missing required input: $path" >&2; exit 2; }
done

run_case() {
  local label="$1" modes="$2" overlay="${3:-}"
  local case_name provider shape trace_rel trace
  while IFS=$'\t' read -r case_name provider shape trace_rel; do
    [[ -z "$case_name" || "$case_name" == case || "$case_name" == \#* ]] && continue
    trace="$trace_root/$trace_rel/kernelslist.g"
    [[ -f "$trace" ]] || { echo "error: trace missing: $trace" >&2; return 2; }
    local args=("$repo_root/scripts/run_c2p_cache_cases.sh"
      --trace "$trace" --config "$base_config"
      --config-extra "$trace_config" --config-extra "$paper_config"
      --strip-mem-addr-mapping --modes "$modes"
      --out-dir "$out_root/$case_name/$label")
    [[ -n "$overlay" ]] && args+=(--mode-config-extra "$overlay")
    (( skip_complete )) && args+=(--skip-complete)
    (( build )) && args+=(--build)
    "${args[@]}"
  done < "$manifest"
}

case "$stage" in
  smoke) run_case smoke baseline,oracle ;;
  core) run_case core c2p,ideal ;;
  classify) run_case l2_50 baseline "$l2_50_config" ;;
  c2pplus-control) run_case c2pplus_control c2p "$control_config" ;;
  c2pplus-addr) run_case c2pplus_addr c2p "$addr_config" ;;
  all)
    run_case smoke baseline,oracle
    run_case core c2p,ideal
    run_case l2_50 baseline "$l2_50_config"
    run_case c2pplus_control c2p "$control_config"
    run_case c2pplus_addr c2p "$addr_config"
    ;;
esac
