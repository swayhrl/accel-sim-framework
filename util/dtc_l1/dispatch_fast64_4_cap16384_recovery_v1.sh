#!/usr/bin/env bash
# Future-only immutable-v2 dispatch for the first monotonic FAST64.4 cap sweep.
# It never selects a cap or promotes a result; it only acquires the exact rows
# that were cap-bound at 8192 or are needed to keep their final triplets whole.
set -euo pipefail

case "${1:-}" in
  --dry-run) dispatch=0 ;;
  --dispatch) dispatch=1 ;;
  *) echo "usage: $0 --dry-run|--dispatch --cpu-list C1,...,C9" >&2; exit 2 ;;
esac
shift
test "${1:-}" = --cpu-list && cpus=${2:-} && test "$#" = 2 || {
  echo "usage: $0 --dry-run|--dispatch --cpu-list C1,...,C9" >&2; exit 2;
}
IFS=, read -r -a cpu <<<"$cpus"
test "${#cpu[@]}" = 9 || { echo CAP16384_CPU_COUNT_MUST_BE_9 >&2; exit 2; }
for item in "${cpu[@]}"; do [[ "$item" =~ ^[0-9]+$ ]] || { echo CAP16384_CPU_NOT_NUMERIC >&2; exit 2; }; done
test "$(printf '%s\n' "${cpu[@]}" | sort -u | wc -l)" = 9 || { echo CAP16384_CPU_DUPLICATE >&2; exit 2; }

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
core_repo=/workspace/worktrees/gpgpu-sim-fast64-formal-95ccdb7a
core95=95ccdb7a056f2d53f740d90869785cac6d4ee0f5
runtime95=/tmp/dtc-fast64-zero-access-formal-95ccdb7a/accel-sim.out
runtime95_sha=462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9
core658=6587238c60214d99491f4048e28ce8a3458c1509
runtime658=/tmp/dtc-fast64-2d-reserved-tag-repair-v1/accel-sim.out
runtime658_sha=29a3dd9f57a5accb89822ca3fcf06b11c437bfe864ee43d2ff5f26c8c056f3c1
runner_sha=bf9a84c8aab54ccd5d00a8465d69669cfac78012b783c3cfd9e0e4433062e6af
runner=/tmp/fast64-runners/$runner_sha/run_fast64_trace_v2.sh
trace_config="$repo/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
framework=037f008b330eb230353b60edf126d6be9f45afdc
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
classification=FAST64_4_CAP16384_CANDIDATE_PENDING_RESOLUTION
run_root=/workspace/fast64-primary-r4-cap-recovery
output_root="$repo/docs/dtc_l1/fast64/generated/fast64_4_cap16384_recovery_v1"
dispatcher_sha=$(sha256sum "${BASH_SOURCE[0]}" | awk '{print $1}')

# workload|mode|Core label; exactly nine rows, fixed before candidate execution.
rows=(
  '2DConvolution|IO|658'
  'Gaussian|BASE|95'
  'Gaussian|IO|95'
  'Gaussian|OO|95'
  'Hotspot1|IO|95'
  'Hotspot1|OO|95'
  'LUD|BASE|95'
  'LUD|IO|95'
  'LUD|OO|95'
)

trace_for() {
  case "$1" in
    2DConvolution) printf '%s\n' /workspace/worktrees/accel-sim-decoupled-l2/hw_run/c2p-polybench-full-20260821/polybench/11.0/polybench-2DConvolution/NO_ARGS/traces/kernelslist.g ;;
    Gaussian) printf '%s\n' /workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/gaussian-rodinia-3.1/_s_256/traces/kernelslist.g ;;
    Hotspot1) printf '%s\n' /workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/hotspot-rodinia-3.1/1024_2_2___data_temp_1024___data_power_1024_output_out/traces/kernelslist.g ;;
    LUD) printf '%s\n' /workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/lud-rodinia-3.1/_i___data_512_dat/traces/kernelslist.g ;;
    *) echo CAP16384_UNKNOWN_WORKLOAD >&2; return 1 ;;
  esac
}

config_for() {
  case "$1" in
    BASE) printf '%s\n' "$repo/configs/dtc_l1/fast64/FAST64_BASE_CAP16384.config" ;;
    IO) printf '%s\n' "$repo/configs/dtc_l1/fast64/FAST64_IO_CAP16384.config" ;;
    OO) printf '%s\n' "$repo/configs/dtc_l1/fast64/FAST64_OO_CAP16384.config" ;;
    *) echo CAP16384_UNKNOWN_MODE >&2; return 1 ;;
  esac
}

config_id_for() { printf 'FAST64_%s_CAP16384_A1\n' "$1"; }

