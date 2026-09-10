#!/usr/bin/env bash
# Future-only, nonformal reproducer for the preserved 2DConvolution/Base
# failure.  It is intentionally not a formal result dispatcher.
set -euo pipefail

case "${1:-}" in
  --dry-run) dispatch=0 ;;
  --dispatch) dispatch=1 ;;
  *) echo "usage: $0 --dry-run|--dispatch [--cpu N]" >&2; exit 2 ;;
esac
shift
cpu=
if test "${1:-}" = --cpu; then cpu=${2:-}; shift 2; fi
test "$#" -eq 0
[[ -z "$cpu" || "$cpu" =~ ^[0-9]+$ ]] || exit 2

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
core=/workspace/worktrees/gpgpu-sim-decoupled-l1-m5
core_sha=f2836ea1258ce64d2ca48e1b7a8ec8522060203f
sim=/tmp/dtc-fast64-2d-fill-owner-YXYc7J/accel-sim.out
sim_sha=361aada1e0fc166cb161670e0c9386dc63baad9c8f75587d34cfb69d51da48e7
runner_sha=bf9a84c8aab54ccd5d00a8465d69669cfac78012b783c3cfd9e0e4433062e6af
runner=/tmp/fast64-runners/$runner_sha/run_fast64_trace_v2.sh
config="$repo/configs/dtc_l1/fast64/FAST64_BASE.config"
config_sha=1a016e3cac65376330a92dd3fcf037d5fdcab5e7d295920be568e04600dd1cde
trace=/workspace/worktrees/accel-sim-decoupled-l2/hw_run/c2p-polybench-full-20260821/polybench/11.0/polybench-2DConvolution/NO_ARGS/traces/kernelslist.g
trace_sha=23bcc08b04d82fc527ffc1365d3199f4d1f3057bf6a2705d1110c5c226227d64
trace_config="$repo/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
run=/workspace/fast64-diagnostics/fast64_3_2DConvolution_base_coref283_diag_v1

test "$(git -C "$core" rev-parse HEAD)" = "$core_sha"
test -z "$(git -C "$core" status --porcelain)"
test -x "$sim" && test "$(sha256sum "$sim" | awk '{print $1}')" = "$sim_sha"
test -x "$runner" && test "$(sha256sum "$runner" | awk '{print $1}')" = "$runner_sha"
test $((8#$(stat -c %a "$runner") & 0222)) -eq 0
test "$(sha256sum "$config" | awk '{print $1}')" = "$config_sha"
test "$(sha256sum "$trace" | awk '{print $1}')" = "$trace_sha"
test -r "$trace_config"
test ! -e "$run" || { echo "DIAGNOSTIC_NAMESPACE_EXISTS_REFUSE_RERUN $run" >&2; exit 1; }

if test "$dispatch" = 0; then
  printf 'FAST64_3_2D_DIAG_DRY_RUN_PASS\tcore=%s\tbinary=%s\n' "$core_sha" "$sim_sha"
  exit 0
fi
test -n "$cpu" || { echo 'FAST64_3_2D_DIAG_CPU_REQUIRED' >&2; exit 2; }
uuid=$(cat /proc/sys/kernel/random/uuid)
mkdir -p /workspace/fast64-diagnostics
exec setsid "$runner" --simulator "$sim" --config "$config" --trace "$trace" \
  --trace-config "$trace_config" --run-dir "$run" --cpu "$cpu" \
  --attempt-uuid "$uuid" --runner-sha256 "$runner_sha" \
  --immutable-runner-path "$runner" \
  --framework-scientific-config-source-sha 037f008b330eb230353b60edf126d6be9f45afdc \
  --core-source-head "$core_sha" \
  --observer-overlay-sha 2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e \
  --result-classification NONFORMAL_DIAGNOSTIC_NOT_RESULT
