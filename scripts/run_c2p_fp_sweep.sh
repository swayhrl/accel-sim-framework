#!/usr/bin/env bash
# Run C2P-only m/k points for the paper Figure-13 FP-ratio study.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_c2p_fp_sweep.sh --trace-root HW_RUN_ROOT --out-root RESULT_ROOT
       [--case CASE[,CASE...]] [--build]

Each point retains the paper-table geometry and differs only in the C2P
Snapshot Matrix BF rows per bank and the number of BF hashes.  The baseline
IPC and R/S group classification are intentionally imported from the canonical
paper16 campaign during analysis; this runner performs C2P-only replays.
EOF
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
trace_root=""
out_root=""
cases=""
build=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --trace-root) trace_root="$2"; shift 2 ;;
    --out-root) out_root="$2"; shift 2 ;;
    --case) cases="$2"; shift 2 ;;
    --build) build=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ -n "$trace_root" && -d "$trace_root" ]] || {
  echo "error: --trace-root must name the staged hw_run directory" >&2; exit 2;
}
[[ -n "$out_root" ]] || { echo "error: --out-root is required" >&2; exit 2; }

for config in "$repo_root"/configs/c2p-cache/fp-sweep/*.config; do
  point="$(basename "$config" .config)"
  args=(--trace-root "$trace_root" --out-root "$out_root/$point" --modes c2p
        --mode-config-extra "$config")
  [[ -n "$cases" ]] && args+=(--case "$cases")
  (( build )) && args+=(--build)
  "$repo_root/scripts/run_c2p_paper16.sh" "${args[@]}"
done