test -d "$core_repo" && git -C "$core_repo" cat-file -e "$core95^{commit}" && git -C "$core_repo" cat-file -e "$core658^{commit}"
git -C "$repo" cat-file -e "$framework^{commit}"
test -x "$runner" && test "$(sha256sum "$runner" | awk '{print $1}')" = "$runner_sha"
test $((8#$(stat -c %a "$runner") & 0222)) -eq 0
test -r "$trace_config"
test "$(grep -Fxc -- '-gpgpu_dtc_l1_lower_outstanding_cap 16384' "$repo/configs/dtc_l1/fast64/FAST64_BASE_CAP16384.config")" = 1
test "$(grep -Fxc -- '-gpgpu_dtc_l1_lower_outstanding_cap 16384' "$repo/configs/dtc_l1/fast64/FAST64_IO_CAP16384.config")" = 1
test "$(grep -Fxc -- '-gpgpu_dtc_l1_lower_outstanding_cap 16384' "$repo/configs/dtc_l1/fast64/FAST64_OO_CAP16384.config")" = 1

for index in "${!rows[@]}"; do
  IFS='|' read -r workload mode core_label <<<"${rows[$index]}"
  lower=${mode,,}; row="fast64_4_${workload}_${lower}_cap16384_core${core_label}_a1_v1"
  run="$run_root/$row"; output="$output_root/$row.json"; trace=$(trace_for "$workload"); config=$(config_for "$mode")
  test -r "$trace" && test -r "$config"
  for path in "$run" "$run.launcher.log" "$run.supervisor.tsv" "$output" "${output}.lock"; do
    test ! -e "$path" || { echo "CAP16384_TARGET_EXISTS_REFUSE_RERUN $path" >&2; exit 1; }
  done
done

if test "$dispatch" = 0; then
  printf 'FAST64_4_CAP16384_RECOVERY_V1_DRY_RUN_PASS\trows=%s\tdispatcher_sha=%s\n' "${#rows[@]}" "$dispatcher_sha"
  exit 0
fi

mkdir -p "$run_root" "$output_root"
exec 9>"$run_root/.fast64_4_cap16384_recovery_dispatch.lock"
flock -n 9 || { echo CAP16384_DISPATCH_LOCK_HELD >&2; exit 1; }
for index in "${!rows[@]}"; do
  IFS='|' read -r workload mode core_label <<<"${rows[$index]}"
  lower=${mode,,}; row="fast64_4_${workload}_${lower}_cap16384_core${core_label}_a1_v1"
  run="$run_root/$row"; output="$output_root/$row.json"; trace=$(trace_for "$workload"); config=$(config_for "$mode"); config_id=$(config_id_for "$mode")
  for path in "$run" "$run.launcher.log" "$run.supervisor.tsv" "$output" "${output}.lock"; do
    test ! -e "$path" || { echo "CAP16384_TARGET_RACED_REFUSE_RERUN $path" >&2; exit 1; }
  done
  if test "$core_label" = 95; then core="$core95"; runtime="$runtime95"; runtime_sha="$runtime95_sha"; else core="$core658"; runtime="$runtime658"; runtime_sha="$runtime658_sha"; fi
  test -x "$runtime" && test "$(sha256sum "$runtime" | awk '{print $1}')" = "$runtime_sha"
  uuid=$(cat /proc/sys/kernel/random/uuid)
  (
    exec 9>&-
    exec setsid "$runner" --simulator "$runtime" --config "$config" --trace "$trace" --trace-config "$trace_config" \
      --run-dir "$run" --cpu "${cpu[$index]}" --attempt-uuid "$uuid" --runner-sha256 "$runner_sha" \
      --immutable-runner-path "$runner" --framework-scientific-config-source-sha "$framework" \
      --core-source-head "$core" --observer-overlay-sha "$observer" --result-classification "$classification"
  ) >"$run.launcher.log" 2>&1 &
  supervisor=$!
  printf 'row\tsupervisor_pid\tcpu_slot\tattempt_uuid\tdispatcher_sha256\trunner_sha256\tcore_sha\truntime_sha256\tconfig_sha256\tclassification\n%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$row" "$supervisor" "${cpu[$index]}" "$uuid" "$dispatcher_sha" "$runner_sha" "$core" "$runtime_sha" "$(sha256sum "$config" | awk '{print $1}')" "$classification" >"$run.supervisor.tsv"
  setsid "$repo/util/dtc_l1/monitor_fast64_repaired_core_row_v2.sh" --run-dir "$run" --workload-id "$workload" --mode "$mode" \
    --config-id "$config_id" --config-file "$config" --core-sha "$core" --runtime-sha "$runtime_sha" --classification "$classification" \
    --output "$output" --log "${run}_closeout.log" --poll-seconds 120 >"${run}_monitor.log" 2>&1 &
  printf 'FAST64_4_CAP16384_RECOVERY_V1_DISPATCHED\trow=%s\tcpu=%s\tsupervisor=%s\tuuid=%s\n' "$row" "${cpu[$index]}" "$supervisor" "$uuid"
done
