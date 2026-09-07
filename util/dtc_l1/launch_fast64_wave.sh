#!/usr/bin/env bash
# Dispatch one frozen FAST64 mode wave.  This launcher never kills, replaces,
# or overwrites a prior run; each requested row needs an empty run namespace.
set -euo pipefail

usage() {
  echo "usage: $0 --stage N --mode BASE|IO|OO --simulator PATH --runs-root PATH --cpus N[,N...] [--workloads W[,W...]] [--dry-run]" >&2
  exit 2
}

stage= mode= simulator= runs_root= cpus= workloads=
dry_run=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --stage) stage=${2:-}; shift 2 ;;
    --mode) mode=${2:-}; shift 2 ;;
    --simulator) simulator=${2:-}; shift 2 ;;
    --runs-root) runs_root=${2:-}; shift 2 ;;
    --cpus) cpus=${2:-}; shift 2 ;;
    --workloads) workloads=${2:-}; shift 2 ;;
    --dry-run) dry_run=1; shift ;;
    *) usage ;;
  esac
done

test -n "$stage" && test -n "$mode" && test -n "$simulator" && \
  test -n "$runs_root" && test -n "$cpus" || usage
[[ "$stage" =~ ^[0-9]+$ ]] || usage
case "$mode" in BASE|IO|OO) ;; *) usage ;; esac
test -x "$simulator"

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
manifest="$repo_root/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
runner="$repo_root/util/dtc_l1/run_fast64_trace.sh"
test -r "$manifest" && test -x "$runner"
config="$repo_root/configs/dtc_l1/fast64/FAST64_${mode}.config"
test -r "$config"

if [ -z "$workloads" ]; then
  workloads=$(awk -F '\t' 'NR > 1 { print $1 }' "$manifest" | paste -sd, -)
fi
IFS=, read -r -a workload_list <<<"$workloads"
IFS=, read -r -a cpu_list <<<"$cpus"
test "${#workload_list[@]}" -gt 0
test "${#cpu_list[@]}" -ge "${#workload_list[@]}" || {
  echo "need at least one explicit CPU per requested workload" >&2
  exit 2
}

for index in "${!workload_list[@]}"; do
  workload=${workload_list[$index]}
  cpu=${cpu_list[$index]}
  [[ "$cpu" =~ ^[0-9]+$ ]] || { echo "invalid CPU: $cpu" >&2; exit 2; }
  trace_root=$(awk -F '\t' -v workload="$workload" '$1 == workload { print $2; exit }' "$manifest")
  test -n "$trace_root" || { echo "unknown frozen workload: $workload" >&2; exit 2; }
  trace="$trace_root/kernelslist.g"
  test -r "$trace" || { echo "missing frozen trace list: $trace" >&2; exit 2; }
  mode_lower=${mode,,}
  run_name="fast64_${stage}_${workload}_${mode_lower}_cap8192_a1"
  run_dir="$runs_root/$run_name"
  test ! -e "$run_dir" || { echo "refusing duplicate/overwrite: $run_dir" >&2; exit 1; }
  printf 'PLAN\tstage=%s\tworkload=%s\tmode=%s\tcpu=%s\trun_dir=%s\n' \
    "$stage" "$workload" "$mode" "$cpu" "$run_dir"
  if [ "$dry_run" -eq 0 ]; then
    setsid "$runner" --simulator "$simulator" --config "$config" --trace "$trace" \
      --run-dir "$run_dir" --cpu "$cpu" >"$runs_root/${run_name}.launcher.log" 2>&1 &
    supervisor=$!
    printf '%s\t%s\t%s\t%s\t%s\n' "$run_name" "$supervisor" "$cpu" "$mode" "$workload" \
      >"$runs_root/${run_name}.supervisor.tsv"
  fi
done
