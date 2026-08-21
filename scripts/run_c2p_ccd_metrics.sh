#!/usr/bin/env bash
# Re-run CCD only to collect the TP/FN/FP/TN counters added after paper16 v7.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_c2p_ccd_metrics.sh --trace-root HW_RUN_ROOT --out-root RESULT_ROOT
       [--case CASE[,CASE...]] [--skip-complete] [--build]

This preserves v7's seven-mode performance bundles.  It creates a separate
CCD-only, provenance-captured replay root for Fig. 12 classification counters.
Pass that root to analyze_c2p_paper16.py via --ccd-metrics-root.
EOF
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
trace_root=""
out_root=""
cases=""
build=0
skip_complete=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --trace-root) trace_root="$2"; shift 2 ;;
    --out-root) out_root="$2"; shift 2 ;;
    --case) cases="$2"; shift 2 ;;
    --skip-complete) skip_complete=1; shift ;;
    --build) build=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ -n "$trace_root" && -d "$trace_root" ]] || {
  echo "error: --trace-root must name the staged hw_run directory" >&2; exit 2;
}
[[ -n "$out_root" ]] || { echo "error: --out-root is required" >&2; exit 2; }

args=(--trace-root "$trace_root" --out-root "$out_root" --modes ccd)
[[ -n "$cases" ]] && args+=(--case "$cases")
(( build )) && args+=(--build)
(( skip_complete )) && args+=(--skip-complete)
"$repo_root/scripts/run_c2p_paper16.sh" "${args[@]}"
