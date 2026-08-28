#!/usr/bin/env bash
# Run the observation-only peer-locality diagnostic campaign described by
# docs/c2p-cache/peer_locality_diagnostic_contract.md.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_c2p_peer_locality_diagnostic.sh --trace-root HW_RUN_ROOT \
       --out-root RESULT_ROOT [--stage current64|literal16k|fourset64k|all] \
       [--jobs N] [--skip-complete]

Each replay is oracle-only and enables the read-only peer-locality overlay
only for that oracle mode.  The three stages are:
  current64    all 16 locally complete traces, 16x32x128B private L1;
  literal16k   Hotspot, Gaussian, LUD, SGEMM, 3mm, GEMM with 4x32x128B;
  fourset64k   the same six workloads with 4x128x128B.

The script writes a per-stage invariant audit after every successful stage.
For `literal16k`, a Gaussian deadlock is accepted only as the explicitly
recorded invalid baseline-geometry cell; all other selected cases must pass
the same audit.  Set C2P_GPGPUSIM_ROOT to the matching GPGPU-Sim source
worktree.
EOF
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
trace_root=""
out_root=""
stage="all"
jobs=4
skip_complete=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --trace-root) trace_root="$2"; shift 2 ;;
    --out-root) out_root="$2"; shift 2 ;;
    --stage) stage="$2"; shift 2 ;;
    --jobs) jobs="$2"; shift 2 ;;
    --skip-complete) skip_complete=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -d "$trace_root" ]] || { echo "error: missing --trace-root" >&2; exit 2; }
[[ -n "$out_root" ]] || { echo "error: --out-root is required" >&2; exit 2; }
[[ "$jobs" =~ ^[1-9][0-9]*$ ]] || { echo "error: --jobs must be positive" >&2; exit 2; }
case "$stage" in
  current64|literal16k|fourset64k|all) ;;
  *) echo "error: invalid --stage $stage" >&2; exit 2 ;;
esac

manifest="$repo_root/configs/c2p-cache/paper16_workloads.tsv"
diagnostic="$repo_root/configs/c2p-cache/peer-locality-diagnostic.config"
six_cases="hotspot1,gaussian,lud,sgemm,3mm,gemm"

run_stage() {
  local label="$1" cases="$2" overlay="$3" invalid_case="${4:-}"
  local result_root="$out_root/$label"
  local runner=("$repo_root/scripts/run_c2p_paper16.sh"
    --trace-root "$trace_root" --out-root "$result_root"
    --modes oracle --oracle-config-extra "$diagnostic" --jobs "$jobs")
  [[ -n "$cases" ]] && runner+=(--case "$cases")
  [[ -n "$overlay" ]] && runner+=(--config-extra "$overlay")
  (( skip_complete )) && runner+=(--skip-complete)
  local run_status=0
  "${runner[@]}" || run_status=$?

  # The literal 16-KiB Gaussian replay is a documented baseline deadlock:
  # it reproduces without the observation overlay and without C2P.  Retain
  # that cell as invalid rather than pretending it passed, while allowing the
  # other independent geometry cases to receive their normal invariant audit.
  if (( run_status )); then
    [[ -n "$invalid_case" ]] || return "$run_status"
    local invalid_out="$result_root/$invalid_case/oracle/run.out"
    [[ -f "$invalid_out" ]] &&
      grep -q 'deadlock detected' "$invalid_out" || {
        echo "error: $label failed outside its documented $invalid_case deadlock" >&2
        return "$run_status"
      }
  fi

  local analyzer=(python3 "$repo_root/scripts/analyze_c2p_peer_locality.py"
    --manifest "$manifest" --root "$label=$result_root"
    --out-dir "$result_root/analysis")
  if [[ -n "$invalid_case" ]]; then
    local audit_cases=()
    local case
    IFS=',' read -ra audit_cases <<< "$cases"
    local retained_cases=()
    for case in "${audit_cases[@]}"; do
      [[ "$case" == "$invalid_case" ]] || retained_cases+=("$case")
    done
    analyzer+=(--case "$(IFS=,; echo "${retained_cases[*]}")")
    mkdir -p "$result_root/analysis"
    {
      echo 'case,status,reason'
      echo "$invalid_case,INVALID_BASELINE_DEADLOCK,documented literal-16KiB baseline deadlock"
    } > "$result_root/analysis/invalid_geometry_cases.csv"
  elif [[ -n "$cases" ]]; then
    analyzer+=(--case "$cases")
  fi
  "${analyzer[@]}"
}

if [[ "$stage" == current64 || "$stage" == all ]]; then
  run_stage current64 "" ""
fi
if [[ "$stage" == literal16k || "$stage" == all ]]; then
  run_stage literal16k "$six_cases" \
    "$repo_root/configs/c2p-cache/paper-table-l1-16k-literal.config" gaussian
fi
if [[ "$stage" == fourset64k || "$stage" == all ]]; then
  run_stage fourset64k "$six_cases" \
    "$repo_root/configs/c2p-cache/paper-table-l1-4set-64k.config"
fi
