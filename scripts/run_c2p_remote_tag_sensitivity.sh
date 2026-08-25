#!/usr/bin/env bash
# Run the staged global C2P remote-tag 7-to-14-cycle sensitivity.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_c2p_remote_tag_sensitivity.sh --out-root DIR --phase PHASE
       [--trace-root DIR] [--v100-stage DIR] [--case CASE[,CASE...]] [--jobs N]

PHASE is one of: canonical, locality, admission.

canonical compares ordinary C2P at remote tag lookup 7 and 14 cycles.
locality compares the same points with 4-SM local-first candidate ordering.
admission compares matched local-first control/policy pairs at both points.
All points retain remote return latency=2 and shared L2 latency=200.
EOF
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out_root=""
phase=""
trace_root="/workspace/worktrees/accel-sim-decoupled-l2/hw_run"
v100_stage="/workspace/worktrees/accel-sim-c2p-cache/hw_run/c2p-v100-baseline-compat-smoke-v2-20260822/stage"
selected_cases=""
jobs=1
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out-root) out_root="$2"; shift 2 ;;
    --phase) phase="$2"; shift 2 ;;
    --trace-root) trace_root="$2"; shift 2 ;;
    --v100-stage) v100_stage="$2"; shift 2 ;;
    --case) selected_cases="$2"; shift 2 ;;
    --jobs) jobs="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ -n "$out_root" ]] || { echo "error: --out-root is required" >&2; exit 2; }
case "$phase" in canonical|locality|admission) ;; *)
  echo "error: --phase must be canonical, locality, or admission" >&2; exit 2 ;;
esac
[[ "$jobs" =~ ^[1-9][0-9]*$ ]] || { echo "error: positive --jobs required" >&2; exit 2; }
[[ -n "${C2P_GPGPUSIM_ROOT:-}" ]] || {
  echo "error: set C2P_GPGPUSIM_ROOT to the matching backend worktree" >&2; exit 2;
}

base_config="$C2P_GPGPUSIM_ROOT/configs/tested-cfgs/SM7_QV100/gpgpusim.config"
trace_config="$repo_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
paper_config="$repo_root/configs/c2p-cache/paper-table.config"
locality_config="$repo_root/configs/c2p-cache/c2p-locality-near-outer-d0.config"
order_config="$repo_root/configs/c2p-cache/c2p-locality-order.config"
policy_config="$repo_root/configs/c2p-cache/c2p-outer-admission.config"
remote14_config="$repo_root/configs/c2p-cache/c2p-remote-tag-14.config"
canonical_manifest="$repo_root/configs/c2p-cache/paper16_workloads.tsv"
extension_manifest="$repo_root/configs/c2p-cache/v100_extension_workloads.tsv"
for path in "$base_config" "$trace_config" "$paper_config" "$locality_config" \
            "$order_config" "$policy_config" "$remote14_config" \
            "$canonical_manifest" "$extension_manifest"; do
  [[ -f "$path" ]] || { echo "error: missing required input: $path" >&2; exit 2; }
done

case_selected() {
  [[ -z "$selected_cases" ]] && return 0
  local item
  IFS=',' read -ra items <<< "$selected_cases"
  for item in "${items[@]}"; do [[ "$item" == "$1" ]] && return 0; done
  return 1
}

run_one() {
  local case_name="$1" trace="$2" variant="$3"
  local args=(--trace "$trace" --config "$base_config"
      --config-extra "$trace_config" --config-extra "$paper_config"
      --strip-mem-addr-mapping --skip-complete --modes c2p
      --out-dir "$out_root/$phase/$case_name/$variant")
  case "$phase:$variant" in
    canonical:tag7) ;;
    canonical:tag14) args+=(--mode-config-extra "$remote14_config") ;;
    locality:tag7) args+=(--mode-config-extra "$locality_config") ;;
    locality:tag14) args+=(--mode-config-extra "$locality_config" --mode-config-extra "$remote14_config") ;;
    admission:control7) args+=(--mode-config-extra "$order_config") ;;
    admission:policy7) args+=(--mode-config-extra "$order_config" --mode-config-extra "$policy_config") ;;
    admission:control14) args+=(--mode-config-extra "$order_config" --mode-config-extra "$remote14_config") ;;
    admission:policy14) args+=(--mode-config-extra "$order_config" --mode-config-extra "$policy_config" --mode-config-extra "$remote14_config") ;;
    *) echo "error: invalid phase/variant $phase/$variant" >&2; return 2 ;;
  esac
  "$repo_root/scripts/run_c2p_cache_cases.sh" "${args[@]}"
}

run_case() {
  local case_name="$1" trace="$2" status=0 variant lock_root lock_fd
  local -a variants=()
  case "$phase" in
    canonical|locality) variants=(tag7 tag14) ;;
    admission) variants=(control7 policy7 control14 policy14) ;;
  esac
  lock_root="$out_root/.${phase}_locks"
  mkdir -p "$lock_root"
  exec {lock_fd}>"$lock_root/$case_name.lock"
  flock "$lock_fd"
  [[ -f "$trace" ]] || { echo "missing trace: $trace" >&2; return 2; }
  local -a pids=()
  for variant in "${variants[@]}"; do
    run_one "$case_name" "$trace" "$variant" \
        >"$out_root/$case_name.$variant.driver.log" 2>&1 &
    pids+=("$!")
  done
  for pid in "${pids[@]}"; do wait "$pid" || status=1; done
  return "$status"
}

mkdir -p "$out_root"
declare -a cases=()
while IFS=$'\t' read -r case_name _ _ _ trace_rel; do
  [[ -z "$case_name" || "$case_name" == case || "$case_name" == \#* ]] && continue
  case_selected "$case_name" || continue
  cases+=("$case_name|$trace_root/$trace_rel/kernelslist.g")
done < "$canonical_manifest"
while IFS=$'\t' read -r case_name _ _ _ _ _ kernelslist_rel; do
  [[ -z "$case_name" || "$case_name" == case || "$case_name" == \#* ]] && continue
  case_selected "$case_name" || continue
  cases+=("$case_name|$v100_stage/$case_name/$kernelslist_rel")
done < "$extension_manifest"
(( ${#cases[@]} != 0 )) || { echo "error: no selected workloads" >&2; exit 2; }

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
(( status == 0 )) || exit "$status"

case_list=""
for spec in "${cases[@]}"; do
  IFS='|' read -r case_name _ <<< "$spec"
  case_list+="${case_list:+,}$case_name"
done
python3 "$repo_root/scripts/analyze_c2p_remote_tag_sensitivity.py" \
  --root "$out_root/$phase" --phase "$phase" --case "$case_list" \
  --csv "$out_root/$phase/$phase.csv" --markdown "$out_root/$phase/$phase.md"
