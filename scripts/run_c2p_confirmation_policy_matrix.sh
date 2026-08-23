#!/usr/bin/env bash
# Replay matched exhaustive, PC-hash, and address/topology C2P+ policies.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_c2p_confirmation_policy_matrix.sh --out-root DIR
       [--trace-root DIR] [--v100-stage DIR] [--case CASE[,CASE...]] [--no-analyze]
       [--jobs N] [--build]

Each selected workload runs three C2P+ modes from the same frontend/backend
build: exhaustive control, PC-hash confirmation package, and capacity-matched
address-region x requester-cluster confirmation package.  The canonical 16
and V100 extension eight are kept in separate output tiers.
EOF
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out_root=""
trace_root="/workspace/worktrees/accel-sim-decoupled-l2/hw_run"
v100_stage="/workspace/worktrees/accel-sim-c2p-cache/hw_run/c2p-v100-baseline-compat-smoke-v2-20260822/stage"
selected_cases=""
run_analysis=1
jobs=1
build=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out-root) out_root="$2"; shift 2 ;;
    --trace-root) trace_root="$2"; shift 2 ;;
    --v100-stage) v100_stage="$2"; shift 2 ;;
    --case) selected_cases="$2"; shift 2 ;;
    --no-analyze) run_analysis=0; shift ;;
    --jobs) jobs="$2"; shift 2 ;;
    --build) build=1; shift ;;
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
control_config="$repo_root/configs/c2p-cache/c2p-adaptive-package-control.config"
pc_config="$repo_root/configs/c2p-cache/c2p-adaptive-package-policy.config"
addr_config="$repo_root/configs/c2p-cache/c2p-adaptive-package-addr-topology-policy.config"
canonical_manifest="$repo_root/configs/c2p-cache/paper16_workloads.tsv"
extension_manifest="$repo_root/configs/c2p-cache/v100_extension_workloads.tsv"
for path in "$base_config" "$trace_config" "$paper_config" "$control_config" \
            "$pc_config" "$addr_config" "$canonical_manifest" "$extension_manifest"; do
  [[ -f "$path" ]] || { echo "error: missing required input: $path" >&2; exit 2; }
done

case_selected() {
  [[ -z "$selected_cases" ]] && return 0
  local item
  IFS=',' read -ra items <<< "$selected_cases"
  for item in "${items[@]}"; do [[ "$item" == "$1" ]] && return 0; done
  return 1
}

if (( build )); then
  # The C2P configuration class lives in the backend ABI, so rebuild this
  # small frontend once before parallel children copy their executable.
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
  local tier="$1" case_name="$2" trace="$3" variant="$4" overlay="$5"
  "$repo_root/scripts/run_c2p_cache_cases.sh" --trace "$trace" --config "$base_config" \
      --config-extra "$trace_config" --config-extra "$paper_config" \
      --mode-config-extra "$overlay" --strip-mem-addr-mapping --skip-complete \
      --modes c2p --out-dir "$out_root/$tier/$case_name/$variant"
}

run_triplet() {
  local tier="$1" case_name="$2" trace="$3" status=0
  # A campaign may be extended by a second launcher while its original
  # manifest walk is still live.  Serialize just this workload so both
  # launchers cannot copy/run the same three policy directories at once.
  # Once the first triplet exits, --skip-complete below makes the waiter a
  # cheap no-op instead of a duplicate replay.
  local lock_root="$out_root/.triplet_locks"
  local lock_fd
  mkdir -p "$lock_root"
  exec {lock_fd}>"$lock_root/$tier.$case_name.lock"
  flock "$lock_fd"
  [[ -f "$trace" ]] || { echo "missing trace: $trace" >&2; return 2; }
  run_one "$tier" "$case_name" "$trace" control "$control_config" \
      >"$out_root/$tier/$case_name.control.driver.log" 2>&1 &
  local control_pid=$!
  run_one "$tier" "$case_name" "$trace" pc "$pc_config" \
      >"$out_root/$tier/$case_name.pc.driver.log" 2>&1 &
  local pc_pid=$!
  run_one "$tier" "$case_name" "$trace" addr "$addr_config" \
      >"$out_root/$tier/$case_name.addr.driver.log" 2>&1 &
  local addr_pid=$!
  wait "$control_pid" || status=1
  wait "$pc_pid" || status=1
  wait "$addr_pid" || status=1
  return "$status"
}

mkdir -p "$out_root/canonical" "$out_root/extension"
declare -a cases=()
while IFS=$'\t' read -r case_name _ _ _ trace_rel; do
  [[ -z "$case_name" || "$case_name" == case || "$case_name" == \#* ]] && continue
  case_selected "$case_name" || continue
  cases+=("canonical|$case_name|$trace_root/$trace_rel/kernelslist.g")
done < "$canonical_manifest"
while IFS=$'\t' read -r case_name _ _ _ _ _ kernelslist_rel; do
  [[ -z "$case_name" || "$case_name" == case || "$case_name" == \#* ]] && continue
  case_selected "$case_name" || continue
  cases+=("extension|$case_name|$v100_stage/$case_name/$kernelslist_rel")
done < "$extension_manifest"
(( ${#cases[@]} != 0 )) || { echo "error: no selected workloads" >&2; exit 2; }

status=0
active=0
for spec in "${cases[@]}"; do
  IFS='|' read -r tier case_name trace <<< "$spec"
  run_triplet "$tier" "$case_name" "$trace" &
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

if (( run_analysis )); then
  analyze_args=(--root "$out_root" --csv "$out_root/policy_matrix.csv"
                --markdown "$out_root/policy_matrix.md")
  [[ -n "$selected_cases" ]] && analyze_args+=(--case "$selected_cases")
  python3 "$repo_root/scripts/analyze_c2p_confirmation_policy_matrix.py" "${analyze_args[@]}"
fi
