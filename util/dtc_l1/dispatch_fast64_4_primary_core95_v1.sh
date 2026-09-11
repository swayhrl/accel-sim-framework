#!/usr/bin/env bash
# Future-only immutable dispatch for the Core95 FAST64.4 primary IO/OO wave.
# It deliberately does not alter the retained bbcbb dispatcher or any live
# controller.  Every invocation owns a fresh namespace under fast64-primary-r4.
set -euo pipefail

usage() {
  echo "usage: $0 --name NAME --workload NAME --mode IO|OO --config PATH --cpu N --framework-scientific-config-source-sha SHA [--dry-run]" >&2
  exit 2
}

name= workload= mode= config= cpu= framework= dry_run=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --name) name=${2:-}; shift 2 ;;
    --workload) workload=${2:-}; shift 2 ;;
    --mode) mode=${2:-}; shift 2 ;;
    --config) config=${2:-}; shift 2 ;;
    --cpu) cpu=${2:-}; shift 2 ;;
    --framework-scientific-config-source-sha) framework=${2:-}; shift 2 ;;
    --dry-run) dry_run=1; shift ;;
    *) usage ;;
  esac
done
test -n "$name" && test -n "$workload" && test -n "$config" && test -n "$cpu" && test -n "$framework" || usage
[[ "$name" =~ ^[A-Za-z0-9._-]+$ ]] || usage
[[ "$cpu" =~ ^[0-9]+$ ]] || usage
case "$mode" in IO|OO) ;; *) usage ;; esac

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
core=/workspace/worktrees/gpgpu-sim-decoupled-l1-m5
runs=/workspace/fast64-primary-r4
core_sha=95ccdb7a056f2d53f740d90869785cac6d4ee0f5
runtime=/tmp/dtc-fast64-zero-access-formal-95ccdb7a/accel-sim.out
runtime_sha=462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
runner_sha=bf9a84c8aab54ccd5d00a8465d69669cfac78012b783c3cfd9e0e4433062e6af
runner_source="$repo/util/dtc_l1/run_fast64_trace_v2.sh"
runner="/tmp/fast64-runners/$runner_sha/run_fast64_trace_v2.sh"
trace_config="$repo/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
payload="$repo/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
classification=PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE
run="$runs/$name"

test -f "$repo/docs/dtc_l1/fast64/handoffs/FAST64_2_REPAIR_QUALIFICATION.md" || {
  echo FAST64_2_REPAIR_PASS_REQUIRED >&2; exit 1;
}
grep -Fq FAST64_2_REPAIR_PASS "$repo/docs/dtc_l1/fast64/handoffs/FAST64_2_REPAIR_QUALIFICATION.md" || {
  echo FAST64_2_REPAIR_PASS_REQUIRED >&2; exit 1;
}
git -C "$core" cat-file -e "$core_sha^{commit}"
git -C "$repo" cat-file -e "$framework^{commit}"
test -x "$runtime" && test "$(sha256sum "$runtime" | awk '{print $1}')" = "$runtime_sha"
test -x "$runner_source" && test "$(sha256sum "$runner_source" | awk '{print $1}')" = "$runner_sha"
test -x "$runner" && test "$(sha256sum "$runner" | awk '{print $1}')" = "$runner_sha"
test $((8#$(stat -c %a "$runner") & 0222)) -eq 0
test -r "$config" && test -r "$trace_config" && test -r "$payload"
test "$(sha256sum "$config" | awk '{print $1}')" = "$(git -C "$repo" show "$framework:${config#$repo/}" | sha256sum | awk '{print $1}')"
test "$(sha256sum "$trace_config" | awk '{print $1}')" = "$(git -C "$repo" show "$framework:gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config" | sha256sum | awk '{print $1}')"
trace=$(awk -F '\t' -v w="$workload" 'tolower($1) == tolower(w) {print $2; exit}' "$payload")
test -n "$trace" && test -r "$trace/kernelslist.g"
for path in "$run" "$run.launcher.log" "$run.supervisor.tsv"; do
  test ! -e "$path" || { echo "TARGET_EXISTS_REFUSE_RERUN $path" >&2; exit 1; }
done

if [ "$dry_run" = 1 ]; then
  printf 'FAST64_4_PRIMARY_CORE95_V1_DRY_RUN_PASS\tname=%s\tworkload=%s\tmode=%s\tcpu=%s\n' "$name" "$workload" "$mode" "$cpu"
  exit 0
fi

mkdir -p "$runs"
exec 9>"$runs/.fast64_4_primary_core95_v1_dispatch.lock"
flock -n 9 || { echo FAST64_4_PRIMARY_CORE95_V1_DISPATCH_LOCK_HELD >&2; exit 1; }
for path in "$run" "$run.launcher.log" "$run.supervisor.tsv"; do
  test ! -e "$path" || { echo "TARGET_RACED_REFUSE_RERUN $path" >&2; exit 1; }
done
uuid=$(cat /proc/sys/kernel/random/uuid)
(
  exec 9>&-
  exec setsid "$runner" --simulator "$runtime" --config "$config" --trace "$trace/kernelslist.g" \
    --trace-config "$trace_config" --run-dir "$run" --cpu "$cpu" --attempt-uuid "$uuid" \
    --runner-sha256 "$runner_sha" --immutable-runner-path "$runner" \
    --framework-scientific-config-source-sha "$framework" --core-source-head "$core_sha" \
    --observer-overlay-sha "$observer" --result-classification "$classification"
) >"$run.launcher.log" 2>&1 &
supervisor=$!
printf 'row\tsupervisor_pid\tcpu_slot\tattempt_uuid\trunner_sha256\timmutable_runner\tcore_sha\truntime_sha256\tclassification\n%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
  "$name" "$supervisor" "$cpu" "$uuid" "$runner_sha" "$runner" "$core_sha" "$runtime_sha" "$classification" >"$run.supervisor.tsv"
printf 'FAST64_4_PRIMARY_CORE95_V1_DISPATCHED\trow=%s\tcpu=%s\tsupervisor=%s\tattempt_uuid=%s\n' "$name" "$cpu" "$supervisor" "$uuid"
