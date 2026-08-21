#!/usr/bin/env bash
# Run the canonical locally available C2P paper workload set.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_c2p_paper16.sh --trace-root HW_RUN_ROOT --out-root RESULT_ROOT
       [--case CASE[,CASE...]] [--modes MODES] [--config-extra FILE]
       [--mode-config-extra FILE] [--build]

The canonical case list is configs/c2p-cache/paper16_workloads.tsv.  Each
entry names a complete replay trace for its selected input; no 1/N trace
fraction is used by this runner.  The standard paper-table overlay is always
applied.  Pass paper-table-l2-50.config through --config-extra to create the
50-cycle L2 classification point in a separate result root.
EOF
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
manifest="$repo_root/configs/c2p-cache/paper16_workloads.tsv"
trace_root=""
out_root=""
cases=""
modes="baseline,oracle,ideal,c2p,ata,ccd,ring"
build=0
config_extras=()
mode_config_extras=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --trace-root) trace_root="$2"; shift 2 ;;
    --out-root) out_root="$2"; shift 2 ;;
    --case) cases="$2"; shift 2 ;;
    --modes) modes="$2"; shift 2 ;;
    --config-extra) config_extras+=("$2"); shift 2 ;;
    --mode-config-extra) mode_config_extras+=("$2"); shift 2 ;;
    --build) build=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -n "$trace_root" && -d "$trace_root" ]] || {
  echo "error: --trace-root must name the staged hw_run directory" >&2; exit 2;
}
[[ -n "$out_root" ]] || { echo "error: --out-root is required" >&2; exit 2; }
[[ -n "${C2P_GPGPUSIM_ROOT:-}" ]] || {
  echo "error: set C2P_GPGPUSIM_ROOT to the matching C2P GPGPU-Sim worktree" >&2; exit 2;
}

case_selected() {
  [[ -z "$cases" ]] && return 0
  local item
  IFS=',' read -ra items <<< "$cases"
  for item in "${items[@]}"; do [[ "$item" == "$1" ]] && return 0; done
  return 1
}

runner=("$repo_root/scripts/run_c2p_cache_cases.sh"
  --config "$repo_root/gpu-simulator/gpgpu-sim/configs/tested-cfgs/SM7_QV100/gpgpusim.config"
  --config-extra "$repo_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
  --config-extra "$repo_root/configs/c2p-cache/paper-table.config"
  --strip-mem-addr-mapping --modes "$modes")
for config_extra in "${config_extras[@]}"; do
  runner+=(--config-extra "$config_extra")
done
for config_extra in "${mode_config_extras[@]}"; do
  runner+=(--mode-config-extra "$config_extra")
done
(( build )) && runner+=(--build)

mkdir -p "$out_root"
while IFS=$'\t' read -r case suite abbr input_label trace_rel; do
  [[ -z "$case" || "$case" == "case" || "$case" == \#* ]] && continue
  case_selected "$case" || continue
  trace="$trace_root/$trace_rel/kernelslist.g"
  [[ -f "$trace" ]] || { echo "error: $case trace missing: $trace" >&2; exit 2; }
  printf 'RUN case=%s suite=%s input=%s\n' "$case" "$suite" "$input_label"
  "${runner[@]}" --trace "$trace" --out-dir "$out_root/$case"
done < "$manifest"
