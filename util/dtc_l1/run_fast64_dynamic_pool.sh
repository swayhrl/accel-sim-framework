#!/usr/bin/env bash
# Dynamic, exactly-once FAST64 acquisition pool.  A terminal row is strict
# validated before its physical CPU slot is refilled; a missing terminal state
# or validation failure is fail-closed and never causes a restart.
set -euo pipefail

usage() {
  echo "usage: $0 --stage N --modes BASE[,IO[,OO]] --classification LABEL --cpus N[,N...] [--workloads W[,W...]] [--poll-seconds N] [--dry-run]" >&2
  exit 2
}

stage= modes= classification= cpus= workloads= poll_seconds=30 dry_run=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --stage) stage=${2:-}; shift 2 ;;
    --modes) modes=${2:-}; shift 2 ;;
    --classification) classification=${2:-}; shift 2 ;;
    --cpus) cpus=${2:-}; shift 2 ;;
    --workloads) workloads=${2:-}; shift 2 ;;
    --poll-seconds) poll_seconds=${2:-}; shift 2 ;;
    --dry-run) dry_run=1; shift ;;
    *) usage ;;
  esac
done
test -n "$stage" && test -n "$modes" && test -n "$classification" && test -n "$cpus" || usage
[[ "$stage" =~ ^[0-9]+$ ]] || usage
[[ "$poll_seconds" =~ ^[1-9][0-9]*$ ]] || usage

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs_root=/workspace/fast64-runs
manifest="$repo_root/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
dispatcher="$repo_root/util/dtc_l1/dispatch_fast64_precomputed_row.sh"
validator="$repo_root/util/dtc_l1/validate_fast64_trace_row.py"
core=bbcbb5e7565417102087bc80b14c349b4e568c05
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
framework=$(git -C "$repo_root" rev-parse HEAD)
test -r "$manifest" && test -x "$dispatcher" && test -x "$validator"

IFS=, read -r -a cpu_list <<<"$cpus"
test "${#cpu_list[@]}" -gt 0
declare -A seen_cpu=()
for cpu in "${cpu_list[@]}"; do
  [[ "$cpu" =~ ^[0-9]+$ ]] || { echo "invalid CPU: $cpu" >&2; exit 2; }
  test -z "${seen_cpu[$cpu]:-}" || { echo "duplicate CPU: $cpu" >&2; exit 2; }
  seen_cpu[$cpu]=1
done

IFS=, read -r -a mode_list <<<"$modes"
for mode in "${mode_list[@]}"; do
  case "$mode" in BASE|IO|OO) ;; *) echo "invalid mode: $mode" >&2; exit 2 ;; esac
done
if [ -z "$workloads" ]; then
  workloads=$(awk -F '\t' 'NR > 1 { print $1 }' "$manifest" | paste -sd, -)
fi
IFS=, read -r -a workload_list <<<"$workloads"
test "${#workload_list[@]}" -gt 0
for workload in "${workload_list[@]}"; do
  test -n "$(awk -F '\t' -v w="$workload" '$1 == w {print $1; exit}' "$manifest")" || {
    echo "unknown frozen workload: $workload" >&2; exit 2;
  }
done

tasks=()
for workload in "${workload_list[@]}"; do
  for mode in "${mode_list[@]}"; do
    tasks+=("$workload|$mode")
  done
done
printf 'POOL_PLAN\tstage=%s\tframework=%s\tclassification=%s\tworkers=%s\ttasks=%s\n' \
  "$stage" "$framework" "$classification" "${#cpu_list[@]}" "${#tasks[@]}"

if [ "$dry_run" = 1 ]; then
  for task in "${tasks[@]}"; do printf 'POOL_TASK\t%s\n' "$task"; done
  exit 0
fi

mkdir -p "$runs_root/validated"
declare -A active=()
next=0

config_for_mode() {
  case "$1" in
    BASE) printf '%s\n' "$repo_root/configs/dtc_l1/fast64/FAST64_BASE.config" ;;
    IO) printf '%s\n' "$repo_root/configs/dtc_l1/fast64/FAST64_IO.config" ;;
    OO) printf '%s\n' "$repo_root/configs/dtc_l1/fast64/FAST64_OO.config" ;;
  esac
}

