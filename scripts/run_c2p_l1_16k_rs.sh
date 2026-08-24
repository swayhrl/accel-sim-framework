#!/usr/bin/env bash
# Run only the paper R/S measurements at the literal 16KiB Table-1 L1 point.
# Each workload gets baseline+observational-oracle at L2=200 and baseline at
# L2=50.  No sharing-policy performance matrix is run here.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_c2p_l1_16k_rs.sh --paper16-trace-root DIR --v100-trace-root DIR
       --out-root DIR [--jobs N] [--case CASE[,CASE...]] [--skip-complete]

The manifest includes the 16 paper workloads and the eight available V100
extension traces.  --jobs counts workload pairs; each pair has an L2=200
(baseline,oracle) worker and an L2=50 baseline worker, so at most 2*jobs
simulator processes execute concurrently.
EOF
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
manifest="$repo_root/configs/c2p-cache/rs_l1_capacity_workloads.tsv"
paper16_root=""
v100_root=""
out_root=""
jobs=1
cases=""
skip_complete=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --paper16-trace-root) paper16_root="$2"; shift 2 ;;
    --v100-trace-root) v100_root="$2"; shift 2 ;;
    --out-root) out_root="$2"; shift 2 ;;
    --jobs) jobs="$2"; shift 2 ;;
    --case) cases="$2"; shift 2 ;;
    --skip-complete) skip_complete=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -d "$paper16_root" && -d "$v100_root" && -n "$out_root" ]] || {
  echo "error: both trace roots and --out-root are required" >&2; exit 2;
}
[[ "$jobs" =~ ^[1-9][0-9]*$ ]] || { echo "error: --jobs must be positive" >&2; exit 2; }
[[ -n "${C2P_GPGPUSIM_ROOT:-}" ]] || { echo "error: set C2P_GPGPUSIM_ROOT" >&2; exit 2; }

base_config="$repo_root/gpu-simulator/gpgpu-sim/configs/tested-cfgs/SM7_QV100/gpgpusim.config"
[[ -f "$base_config" ]] || base_config="$C2P_GPGPUSIM_ROOT/configs/tested-cfgs/SM7_QV100/gpgpusim.config"
[[ -f "$base_config" ]] || { echo "error: missing QV100 base config" >&2; exit 2; }

case_selected() {
  [[ -z "$cases" ]] && return 0
  local candidate
  IFS=',' read -ra selected <<< "$cases"
  for candidate in "${selected[@]}"; do [[ "$candidate" == "$1" ]] && return 0; done
  return 1
}

run_case() {
  local case_name="$1" trace="$2"
  local -a common=(
    --trace "$trace" --config "$base_config"
    --config-extra "$repo_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
    --config-extra "$repo_root/configs/c2p-cache/paper-table.config"
    --config-extra "$repo_root/configs/c2p-cache/paper-table-l1-16k.config"
    --strip-mem-addr-mapping
  )
  (( skip_complete )) && common+=(--skip-complete)
  printf 'START case=%s time=%s\n' "$case_name" "$(date --iso-8601=seconds)"
  "$repo_root/scripts/run_c2p_cache_cases.sh" "${common[@]}" \
    --modes baseline,oracle --out-dir "$out_root/$case_name/l2_200" \
    >"$out_root/$case_name.l2_200.driver.log" 2>&1 &
  local main_pid=$!
  "$repo_root/scripts/run_c2p_cache_cases.sh" "${common[@]}" \
    --config-extra "$repo_root/configs/c2p-cache/paper-table-l2-50.config" \
    --modes baseline --out-dir "$out_root/$case_name/l2_50" \
    >"$out_root/$case_name.l2_50.driver.log" 2>&1 &
  local fast_pid=$!
  wait "$main_pid"
  wait "$fast_pid"
  printf 'PASS case=%s time=%s\n' "$case_name" "$(date --iso-8601=seconds)"
}

mkdir -p "$out_root"
# Fail before launching any replay: a typo in a late manifest row must not
# leave a partial experiment queue running beside a clear configuration error.
while IFS=$'\t' read -r case_name suite abbr input_label trace_kind trace_rel; do
  [[ -z "$case_name" || "$case_name" == "case" || "$case_name" == \#* ]] && continue
  case_selected "$case_name" || continue
  case "$trace_kind" in
    paper16) trace="$paper16_root/$trace_rel/kernelslist.g" ;;
    v100ext) trace="$v100_root/$trace_rel/kernelslist.g" ;;
    *) echo "error: unknown trace root '$trace_kind' for $case_name" >&2; exit 2 ;;
  esac
  [[ -f "$trace" ]] || { echo "error: missing trace for $case_name: $trace" >&2; exit 2; }
done < "$manifest"

active=0
status=0
while IFS=$'\t' read -r case_name suite abbr input_label trace_kind trace_rel; do
  [[ -z "$case_name" || "$case_name" == "case" || "$case_name" == \#* ]] && continue
  case_selected "$case_name" || continue
  case "$trace_kind" in
    paper16) trace="$paper16_root/$trace_rel/kernelslist.g" ;;
    v100ext) trace="$v100_root/$trace_rel/kernelslist.g" ;;
    *) echo "error: unknown trace root '$trace_kind' for $case_name" >&2; exit 2 ;;
  esac
  run_case "$case_name" "$trace" >"$out_root/$case_name.queue.log" 2>&1 &
  active=$((active + 1))
  if (( active >= jobs )); then
    wait -n || status=1
    active=$((active - 1))
  fi
done < "$manifest"
while (( active > 0 )); do
  wait -n || status=1
  active=$((active - 1))
done
exit "$status"
