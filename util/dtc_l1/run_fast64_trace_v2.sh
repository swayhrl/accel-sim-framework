#!/usr/bin/env bash
# Launch one future FAST64 recovery attempt. The caller must execute an
# immutable, SHA-bound copy of this file; this script never reopens a namespace.
set -euo pipefail

usage() {
  echo "usage: $0 --simulator PATH --config PATH --trace PATH --trace-config PATH --run-dir PATH --attempt-uuid UUID --runner-sha256 SHA --immutable-runner-path PATH --framework-scientific-config-source-sha SHA --core-source-head SHA --observer-overlay-sha SHA [--cpu CPU] [--result-classification LABEL]" >&2
  exit 2
}

simulator= config= trace= trace_config= run_dir= cpu= attempt_uuid=
runner_sha256= immutable_runner_path= framework_scientific_config_source_sha=
core_source_head= observer_overlay_sha= result_classification=
while [ "$#" -gt 0 ]; do
  case "$1" in
    --simulator) simulator=${2:-}; shift 2 ;;
    --config) config=${2:-}; shift 2 ;;
    --trace) trace=${2:-}; shift 2 ;;
    --trace-config) trace_config=${2:-}; shift 2 ;;
    --run-dir) run_dir=${2:-}; shift 2 ;;
    --cpu) cpu=${2:-}; shift 2 ;;
    --attempt-uuid) attempt_uuid=${2:-}; shift 2 ;;
    --runner-sha256) runner_sha256=${2:-}; shift 2 ;;
    --immutable-runner-path) immutable_runner_path=${2:-}; shift 2 ;;
    --framework-scientific-config-source-sha) framework_scientific_config_source_sha=${2:-}; shift 2 ;;
    --core-source-head) core_source_head=${2:-}; shift 2 ;;
    --observer-overlay-sha) observer_overlay_sha=${2:-}; shift 2 ;;
    --result-classification) result_classification=${2:-}; shift 2 ;;
    *) usage ;;
  esac
done

test -x "$simulator" && test -r "$config" && test -r "$trace" && test -r "$trace_config"
test -n "$run_dir" && test -n "$attempt_uuid" && test -n "$runner_sha256"
test -n "$immutable_runner_path" && test -n "$framework_scientific_config_source_sha"
test -n "$core_source_head" && test -n "$observer_overlay_sha"

# A long-lived Bash process must not resume from mutable worktree bytes.
self_path=$(readlink -f -- "$0")
immutable_path=$(readlink -f -- "$immutable_runner_path")
test "$self_path" = "$immutable_path" || {
  echo "RUNNER_NOT_EXECUTED_FROM_IMMUTABLE_PATH self=$self_path immutable=$immutable_path" >&2
  exit 1
}
actual_runner_sha=$(sha256sum "$immutable_path" | awk '{print $1}')
test "$actual_runner_sha" = "$runner_sha256" || {
  echo "RUNNER_SHA256_MISMATCH expected=$runner_sha256 actual=$actual_runner_sha" >&2
  exit 1
}
runner_mode=$(stat -c %a "$immutable_path")
test $((8#$runner_mode & 0222)) -eq 0 || {
  echo "RUNNER_IS_WRITABLE mode=$runner_mode path=$immutable_path" >&2
  exit 1
}

# mkdir is the durable exactly-once witness. Duplicate dispatch must fail
# before any manifest, receipt, or simulator output can be opened.
umask 077
mkdir -- "$run_dir" || {
  echo "TARGET_NAMESPACE_EXISTS_OR_CREATE_FAILED $run_dir" >&2
  exit 1
}

launch_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
manifest="$run_dir/RUN_MANIFEST.tsv"
start_receipt="$run_dir/RUN_START.tsv"
terminal_receipt="$run_dir/RUN_TERMINAL.tsv"
{
  printf 'key\tvalue\n'
  printf 'runner_schema\tFAST64_TRACE_V2_IMMUTABLE_ATTEMPT\n'
  printf 'runner_sha256\t%s\n' "$runner_sha256"
  printf 'immutable_runner_path\t%s\n' "$immutable_path"
  printf 'attempt_uuid\t%s\n' "$attempt_uuid"
  printf 'simulator\t%s\n' "$simulator"
  printf 'simulator_sha256\t%s\n' "$(sha256sum "$simulator" | awk '{print $1}')"
  printf 'config\t%s\n' "$config"
  printf 'config_sha256\t%s\n' "$(sha256sum "$config" | awk '{print $1}')"
  printf 'trace_list\t%s\n' "$trace"
  printf 'trace_list_sha256\t%s\n' "$(sha256sum "$trace" | awk '{print $1}')"
  printf 'trace_config\t%s\n' "$trace_config"
  printf 'trace_config_sha256\t%s\n' "$(sha256sum "$trace_config" | awk '{print $1}')"
  printf 'framework_scientific_config_source_sha\t%s\n' "$framework_scientific_config_source_sha"
  printf 'core_source_head\t%s\n' "$core_source_head"
  printf 'observer_overlay_sha256\t%s\n' "$observer_overlay_sha"
  if [ -n "$result_classification" ]; then
    printf 'result_classification\t%s\n' "$result_classification"
  fi
  printf 'launch_utc\t%s\n' "$launch_utc"
} >"$manifest"
{
  printf 'key\tvalue\n'
  printf 'receipt_schema\tFAST64_ATTEMPT_RECEIPT_V1\n'
  printf 'receipt_type\tSTART\n'
  printf 'attempt_uuid\t%s\n' "$attempt_uuid"
  printf 'runner_sha256\t%s\n' "$runner_sha256"
  printf 'immutable_runner_path\t%s\n' "$immutable_path"
  printf 'launch_utc\t%s\n' "$launch_utc"
} >"$start_receipt"
chmod 444 "$start_receipt"

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
terminal_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
{
  printf 'key\tvalue\n'
  printf 'receipt_schema\tFAST64_ATTEMPT_RECEIPT_V1\n'
  printf 'receipt_type\tTERMINAL\n'
  printf 'attempt_uuid\t%s\n' "$attempt_uuid"
  printf 'runner_sha256\t%s\n' "$runner_sha256"
  printf 'immutable_runner_path\t%s\n' "$immutable_path"
  printf 'simulator_exit_status\t%s\n' "$status"
  printf 'terminal_utc\t%s\n' "$terminal_utc"
} >"$terminal_receipt"
chmod 444 "$terminal_receipt"
printf 'simulator_exit_status\t%s\n' "$status" >>"$manifest"
printf 'terminal_utc\t%s\n' "$terminal_utc" >>"$manifest"
exit "$status"
