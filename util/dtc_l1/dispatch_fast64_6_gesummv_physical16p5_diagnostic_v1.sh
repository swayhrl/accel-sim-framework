#!/usr/bin/env bash
# Future-only, nonformal GESUMMV 16.5-KiB physical-pool diagnostic.  It uses
# the observational Core only after a resource-safe CPU is explicitly supplied.
set -euo pipefail

case "${1:-}" in
  --dry-run) dispatch=0 ;;
  --dispatch) dispatch=1 ;;
  *) echo "usage: $0 --dry-run|--dispatch --mode IO|OO [--cpu N]" >&2; exit 2 ;;
esac
shift
mode= cpu=
while [ "$#" -gt 0 ]; do
  case "$1" in
    --mode) mode=${2:-}; shift 2 ;;
    --cpu) cpu=${2:-}; shift 2 ;;
    *) echo "usage: $0 --dry-run|--dispatch --mode IO|OO [--cpu N]" >&2; exit 2 ;;
  esac
done
case "$mode" in IO|OO) ;; *) echo 'FAST64_6_GESUMMV_DIAG_MODE_REQUIRED' >&2; exit 2 ;; esac
[[ -z "$cpu" || "$cpu" =~ ^[0-9]+$ ]] || exit 2

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
core=/workspace/worktrees/gpgpu-sim-decoupled-l1-m5
core_sha=f2836ea1258ce64d2ca48e1b7a8ec8522060203f
sim=/tmp/dtc-fast64-2d-fill-owner-YXYc7J/accel-sim.out
sim_sha=361aada1e0fc166cb161670e0c9386dc63baad9c8f75587d34cfb69d51da48e7
runner_sha=bf9a84c8aab54ccd5d00a8465d69669cfac78012b783c3cfd9e0e4433062e6af
runner=/tmp/fast64-runners/$runner_sha/run_fast64_trace_v2.sh
trace=/workspace/worktrees/accel-sim-decoupled-l2/hw_run/c2p-polybench-full-20260821/polybench/11.0/polybench-gesummv/NO_ARGS/traces/kernelslist.g
trace_config="$repo/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
case "$mode" in
  IO)
    config="$repo/configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_16.5/FAST64_SENS_PHYSICAL_16p5KB_IO.config"
    config_sha=475b8eab9b555c06ca3adeb2b011079eee01de0bf7b8bcca36e7c3adce7d9a77
    ;;
  OO)
    config="$repo/configs/dtc_l1/fast64/sensitivity_frozen_v2/physical_16.5/FAST64_SENS_PHYSICAL_16p5KB_OO.config"
    config_sha=f9855bce0b1480a529f894de15a2fd769233f83d837ee07e745f88c901782d31
    ;;
esac
run=/workspace/fast64-diagnostics/fast64_6_gesummv_physical16p5_${mode,,}_coref283_diag_v1

test "$(git -C "$core" rev-parse HEAD)" = "$core_sha"
test -z "$(git -C "$core" status --porcelain)"
test -x "$sim" && test "$(sha256sum "$sim" | awk '{print $1}')" = "$sim_sha"
test -x "$runner" && test "$(sha256sum "$runner" | awk '{print $1}')" = "$runner_sha"
test $((8#$(stat -c %a "$runner") & 0222)) -eq 0
test "$(sha256sum "$config" | awk '{print $1}')" = "$config_sha"
test -r "$trace" && test -r "$trace_config"
test ! -e "$run" || { echo "DIAGNOSTIC_NAMESPACE_EXISTS_REFUSE_RERUN $run" >&2; exit 1; }

if test "$dispatch" = 0; then
  printf 'FAST64_6_GESUMMV_DIAG_DRY_RUN_PASS\tmode=%s\tcore=%s\tbinary=%s\tconfig=%s\n' "$mode" "$core_sha" "$sim_sha" "$config_sha"
  exit 0
fi
test -n "$cpu" || { echo 'FAST64_6_GESUMMV_DIAG_CPU_REQUIRED' >&2; exit 2; }
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
