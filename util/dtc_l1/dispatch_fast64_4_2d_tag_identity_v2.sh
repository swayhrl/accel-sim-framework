#!/usr/bin/env bash
# Future-only Core-658 2DConvolution IO/OO dispatcher.  It cannot mix any
# historical/Core-41 evidence into the final 2D triplet.
set -euo pipefail

case "${1:-}" in
  --dry-run) dispatch=0 ;;
  --dispatch) dispatch=1 ;;
  *) echo "usage: $0 --dry-run|--dispatch --mode IO|OO --cpu N" >&2; exit 2 ;;
esac
shift
mode= cpu=
while [ "$#" -gt 0 ]; do
  case "$1" in
    --mode) mode=${2:-}; shift 2 ;;
    --cpu) cpu=${2:-}; shift 2 ;;
    *) echo "usage: $0 --dry-run|--dispatch --mode IO|OO --cpu N" >&2; exit 2 ;;
  esac
done
case "$mode" in IO|OO) ;; *) echo MODE_REQUIRED >&2; exit 2 ;; esac
[[ "$cpu" =~ ^[0-9]+$ ]] || { echo CPU_MUST_BE_NUMERIC >&2; exit 2; }

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
core=/workspace/worktrees/gpgpu-sim-fast64-formal-95ccdb7a
core_sha=6587238c60214d99491f4048e28ce8a3458c1509
runtime=/tmp/dtc-fast64-2d-reserved-tag-repair-v1/accel-sim.out
runtime_sha=29a3dd9f57a5accb89822ca3fcf06b11c437bfe864ee43d2ff5f26c8c056f3c1
runner_sha=bf9a84c8aab54ccd5d00a8465d69669cfac78012b783c3cfd9e0e4433062e6af
runner=/tmp/fast64-runners/$runner_sha/run_fast64_trace_v2.sh
trace=/workspace/worktrees/accel-sim-decoupled-l2/hw_run/c2p-polybench-full-20260821/polybench/11.0/polybench-2DConvolution/NO_ARGS/traces/kernelslist.g
trace_sha=23bcc08b04d82fc527ffc1365d3199f4d1f3057bf6a2705d1110c5c226227d64
trace_config="$repo/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
framework=037f008b330eb230353b60edf126d6be9f45afdc
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
classification=PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE
base="$repo/docs/dtc_l1/fast64/generated/fast64_3_tag_identity_repair_v2/fast64_3_2DConvolution_base_core6587238c_a1_v1.json"
structural="$repo/docs/dtc_l1/fast64/generated/fast64_3_tag_identity_repair_v2/FAST64_3_2DCONVOLUTION_BASE_STRUCTURAL_METRICS_V1.json"

case "$mode" in
  IO) config="$repo/configs/dtc_l1/fast64/FAST64_IO.config"; config_sha=d4a2d9d0088946b950370b922a8d8e34422bbca9bac26f109b3977fe02a7f621 ;;
  OO) config="$repo/configs/dtc_l1/fast64/FAST64_OO.config"; config_sha=546c68f96d47f4650703ccfbc925bd789f923501d5607a77e79ca4845f234caa ;;
esac
lower=${mode,,}
run_root=/workspace/fast64-primary-r4-tag-identity-v2
row="fast64_4_primary_2DConvolution_${lower}_core6587238c_a1_v1"
run="$run_root/$row"

test "$(git -C "$core" rev-parse HEAD)" = "$core_sha"
test -z "$(git -C "$core" status --porcelain)"
git -C "$repo" cat-file -e "$framework^{commit}"
test -x "$runtime" && test "$(sha256sum "$runtime" | awk '{print $1}')" = "$runtime_sha"
test -x "$runner" && test "$(sha256sum "$runner" | awk '{print $1}')" = "$runner_sha"
test $((8#$(stat -c %a "$runner") & 0222)) -eq 0
test "$(sha256sum "$config" | awk '{print $1}')" = "$config_sha"
test "$(sha256sum "$trace" | awk '{print $1}')" = "$trace_sha"
test -r "$trace_config"
test -f "$base" && test -f "$structural" || { echo BASE_STRICT_GATE_REQUIRED >&2; exit 1; }
jq -e --arg core "$core_sha" --arg runtime "$runtime_sha" --arg framework "$framework" --arg observer "$observer" '
  .provenance.workload_id == "2DConvolution" and .provenance.config_id == "FAST64_BASE_A1" and
  .provenance.core_sha == $core and .provenance.runtime_binary_sha256 == $runtime and
  .provenance.framework_sha == $framework and .provenance.observer_overlay_sha256 == $observer and
  .provenance.result_classification == "PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE"
' "$base" >/dev/null
jq -e --arg base "$base" '
  .schema == "FAST64_3_BASE_STRUCTURAL_METRICS_V1" and .source_summary == $base and
  .metrics.terminal_lower_outstanding == 0 and .metrics.terminal_pib_occupancy == 0
' "$structural" >/dev/null
for path in "$run" "$run.launcher.log" "$run.supervisor.tsv"; do
  test ! -e "$path" || { echo "TARGET_EXISTS_REFUSE_RERUN $path" >&2; exit 1; }
done

if test "$dispatch" = 0; then
  printf 'FAST64_4_2D_TAG_IDENTITY_V2_DRY_RUN_PASS\tmode=%s\tcore=%s\truntime=%s\tcpu=%s\n' "$mode" "$core_sha" "$runtime_sha" "$cpu"
  exit 0
fi
mkdir -p "$run_root"
exec 9>"$run_root/.fast64_4_2d_tag_identity_v2_dispatch.lock"
flock -n 9 || { echo DISPATCH_LOCK_HELD >&2; exit 1; }
for path in "$run" "$run.launcher.log" "$run.supervisor.tsv"; do
  test ! -e "$path" || { echo "TARGET_RACED_REFUSE_RERUN $path" >&2; exit 1; }
done
uuid=$(cat /proc/sys/kernel/random/uuid)
(
  exec 9>&-
  exec setsid "$runner" --simulator "$runtime" --config "$config" --trace "$trace" --trace-config "$trace_config" \
    --run-dir "$run" --cpu "$cpu" --attempt-uuid "$uuid" --runner-sha256 "$runner_sha" \
    --immutable-runner-path "$runner" --framework-scientific-config-source-sha "$framework" \
    --core-source-head "$core_sha" --observer-overlay-sha "$observer" --result-classification "$classification"
) >"$run.launcher.log" 2>&1 &
supervisor=$!
printf 'row\tsupervisor_pid\tcpu_slot\tattempt_uuid\trunner_sha256\timmutable_runner\tcore_sha\truntime_sha256\tclassification\n%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
  "$row" "$supervisor" "$cpu" "$uuid" "$runner_sha" "$runner" "$core_sha" "$runtime_sha" "$classification" >"$run.supervisor.tsv"
printf 'FAST64_4_2D_TAG_IDENTITY_V2_DISPATCHED\trow=%s\tmode=%s\tcpu=%s\tsupervisor=%s\tattempt_uuid=%s\n' \
  "$row" "$mode" "$cpu" "$supervisor" "$uuid"