validate_terminal() {
  local name=$1 workload=$2 mode=$3 config=$4 run_dir=$5 output=$6
  test "$(awk -F '\t' '$1=="simulator_exit_status" {print $2}' "$run_dir/RUN_MANIFEST.tsv")" = 0 || {
    echo "NONZERO_OR_MISSING_TERMINAL $name" >&2; return 1;
  }
  test ! -e "$output" || { echo "VALIDATION_OUTPUT_EXISTS $output" >&2; return 1; }
  test "$(awk -F '\t' '$1=="core_source_head" {print $2}' "$run_dir/RUN_MANIFEST.tsv")" = "$core" || {
    echo "CORE_IDENTITY_MISMATCH $name" >&2; return 1;
  }
  test "$(awk -F '\t' '$1=="framework_source_head" {print $2}' "$run_dir/RUN_MANIFEST.tsv")" = "$framework" || {
    echo "FRAMEWORK_IDENTITY_MISMATCH $name" >&2; return 1;
  }
  test "$(awk -F '\t' '$1=="result_classification" {print $2}' "$run_dir/RUN_MANIFEST.tsv")" = "$classification" || {
    echo "CLASSIFICATION_MISMATCH $name" >&2; return 1;
  }
  test "$(awk -F '\t' '$1=="config_sha256" {print $2}' "$run_dir/RUN_MANIFEST.tsv")" = \
    "$(sha256sum "$config" | awk '{print $1}')" || {
    echo "CONFIG_IDENTITY_MISMATCH $name" >&2; return 1;
  }
  python3 "$validator" --run-dir "$run_dir" --workload-id "$workload" --mode "$mode" \
    --config-id "FAST64_${mode}_CAP8192_A1" --config-file "$config" \
    --core-sha "$core" --framework-sha "$framework" --observer-sha "$observer" --payload-manifest "$manifest" \
    --classification "$classification" --output "$output"
}

while [ "$next" -lt "${#tasks[@]}" ] || [ "${#active[@]}" -gt 0 ]; do
  # Close terminal rows before refilling.  A non-terminal namespace remains
  # occupied even if its OS process later disappears, avoiding accidental rerun.
  for name in "${!active[@]}"; do
    IFS='|' read -r workload mode cpu <<<"${active[$name]}"
    run_dir="$runs_root/$name"
    if awk -F '\t' '$1=="simulator_exit_status" {found=1} END {exit !found}' "$run_dir/RUN_MANIFEST.tsv"; then
      config=$(config_for_mode "$mode")
      validate_terminal "$name" "$workload" "$mode" "$config" "$run_dir" \
        "$runs_root/validated/$name.summary.json"
      unset 'active[$name]'
      echo "POOL_VALIDATED $name"
    else
      supervisor=$(awk -F '\t' '$1=="supervisor_pid" {print $2}' "$runs_root/$name.supervisor.tsv")
      if ! kill -0 "$supervisor" 2>/dev/null; then
        echo "LIVE_NAMESPACE_WITHOUT_TERMINAL_OR_SUPERVISOR $name" >&2
        exit 1
      fi
    fi
  done

  while [ "$next" -lt "${#tasks[@]}" ] && [ "${#active[@]}" -lt "${#cpu_list[@]}" ]; do
    IFS='|' read -r workload mode <<<"${tasks[$next]}"
    cpu=
    for candidate_cpu in "${cpu_list[@]}"; do
      busy=0
      for active_name in "${!active[@]}"; do
        IFS='|' read -r _ _ active_cpu <<<"${active[$active_name]}"
        if [ "$active_cpu" = "$candidate_cpu" ]; then busy=1; break; fi
      done
      if [ "$busy" = 0 ]; then cpu=$candidate_cpu; break; fi
    done
    test -n "$cpu" || { echo "NO_FREE_CPU_SLOT" >&2; exit 1; }
    mode_lower=${mode,,}
    name="fast64_${stage}_${workload}_${mode_lower}_cap8192_a1"
    run_dir="$runs_root/$name"
    test ! -e "$run_dir" || { echo "TARGET_EXISTS_REFUSE_RERUN $run_dir" >&2; exit 1; }
    config=$(config_for_mode "$mode")
    "$dispatcher" --name "$name" --workload "$workload" --mode "$mode" --config "$config" \
      --cpu "$cpu" --classification "$classification" --framework-source-head "$framework"
    active[$name]="$workload|$mode|$cpu"
    next=$((next + 1))
  done

  [ "${#active[@]}" -eq 0 ] || sleep "$poll_seconds"
done

echo "POOL_COMPLETE stage=$stage classification=$classification"
