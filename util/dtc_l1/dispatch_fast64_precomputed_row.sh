#!/usr/bin/env bash
# Exactly-once, detached dispatch for an identity-recorded FAST64 precomputed row.
set -euo pipefail

usage() {
  echo "usage: $0 --name NAME --workload NAME --mode BASE|IO|OO --config PATH --cpu N --classification LABEL [--framework-source-head SHA] [--dry-run]" >&2
  exit 2
}

name= workload= mode= config= cpu= classification= framework_source_head= dry_run=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --name) name=${2:-}; shift 2 ;;
    --workload) workload=${2:-}; shift 2 ;;
    --mode) mode=${2:-}; shift 2 ;;
    --config) config=${2:-}; shift 2 ;;
    --cpu) cpu=${2:-}; shift 2 ;;
    --classification) classification=${2:-}; shift 2 ;;
    --framework-source-head) framework_source_head=${2:-}; shift 2 ;;
    --dry-run) dry_run=1; shift ;;
    *) usage ;;
  esac
done
test -n "$name" && test -n "$workload" && test -n "$config" && test -n "$cpu" && test -n "$classification" || usage
case "$mode" in BASE|IO|OO) ;; *) usage ;; esac
case "$cpu" in *[!0-9]*) usage ;; esac

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
core_root=/workspace/worktrees/gpgpu-sim-decoupled-l1-m5
runs_root=/workspace/fast64-runs
runtime=/tmp/dtc-fast64-telemetry-build-sEWez4/accel-sim.out
expected_runtime=6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041
expected_core=bbcbb5e7565417102087bc80b14c349b4e568c05
observer_sha=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
runner="$repo_root/util/dtc_l1/run_fast64_trace.sh"
run_dir="$runs_root/$name"

# Physical acquisition is allowed to overlap logical stages only under the
# researcher-approved pending classes.  Keep that policy mechanically
# fail-closed so a generic wave cannot accidentally start main IO/OO rows
# before the FAST64.2 repair qualification exists.
fast64_2_pass="$repo_root/docs/dtc_l1/fast64/handoffs/FAST64_2_REPAIR_QUALIFICATION.md"
case "$classification" in
  PRECOMPUTED_FAST64_2_DIAGNOSTIC_PENDING_FAST64_1_ACCEPTANCE)
    echo "historical high-cap FAST64.2 class is a negative control only" >&2
    exit 1
    ;;
  PRECOMPUTED_FAST64_2_COUPLED_STRESS_PENDING_FAST64_1_ACCEPTANCE)
    echo "coupled stress requires immutable v2 dispatch via prepare_fast64_2_coupled_stress.sh" >&2
    exit 1
    ;;
  PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE)
    test "$mode" = BASE || {
      echo "only Base may precompute before FAST64.2 repair PASS" >&2; exit 2;
    }
    ;;
  PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE|PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE)
    test -f "$fast64_2_pass" && grep -Fxq 'FAST64_2_REPAIR_PASS' "$fast64_2_pass" || {
      echo "FAST64.2 repair PASS evidence is required for $classification" >&2; exit 1;
    }
    ;;
  *)
    echo "unsupported or unclassified precomputed acquisition: $classification" >&2
    exit 2
    ;;
esac

test "$(git -C "$core_root" rev-parse HEAD)" = "$expected_core"
test -x "$runtime"
test "$(sha256sum "$runtime" | awk '{print $1}')" = "$expected_runtime"
test -x "$runner"
test -r "$config"
test ! -e "$run_dir" || { echo "TARGET_EXISTS $run_dir" >&2; exit 1; }
trace_root=$(awk -F '\t' -v workload="${workload,,}" '$1 == workload { print $2; exit }' \
  "$repo_root/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv")
test -n "$trace_root"
test -r "$trace_root/kernelslist.g"
framework_sha=${framework_source_head:-$(git -C "$repo_root" rev-parse HEAD)}
git -C "$repo_root" cat-file -e "$framework_sha^{commit}"

if [ "$dry_run" = 1 ]; then
  printf 'DRY_RUN_PASS\tname=%s\tframework=%s\tcore=%s\ttrace=%s\n' \
    "$name" "$framework_sha" "$expected_core" "$trace_root/kernelslist.g"
  exit 0
fi

mkdir -p "$runs_root"
# v2 is intentionally distinct from the original lock: an already-live first
# dispatch inherited that old descriptor before this fix.  The persistent
# namespace check remains the exactly-once witness across both generations.
lock_file="$runs_root/.fast64_precomputed_dispatch_v2.lock"
exec 9>"$lock_file"
flock -n 9 || { echo "DISPATCH_LOCK_HELD $lock_file" >&2; exit 1; }
test ! -e "$run_dir" || { echo "TARGET_EXISTS $run_dir" >&2; exit 1; }
# Do not let the detached runner inherit fd 9, or it would retain this launch
# lock until natural terminal state and serialize unrelated pending rows.
setsid "$runner" --simulator "$runtime" --config "$config" \
  --trace "$trace_root/kernelslist.g" --run-dir "$run_dir" --cpu "$cpu" \
  --framework-source-head "$framework_sha" --core-source-head "$expected_core" \
  --observer-overlay-sha "$observer_sha" --result-classification "$classification" \
  >"$run_dir.launcher.log" 2>&1 9>&- &
supervisor=$!
printf 'name\t%s\nsupervisor_pid\t%s\ncpu\t%s\nworkload\t%s\nmode\t%s\nclassification\t%s\nframework_source_head\t%s\ncore_source_head\t%s\n' \
  "$name" "$supervisor" "$cpu" "$workload" "$mode" "$classification" "$framework_sha" "$expected_core" \
  >"$run_dir.supervisor.tsv"
printf 'DISPATCHED\t%s\tsupervisor=%s\tcpu=%s\n' "$name" "$supervisor" "$cpu"
