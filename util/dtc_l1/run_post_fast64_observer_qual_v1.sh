#!/usr/bin/env bash
# Future-only immutable runner for post-FAST64 observer qualification.
set -euo pipefail

usage() {
  echo "usage: $0 --simulator PATH --core-sha SHA --config PATH --trace PATH --trace-config PATH --run-dir PATH --workload NAME --mode IO|OO --observer 0|1 [--cpu N]" >&2
  exit 2
}

original_args=("$@")
simulator= core_sha= config= trace= trace_config= run_dir= workload= mode=
observer= cpu= immutable_runner_sha=
while [ "$#" -gt 0 ]; do
  case "$1" in
    --simulator) simulator=${2:-}; shift 2 ;;
    --core-sha) core_sha=${2:-}; shift 2 ;;
    --config) config=${2:-}; shift 2 ;;
    --trace) trace=${2:-}; shift 2 ;;
    --trace-config) trace_config=${2:-}; shift 2 ;;
    --run-dir) run_dir=${2:-}; shift 2 ;;
    --workload) workload=${2:-}; shift 2 ;;
    --mode) mode=${2:-}; shift 2 ;;
    --observer) observer=${2:-}; shift 2 ;;
    --cpu) cpu=${2:-}; shift 2 ;;
    --immutable-runner-sha) immutable_runner_sha=${2:-}; shift 2 ;;
    *) usage ;;
  esac
done
test -x "$simulator" && test -n "$core_sha" && test -r "$config" && \
  test -r "$trace" && test -r "$trace_config" && test -n "$run_dir" && \
  test -n "$workload" && test -n "$mode" && test -n "$observer" || usage
case "$mode" in IO|OO) ;; *) usage ;; esac
case "$observer" in 0|1) ;; *) usage ;; esac
test -z "$cpu" || [[ "$cpu" =~ ^[0-9]+$ ]] || usage

self=$(readlink -f -- "$0")
actual_runner_sha=$(sha256sum "$self" | awk '{print $1}')
if [ -z "$immutable_runner_sha" ]; then
  immutable_dir="/tmp/dtc-post-fast64-observer-runners/$actual_runner_sha"
  immutable_runner="$immutable_dir/run_post_fast64_observer_qual_v1.sh"
  mkdir -p "$immutable_dir"
  if [ ! -e "$immutable_runner" ]; then
    install -m 555 "$self" "$immutable_runner"
  fi
  test "$(sha256sum "$immutable_runner" | awk '{print $1}')" = "$actual_runner_sha"
  exec "$immutable_runner" "${original_args[@]}" \
    --immutable-runner-sha "$actual_runner_sha"
fi
test "$immutable_runner_sha" = "$actual_runner_sha"
test $((8#$(stat -c %a "$self") & 0222)) -eq 0

for path in "$run_dir" "$run_dir/RUN_MANIFEST.tsv" "$run_dir/RUN_START.tsv" \
            "$run_dir/RUN_TERMINAL.tsv"; do
  test ! -e "$path" || { echo "TARGET_EXISTS_REFUSE_RERUN $path" >&2; exit 1; }
done
umask 077
mkdir -- "$run_dir"

sha() { sha256sum "$1" | awk '{print $1}'; }
attempt_uuid=$(cat /proc/sys/kernel/random/uuid)
launch_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
manifest="$run_dir/RUN_MANIFEST.tsv"
{
  printf 'key\tvalue\n'
  printf 'runner_schema\tPOST_FAST64_OBSERVER_QUAL_V1\n'
  printf 'result_classification\tPOST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT\n'
  printf 'attempt_uuid\t%s\n' "$attempt_uuid"
  printf 'runner_sha256\t%s\n' "$actual_runner_sha"
  printf 'immutable_runner_path\t%s\n' "$self"
  printf 'simulator\t%s\n' "$simulator"
  printf 'simulator_sha256\t%s\n' "$(sha "$simulator")"
  printf 'core_source_head\t%s\n' "$core_sha"
  printf 'workload\t%s\n' "$workload"
  printf 'mode\t%s\n' "$mode"
  printf 'observer_enabled\t%s\n' "$observer"
  printf 'config\t%s\n' "$config"
  printf 'config_sha256\t%s\n' "$(sha "$config")"
  printf 'trace_list\t%s\n' "$trace"
  printf 'trace_list_sha256\t%s\n' "$(sha "$trace")"
  printf 'trace_config\t%s\n' "$trace_config"
  printf 'trace_config_sha256\t%s\n' "$(sha "$trace_config")"
  printf 'launch_utc\t%s\n' "$launch_utc"
} >"$manifest"
printf 'key\tvalue\nreceipt_type\tSTART\nattempt_uuid\t%s\nlaunch_utc\t%s\n' \
  "$attempt_uuid" "$launch_utc" >"$run_dir/RUN_START.tsv"
chmod 444 "$run_dir/RUN_START.tsv"

run=("$simulator" -trace "$trace" -config "$config" -config "$trace_config")
if [ "$observer" = 1 ]; then
  run+=(-gpgpu_dtc_l1_post_fast64_telemetry 1)
fi
cd "$run_dir"
set +e
if [ -n "$cpu" ]; then
  /usr/bin/time -v -o resource.time taskset -c "$cpu" "${run[@]}" \
    >simulator.stdout 2>simulator.stderr
else
  /usr/bin/time -v -o resource.time "${run[@]}" \
    >simulator.stdout 2>simulator.stderr
fi
status=$?
set -e
terminal_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
printf 'key\tvalue\nreceipt_type\tTERMINAL\nattempt_uuid\t%s\nsimulator_exit_status\t%s\nterminal_utc\t%s\n' \
  "$attempt_uuid" "$status" "$terminal_utc" >"$run_dir/RUN_TERMINAL.tsv"
chmod 444 "$run_dir/RUN_TERMINAL.tsv"
printf 'simulator_exit_status\t%s\nterminal_utc\t%s\n' "$status" "$terminal_utc" >>"$manifest"
printf 'POST_FAST64_OBSERVER_QUAL_TERMINAL\tworkload=%s\tmode=%s\tobserver=%s\tstatus=%s\trun=%s\n' \
  "$workload" "$mode" "$observer" "$status" "$run_dir"
exit "$status"
