#!/usr/bin/env bash
# Non-scientific isolated regression for R2 host-slot discovery.  It supplies
# a synthetic process table only to the dispatcher's dry-run path.
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
dispatcher="$repo_root/util/dtc_l1/prepare_fast64_1_r2_full_wave.sh"
work_root=$(mktemp -d /tmp/fast64-r2-slot-regression.XXXXXX)
proc_root="$work_root/proc"

mkdir -p -- "$proc_root/101" "$proc_root/202"
printf 'accel-sim.out\0-trace\0synthetic\0' >"$proc_root/101/cmdline"
printf 'Name:\taccel-sim.out\nCpus_allowed_list:\t75,77-78\n' >"$proc_root/101/status"
printf 'accel-sim.out\0-trace\0broad-synthetic\0' >"$proc_root/202/cmdline"
printf 'Name:\taccel-sim.out\nCpus_allowed_list:\t0-511\n' >"$proc_root/202/status"

output=$(FAST64_PROC_ROOT="$proc_root" FAST64_CPU_CANDIDATES='74-80' "$dispatcher" --dry-run)
printf '%s\n' "$output"
printf '%s\n' "$output" | rg -q 'R2_TOPOLOGY_AWARE_DISPATCH_DRY_RUN_PASS'
printf '%s\n' "$output" | rg -q 'available_distinct_physical_cores=4'
printf '%s\n' "$output" | rg -q 'candidate_cpus=74,76,79,80'

# Regression for the dispatcher's advisory-lock lifetime: a detached child
# must not inherit the lock descriptor.  This is a disposable shell/sleep
# topology only; it neither starts a simulator nor touches a real namespace.
lock_file="$work_root/dispatch.lock"
child_pid_file="$work_root/child.pid"
bash -c '
  exec 9>"$1"
  flock -n 9
  ( exec 9>&-; exec sleep 2 ) &
  printf "%s\\n" "$!" >"$2"
' bash "$lock_file" "$child_pid_file"
child_pid=$(cat "$child_pid_file")
kill -0 "$child_pid"
flock -n "$lock_file" -c true
wait_for_child=0
while kill -0 "$child_pid" 2>/dev/null; do
  sleep 0.1
  wait_for_child=$((wait_for_child + 1))
  test "$wait_for_child" -lt 40 || { echo "R2_LOCK_FD_REGRESSION_CHILD_STUCK" >&2; exit 1; }
done
printf 'FAST64_R2_DISPATCH_LOCK_FD_CLOSURE_REGRESSION_PASS\tchild_pid=%s\n' "$child_pid"
printf 'FAST64_R2_TOPOLOGY_SELECTOR_REGRESSION_PASS\twork_root=%s\n' "$work_root"
