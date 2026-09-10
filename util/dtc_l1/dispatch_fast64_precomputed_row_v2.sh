#!/usr/bin/env bash
# Future-only immutable-v2 exactly-once dispatch.  This replaces no live or
# frozen controller and is intended for FAST64 waves only after their owning
# logical stage permits physical acquisition.
set -euo pipefail

usage() {
  echo "usage: $0 --name NAME --workload NAME --mode BASE|IO|OO --config PATH --cpu N --classification LABEL --framework-scientific-config-source-sha SHA [--dry-run]" >&2
  exit 2
}

name= workload= mode= config= cpu= classification= framework= dry_run=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --name) name=${2:-}; shift 2 ;;
    --workload) workload=${2:-}; shift 2 ;;
    --mode) mode=${2:-}; shift 2 ;;
    --config) config=${2:-}; shift 2 ;;
    --cpu) cpu=${2:-}; shift 2 ;;
    --classification) classification=${2:-}; shift 2 ;;
    --framework-scientific-config-source-sha) framework=${2:-}; shift 2 ;;
    --dry-run) dry_run=1; shift ;;
    *) usage ;;
  esac
done
test -n "$name" && test -n "$workload" && test -n "$config" && test -n "$cpu" &&
  test -n "$classification" && test -n "$framework" || usage
[[ "$name" =~ ^[A-Za-z0-9._-]+$ ]] || usage
[[ "$cpu" =~ ^[0-9]+$ ]] || usage
case "$mode" in BASE|IO|OO) ;; *) usage ;; esac

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs=/workspace/fast64-runs
core=/workspace/worktrees/gpgpu-sim-decoupled-l1-m5
core_sha=bbcbb5e7565417102087bc80b14c349b4e568c05
runtime=/tmp/dtc-fast64-telemetry-build-sEWez4/accel-sim.out
runtime_sha=6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
runner_sha=bf9a84c8aab54ccd5d00a8465d69669cfac78012b783c3cfd9e0e4433062e6af
runner_source="$repo/util/dtc_l1/run_fast64_trace_v2.sh"
runner="/tmp/fast64-runners/$runner_sha/run_fast64_trace_v2.sh"
trace_config="$repo/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
payload="$repo/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"
run="$runs/$name"
pass_artifact="$repo/docs/dtc_l1/fast64/handoffs/FAST64_2_REPAIR_QUALIFICATION.md"

# Physical acquisition policy is checked here as well as by the wave pool so a
# direct future invocation cannot bypass the FAST64.2 logical repair gate.
case "$classification" in
  PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE)
    test "$mode" = BASE || { echo "ONLY_BASE_MAY_PRECOMPUTE_BEFORE_FAST64_2_PASS" >&2; exit 2; }
    ;;
  PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE|PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE)
    test -f "$pass_artifact" && grep -Fq 'FAST64_2_REPAIR_PASS' "$pass_artifact" || {
      echo "FAST64_2_REPAIR_PASS_REQUIRED" >&2; exit 1;
    }
    ;;
  *) echo "UNSUPPORTED_OR_UNCLASSIFIED_ACQUISITION $classification" >&2; exit 2 ;;
esac

test "$(git -C "$core" rev-parse HEAD)" = "$core_sha"
git -C "$repo" cat-file -e "$framework^{commit}"
test -x "$runtime" && test "$(sha256sum "$runtime" | awk '{print $1}')" = "$runtime_sha"
test -x "$runner_source" && test "$(sha256sum "$runner_source" | awk '{print $1}')" = "$runner_sha"
test -x "$runner" && test "$(sha256sum "$runner" | awk '{print $1}')" = "$runner_sha"
test $((8#$(stat -c %a "$runner") & 0222)) -eq 0
test -r "$config" && test -r "$trace_config" && test -r "$payload"
test "$(sha256sum "$config" | awk '{print $1}')" = \
  "$(git -C "$repo" show "$framework:${config#$repo/}" | sha256sum | awk '{print $1}')"
test "$(sha256sum "$trace_config" | awk '{print $1}')" = \
  "$(git -C "$repo" show "$framework:gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config" | sha256sum | awk '{print $1}')"
trace=$(awk -F '\t' -v w="$workload" 'tolower($1) == tolower(w) {print $2; exit}' "$payload")
test -n "$trace" && test -r "$trace/kernelslist.g"
for p in "$run" "$run.launcher.log" "$run.supervisor.tsv"; do
  test ! -e "$p" || { echo "TARGET_EXISTS_REFUSE_RERUN $p" >&2; exit 1; }
done

if [ "$dry_run" = 1 ]; then
  printf 'FAST64_V2_DISPATCH_DRY_RUN_PASS\tname=%s\tworkload=%s\tmode=%s\tcpu=%s\tclassification=%s\n' \
    "$name" "$workload" "$mode" "$cpu" "$classification"
  exit 0
fi

mkdir -p "$runs"
exec 9>"$runs/.fast64_precomputed_immutable_v2_dispatch.lock"
flock -n 9 || { echo "FAST64_V2_DISPATCH_LOCK_HELD" >&2; exit 1; }
for p in "$run" "$run.launcher.log" "$run.supervisor.tsv"; do
  test ! -e "$p" || { echo "TARGET_RACED_REFUSE_RERUN $p" >&2; exit 1; }
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
printf 'FAST64_V2_DISPATCHED\trow=%s\tcpu=%s\tsupervisor=%s\tattempt_uuid=%s\n' \
  "$name" "$cpu" "$supervisor" "$uuid"
