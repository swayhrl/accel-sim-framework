#!/usr/bin/env bash
# Future-only formal replacement dispatcher for the invalid 2DConvolution Base
# attempt.  It is intentionally separate from the frozen diagnostic and old
# Core-95 dispatchers.
set -euo pipefail

case "${1:-}" in
  --dry-run) dispatch=0 ;;
  --dispatch) dispatch=1 ;;
  *) echo "usage: $0 --dry-run|--dispatch --cpu N" >&2; exit 2 ;;
esac
shift
test "${1:-}" = --cpu || { echo 'CPU_REQUIRED' >&2; exit 2; }
cpu=${2:-}
shift 2
test "$#" -eq 0
[[ "$cpu" =~ ^[0-9]+$ ]] || exit 2

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
core=/workspace/worktrees/gpgpu-sim-decoupled-l1-m5
core_sha=41d740e862a6ad89ab0fc32b7b927ec787752862
runtime=/tmp/dtc-fast64-invalidate-formal-41d740e8/accel-sim.out
runtime_sha=6e72d36665cde18e2845914ee9c2a9f2e65b37b7b3c216edf4b676ad17e2c21c
runner_sha=bf9a84c8aab54ccd5d00a8465d69669cfac78012b783c3cfd9e0e4433062e6af
runner=/tmp/fast64-runners/$runner_sha/run_fast64_trace_v2.sh
config="$repo/configs/dtc_l1/fast64/FAST64_BASE.config"
config_sha=1a016e3cac65376330a92dd3fcf037d5fdcab5e7d295920be568e04600dd1cde
trace=/workspace/worktrees/accel-sim-decoupled-l2/hw_run/c2p-polybench-full-20260821/polybench/11.0/polybench-2DConvolution/NO_ARGS/traces/kernelslist.g
trace_sha=23bcc08b04d82fc527ffc1365d3199f4d1f3057bf6a2705d1110c5c226227d64
trace_config="$repo/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
run=/workspace/fast64-stage3-repair/fast64_3_2DConvolution_base_core41d740e8_a1_v1
framework=037f008b330eb230353b60edf126d6be9f45afdc
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
classification=PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE

test "$(git -C "$core" rev-parse HEAD)" = "$core_sha"
test -z "$(git -C "$core" status --porcelain)"
git -C "$repo" cat-file -e "$framework^{commit}"
test -x "$runtime" && test "$(sha256sum "$runtime" | awk '{print $1}')" = "$runtime_sha"
test -x "$runner" && test "$(sha256sum "$runner" | awk '{print $1}')" = "$runner_sha"
test $((8#$(stat -c %a "$runner") & 0222)) -eq 0
test "$(sha256sum "$config" | awk '{print $1}')" = "$config_sha"
test "$(sha256sum "$trace" | awk '{print $1}')" = "$trace_sha"
test -r "$trace_config"
for path in "$run" "$run.launcher.log" "$run.supervisor.tsv"; do
  test ! -e "$path" || { echo "TARGET_EXISTS_REFUSE_RERUN $path" >&2; exit 1; }
done

if test "$dispatch" = 0; then
  printf 'FAST64_3_2D_REPAIR_DRY_RUN_PASS\tcore=%s\truntime=%s\tcpu=%s\n' \
    "$core_sha" "$runtime_sha" "$cpu"
  exit 0
fi

mkdir -p /workspace/fast64-stage3-repair
exec 9>/workspace/fast64-stage3-repair/.fast64_3_2d_repair_dispatch.lock
flock -n 9 || { echo 'DISPATCH_LOCK_HELD' >&2; exit 1; }
for path in "$run" "$run.launcher.log" "$run.supervisor.tsv"; do
  test ! -e "$path" || { echo "TARGET_RACED_REFUSE_RERUN $path" >&2; exit 1; }
done
uuid=$(cat /proc/sys/kernel/random/uuid)
(
  exec 9>&-
  exec setsid "$runner" --simulator "$runtime" --config "$config" --trace "$trace" \
    --trace-config "$trace_config" --run-dir "$run" --cpu "$cpu" \
    --attempt-uuid "$uuid" --runner-sha256 "$runner_sha" \
    --immutable-runner-path "$runner" \
    --framework-scientific-config-source-sha "$framework" \
    --core-source-head "$core_sha" --observer-overlay-sha "$observer" \
    --result-classification "$classification"
) >"$run.launcher.log" 2>&1 &
supervisor=$!
printf 'row\tsupervisor_pid\tcpu_slot\tattempt_uuid\trunner_sha256\tcore_sha\truntime_sha256\tclassification\n%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
  fast64_3_2DConvolution_base_core41d740e8_a1_v1 "$supervisor" "$cpu" "$uuid" \
  "$runner_sha" "$core_sha" "$runtime_sha" "$classification" >"$run.supervisor.tsv"
printf 'FAST64_3_2D_REPAIR_DISPATCHED\trow=%s\tcpu=%s\tsupervisor=%s\tattempt_uuid=%s\n' \
  fast64_3_2DConvolution_base_core41d740e8_a1_v1 "$cpu" "$supervisor" "$uuid"
