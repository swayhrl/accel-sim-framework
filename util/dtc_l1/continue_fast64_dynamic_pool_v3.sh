#!/usr/bin/env bash
# Future-only continuation for a pool whose controller exited after dispatch.
# It adopts exactly one already immutable-dispatched row, strictly validates its
# natural terminal, and then refills only fresh namespaces.  It never signals,
# restarts, or changes the adopted execution.
set -euo pipefail

usage() {
  echo "usage: $0 --stage N --modes BASE[,IO[,OO]] --classification LABEL --cpus N[,N...] --workloads W[,W...] --adopt-name NAME --adopt-workload W --adopt-mode BASE|IO|OO --adopt-cpu N [--framework-scientific-config-source-sha SHA] [--poll-seconds N] [--dry-run]" >&2
  exit 2
}

stage= modes= classification= cpus= workloads= adopt_name= adopt_workload= adopt_mode= adopt_cpu=
poll_seconds=30 dry_run=0
framework=037f008b330eb230353b60edf126d6be9f45afdc
while [ "$#" -gt 0 ]; do
  case "$1" in
    --stage) stage=${2:-}; shift 2 ;;
    --modes) modes=${2:-}; shift 2 ;;
    --classification) classification=${2:-}; shift 2 ;;
    --cpus) cpus=${2:-}; shift 2 ;;
    --workloads) workloads=${2:-}; shift 2 ;;
    --adopt-name) adopt_name=${2:-}; shift 2 ;;
    --adopt-workload) adopt_workload=${2:-}; shift 2 ;;
    --adopt-mode) adopt_mode=${2:-}; shift 2 ;;
    --adopt-cpu) adopt_cpu=${2:-}; shift 2 ;;
    --framework-scientific-config-source-sha) framework=${2:-}; shift 2 ;;
    --poll-seconds) poll_seconds=${2:-}; shift 2 ;;
    --dry-run) dry_run=1; shift ;;
    *) usage ;;
  esac
done
test -n "$stage" && test -n "$modes" && test -n "$classification" && test -n "$cpus" && \
  test -n "$workloads" && test -n "$adopt_name" && test -n "$adopt_workload" && \
  test -n "$adopt_mode" && test -n "$adopt_cpu" || usage
[[ "$stage" =~ ^[0-9]+$ ]] && [[ "$poll_seconds" =~ ^[1-9][0-9]*$ ]] || usage
case "$adopt_mode" in BASE|IO|OO) ;; *) usage ;; esac

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs=/workspace/fast64-runs
manifest="$repo/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
dispatcher="$repo/util/dtc_l1/dispatch_fast64_precomputed_row_v2.sh"
validator="$repo/util/dtc_l1/validate_fast64_trace_row_alias_v3.py"
core=bbcbb5e7565417102087bc80b14c349b4e568c05
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
runtime=6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041
test -x "$dispatcher" && test -x "$validator" && test -r "$manifest"
git -C "$repo" cat-file -e "$framework^{commit}"

IFS=, read -r -a cpu_list <<<"$cpus"
test "${#cpu_list[@]}" -gt 0
declare -A seen_cpu=()
for cpu in "${cpu_list[@]}"; do
  [[ "$cpu" =~ ^[0-9]+$ ]] || usage
  test -z "${seen_cpu[$cpu]:-}" || { echo "DUPLICATE_CPU $cpu" >&2; exit 2; }
  seen_cpu[$cpu]=1
done
test -n "${seen_cpu[$adopt_cpu]:-}" || { echo "ADOPT_CPU_NOT_IN_POOL $adopt_cpu" >&2; exit 2; }
IFS=, read -r -a mode_list <<<"$modes"
for mode in "${mode_list[@]}"; do case "$mode" in BASE|IO|OO) ;; *) usage ;; esac; done
IFS=, read -r -a workload_list <<<"$workloads"
test "${#workload_list[@]}" -gt 0
for workload in "${workload_list[@]}"; do
  test -n "$(awk -F '\t' -v w="$workload" 'tolower($1)==tolower(w) {print $1;exit}' "$manifest")" || {
    echo "UNKNOWN_FROZEN_WORKLOAD $workload" >&2; exit 2;
  }
done
test -n "$(awk -F '\t' -v w="$adopt_workload" 'tolower($1)==tolower(w) {print $1;exit}' "$manifest")" || {
  echo "UNKNOWN_ADOPTED_WORKLOAD $adopt_workload" >&2; exit 2;
}

