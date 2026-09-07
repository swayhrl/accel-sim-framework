#!/usr/bin/env bash
# Launch one reproducible FAST64 trace replay with an atomic, exactly-once
# output namespace.  This is a future-recovery runner; it never adopts,
# overwrites, or modifies an already existing namespace.
set -euo pipefail

usage() {
  echo "usage: $0 --simulator PATH --config PATH --trace PATH --run-dir PATH [--cpu CPU] [--framework-source-head SHA] [--core-source-head SHA] [--observer-overlay-sha SHA] [--result-classification LABEL]" >&2
  exit 2
}

simulator=
config=
trace=
run_dir=
cpu=
framework_source_head=
core_source_head=
observer_overlay_sha=
result_classification=
while [ "$#" -gt 0 ]; do
  case "$1" in
    --simulator) simulator=${2:-}; shift 2 ;;
    --config) config=${2:-}; shift 2 ;;
    --trace) trace=${2:-}; shift 2 ;;
    --run-dir) run_dir=${2:-}; shift 2 ;;
    --cpu) cpu=${2:-}; shift 2 ;;
    --framework-source-head) framework_source_head=${2:-}; shift 2 ;;
    --core-source-head) core_source_head=${2:-}; shift 2 ;;
    --observer-overlay-sha) observer_overlay_sha=${2:-}; shift 2 ;;
    --result-classification) result_classification=${2:-}; shift 2 ;;
    *) usage ;;
  esac
done

test -x "$simulator"
test -r "$config"
test -r "$trace"
test -n "$run_dir"

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
trace_config="$repo_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
test -r "$trace_config"

# `mkdir` is the persistent, atomic exactly-once witness.  Never use a
# check-then-create sequence here: a concurrent dispatcher must fail closed.
mkdir -- "$run_dir" || {
  echo "TARGET_NAMESPACE_EXISTS_OR_CREATE_FAILED $run_dir" >&2
  exit 1
}

manifest="$run_dir/RUN_MANIFEST.tsv"
{
  printf 'key\tvalue\n'
  printf 'runner_schema\tFAST64_TRACE_V2_ATOMIC_NAMESPACE\n'
  printf 'simulator\t%s\n' "$simulator"
  printf 'simulator_sha256\t%s\n' "$(sha256sum "$simulator" | awk '{print $1}')"
  printf 'config\t%s\n' "$config"
  printf 'config_sha256\t%s\n' "$(sha256sum "$config" | awk '{print $1}')"
  printf 'trace_list\t%s\n' "$trace"
  printf 'trace_list_sha256\t%s\n' "$(sha256sum "$trace" | awk '{print $1}')"
  printf 'trace_config\t%s\n' "$trace_config"
  printf 'trace_config_sha256\t%s\n' "$(sha256sum "$trace_config" | awk '{print $1}')"
  if [ -n "$framework_source_head" ]; then
    printf 'framework_source_head\t%s\n' "$framework_source_head"
  fi
  if [ -n "$core_source_head" ]; then
    printf 'core_source_head\t%s\n' "$core_source_head"
  fi
  if [ -n "$observer_overlay_sha" ]; then
    printf 'observer_overlay_sha256\t%s\n' "$observer_overlay_sha"
  fi
  if [ -n "$result_classification" ]; then
    printf 'result_classification\t%s\n' "$result_classification"
  fi
  printf 'launch_utc\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} >"$manifest"

run=("$simulator" -trace "$trace" -config "$config" -config "$trace_config")
cd "$run_dir"
set +e
if [ -n "$cpu" ]; then
  /usr/bin/time -v -o resource.time taskset -c "$cpu" "${run[@]}" >simulator.stdout 2>simulator.stderr
else
  /usr/bin/time -v -o resource.time "${run[@]}" >simulator.stdout 2>simulator.stderr
fi
status=$?
set -e
printf 'simulator_exit_status\t%s\n' "$status" >>"$manifest"
printf 'terminal_utc\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$manifest"
exit "$status"
