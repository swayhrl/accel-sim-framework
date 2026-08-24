#!/usr/bin/env bash
# Run matched C2P replays with and without the default-off 4-SM locality
# observer.  The analyzer rejects any timing or base-C2P counter difference.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_c2p_locality_observe.sh --out-root DIR
       [--trace-root DIR] [--v100-stage DIR] [--case CASE[,CASE...]] [--jobs N]

Each selected workload runs matched canonical C2P control and locality-observe
replays.  The observer must not alter timing, candidate selection, or fallback.
EOF
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out_root=""
trace_root="/workspace/worktrees/accel-sim-decoupled-l2/hw_run"
v100_stage="/workspace/worktrees/accel-sim-c2p-cache/hw_run/c2p-v100-baseline-compat-smoke-v2-20260822/stage"
selected_cases=""
jobs=1
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out-root) out_root="$2"; shift 2 ;;
    --trace-root) trace_root="$2"; shift 2 ;;
    --v100-stage) v100_stage="$2"; shift 2 ;;
    --case) selected_cases="$2"; shift 2 ;;
    --jobs) jobs="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -n "$out_root" ]] || { echo "error: --out-root is required" >&2; exit 2; }
[[ "$jobs" =~ ^[1-9][0-9]*$ ]] || { echo "error: positive --jobs required" >&2; exit 2; }
[[ -n "${C2P_GPGPUSIM_ROOT:-}" ]] || {
  echo "error: set C2P_GPGPUSIM_ROOT to the matching backend worktree" >&2; exit 2;
}

base_config="$C2P_GPGPUSIM_ROOT/configs/tested-cfgs/SM7_QV100/gpgpusim.config"
trace_config="$repo_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
paper_config="$repo_root/configs/c2p-cache/paper-table.config"
observe_config="$repo_root/configs/c2p-cache/c2p-locality-observe.config"
canonical_manifest="$repo_root/configs/c2p-cache/paper16_workloads.tsv"
extension_manifest="$repo_root/configs/c2p-cache/v100_extension_workloads.tsv"
for path in "$base_config" "$trace_config" "$paper_config" "$observe_config" \
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
      --out-dir "$out_root/$case_name/$variant")
  [[ "$variant" == observe ]] &&
      args+=(--mode-config-extra "$observe_config")
  "$repo_root/scripts/run_c2p_cache_cases.sh" "${args[@]}"
}

run_pair() {
  local case_name="$1" trace="$2" status=0
  local lock_root="$out_root/.pair_locks" lock_fd
  mkdir -p "$lock_root"
  exec {lock_fd}>"$lock_root/$case_name.lock"
  flock "$lock_fd"
  [[ -f "$trace" ]] || { echo "missing trace: $trace" >&2; return 2; }
  run_one "$case_name" "$trace" control \
      >"$out_root/$case_name.control.driver.log" 2>&1 &
  local control_pid=$!
  run_one "$case_name" "$trace" observe \
      >"$out_root/$case_name.observe.driver.log" 2>&1 &
  local observe_pid=$!
  wait "$control_pid" || status=1
  wait "$observe_pid" || status=1
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
  run_pair "$case_name" "$trace" &
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
python3 "$repo_root/scripts/analyze_c2p_locality.py" --root "$out_root" \
  --case "$case_list" --csv "$out_root/locality.csv" \
  --markdown "$out_root/locality.md"