config_for_mode() {
  case "$1" in
    BASE) printf '%s\n' "$repo/configs/dtc_l1/fast64/FAST64_BASE.config" ;;
    IO) printf '%s\n' "$repo/configs/dtc_l1/fast64/FAST64_IO.config" ;;
    OO) printf '%s\n' "$repo/configs/dtc_l1/fast64/FAST64_OO.config" ;;
  esac
}
config_id_for_mode() { printf 'FAST64_%s_A1\n' "$1"; }
value() { awk -F '\t' -v key="$2" '$1==key {n++;v=$2} END {if(n==1)print v;else exit 1}' "$1"; }
supervisor_from_receipt() {
  awk -F '\t' '
    NR == 1 { for (i = 1; i <= NF; ++i) if ($i == "supervisor_pid") col = i; next }
    NR == 2 && col { print $col; exit }
  ' "$1"
}
validate_terminal() {
  local name=$1 workload=$2 mode=$3 run=$4 config=$5 output=$6
  test -f "$run/RUN_TERMINAL.tsv" || { echo "MISSING_TERMINAL_RECEIPT $name" >&2; return 1; }
  test "$(value "$run/RUN_TERMINAL.tsv" receipt_type)" = TERMINAL || return 1
  test "$(value "$run/RUN_TERMINAL.tsv" simulator_exit_status)" = 0 || { echo "NONZERO_TERMINAL $name" >&2; return 1; }
  test "$(value "$run/RUN_MANIFEST.tsv" simulator_exit_status)" = 0 || { echo "MANIFEST_TERMINAL_MISMATCH $name" >&2; return 1; }
  test "$(value "$run/RUN_MANIFEST.tsv" core_source_head)" = "$core" || { echo "CORE_IDENTITY_MISMATCH $name" >&2; return 1; }
  test "$(value "$run/RUN_MANIFEST.tsv" framework_scientific_config_source_sha)" = "$framework" || { echo "FRAMEWORK_IDENTITY_MISMATCH $name" >&2; return 1; }
  test "$(value "$run/RUN_MANIFEST.tsv" observer_overlay_sha256)" = "$observer" || { echo "OBSERVER_IDENTITY_MISMATCH $name" >&2; return 1; }
  test "$(value "$run/RUN_MANIFEST.tsv" simulator_sha256)" = "$runtime" || { echo "RUNTIME_IDENTITY_MISMATCH $name" >&2; return 1; }
  test "$(value "$run/RUN_MANIFEST.tsv" result_classification)" = "$classification" || { echo "CLASSIFICATION_MISMATCH $name" >&2; return 1; }
  test ! -e "$output" || { echo "VALIDATION_OUTPUT_EXISTS $output" >&2; return 1; }
  python3 "$validator" --run-dir "$run" --workload-id "$workload" --mode "$mode" \
    --config-id "$(config_id_for_mode "$mode")" --config-file "$config" --core-sha "$core" \
    --framework-sha "$framework" --observer-sha "$observer" --runtime-sha "$runtime" \
    --payload-manifest "$manifest" --classification "$classification" --require-immutable-attempt --output "$output"
  if rg -n -i 'assertion failed|fatal error|deadlock detected|output mismatch|segmentation fault' \
      "$run/simulator.stdout" "$run/simulator.stderr" "$run.launcher.log"; then
    echo "FORBIDDEN_FAILURE_SIGNATURE $name" >&2; return 1
  fi
}

adopt_run="$runs/$adopt_name"
adopt_receipt="$runs/$adopt_name.supervisor.tsv"
test -d "$adopt_run" && test -r "$adopt_receipt" || { echo "ADOPTED_ROW_MISSING $adopt_name" >&2; exit 1; }
test "$(awk -F '\t' 'NR==2 {print $1}' "$adopt_receipt")" = "$adopt_name" || { echo "ADOPT_NAME_MISMATCH" >&2; exit 1; }
[[ "$(supervisor_from_receipt "$adopt_receipt")" =~ ^[0-9]+$ ]] || { echo "ADOPT_SUPERVISOR_MISSING" >&2; exit 1; }
printf 'FAST64_V3_CONTINUATION_PLAN\tstage=%s\tframework=%s\tclassification=%s\tworkers=%s\tadopt=%s\ttasks=%s\n' \
  "$stage" "$framework" "$classification" "${#cpu_list[@]}" "$adopt_name" "${#workload_list[@]}"
if [ "$dry_run" = 1 ]; then exit 0; fi
mkdir -p "$runs/validated"

declare -A active=()
active[$adopt_name]="$adopt_workload|$adopt_mode|$adopt_cpu"
next=0
while [ "$next" -lt "${#workload_list[@]}" ] || [ "${#active[@]}" -gt 0 ]; do
  for name in "${!active[@]}"; do
    IFS='|' read -r workload mode cpu <<<"${active[$name]}"
    run="$runs/$name"
    if [ -f "$run/RUN_TERMINAL.tsv" ]; then
      validate_terminal "$name" "$workload" "$mode" "$run" "$(config_for_mode "$mode")" \
        "$runs/validated/$name.alias_v3.summary.json"
      unset 'active[$name]'
      printf 'FAST64_V3_CONTINUATION_VALIDATED\t%s\n' "$name"
    else
      supervisor=$(supervisor_from_receipt "$runs/$name.supervisor.tsv")
      test -n "$supervisor" && kill -0 "$supervisor" 2>/dev/null || {
        echo "LIVE_NAMESPACE_WITHOUT_TERMINAL_OR_SUPERVISOR $name" >&2; exit 1;
      }
    fi
  done
  while [ "$next" -lt "${#workload_list[@]}" ] && [ "${#active[@]}" -lt "${#cpu_list[@]}" ]; do
    workload=${workload_list[$next]}
    mode=BASE
    cpu=
    for candidate in "${cpu_list[@]}"; do
      busy=0
      for active_name in "${!active[@]}"; do IFS='|' read -r _ _ active_cpu <<<"${active[$active_name]}"; [ "$candidate" = "$active_cpu" ] && busy=1; done
      [ "$busy" = 0 ] && { cpu=$candidate; break; }
    done
    test -n "$cpu" || { echo NO_FREE_CPU_SLOT >&2; exit 1; }
    name="fast64_${stage}_${workload}_${mode,,}_cap8192_a1_v2"
    test ! -e "$runs/$name" || { echo "TARGET_EXISTS_REFUSE_RERUN $name" >&2; exit 1; }
    "$dispatcher" --name "$name" --workload "$workload" --mode "$mode" --config "$(config_for_mode "$mode")" --cpu "$cpu" \
      --classification "$classification" --framework-scientific-config-source-sha "$framework"
    active[$name]="$workload|$mode|$cpu"
    next=$((next + 1))
  done
  [ "${#active[@]}" -eq 0 ] || sleep "$poll_seconds"
done
printf 'FAST64_V3_CONTINUATION_COMPLETE\tstage=%s\tclassification=%s\n' "$stage" "$classification"
