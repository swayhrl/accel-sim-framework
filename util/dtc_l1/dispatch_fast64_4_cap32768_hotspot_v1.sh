#!/usr/bin/env bash
# Future-only second monotonic-cap probe for strict-terminal Hotspot1 IO/OO.
set -euo pipefail
case "$1" in --dry-run) dispatch=0;; --dispatch) dispatch=1;; *) echo USAGE >&2; exit 2;; esac
shift
test "$1" = --cpu-list && cpus="$2" && test "$#" = 2 || { echo CPU_LIST_REQUIRED >&2; exit 2; }
test "$(printf '%s' "$cpus" | awk -F, '{print NF}')" = 2 || { echo CAP32768_CPU_COUNT_MUST_BE_2 >&2; exit 2; }
cpu_io=$(printf '%s' "$cpus" | cut -d, -f1); cpu_oo=$(printf '%s' "$cpus" | cut -d, -f2)
[[ "$cpu_io" =~ ^[0-9]+$ && "$cpu_oo" =~ ^[0-9]+$ && "$cpu_io" != "$cpu_oo" ]] || { echo CAP32768_CPU_INVALID >&2; exit 2; }

repo=/workspace/worktrees/accel-sim-decoupled-l1-fast64
core_repo=/workspace/worktrees/gpgpu-sim-fast64-formal-95ccdb7a
core=95ccdb7a056f2d53f740d90869785cac6d4ee0f5
runtime=/tmp/dtc-fast64-zero-access-formal-95ccdb7a/accel-sim.out
runtime_sha=462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9
runner_sha=bf9a84c8aab54ccd5d00a8465d69669cfac78012b783c3cfd9e0e4433062e6af
runner=/tmp/fast64-runners/$runner_sha/run_fast64_trace_v2.sh
trace=/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/hotspot-rodinia-3.1/1024_2_2___data_temp_1024___data_power_1024_output_out/traces/kernelslist.g
trace_config=$repo/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config
framework=037f008b330eb230353b60edf126d6be9f45afdc
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
classification=FAST64_4_CAP32768_CANDIDATE_PENDING_RESOLUTION
run_root=/workspace/fast64-primary-r4-cap-recovery
output_root=$repo/docs/dtc_l1/fast64/generated/fast64_4_cap32768_recovery_v1
dispatcher_sha=$(sha256sum "$0" | awk '{print $1}')

test -d "$core_repo" && git -C "$core_repo" cat-file -e "$core^{commit}" && git -C "$repo" cat-file -e "$framework^{commit}"
test -x "$runtime" && test "$(sha256sum "$runtime" | awk '{print $1}')" = "$runtime_sha"
test -x "$runner" && test "$(sha256sum "$runner" | awk '{print $1}')" = "$runner_sha" && test $((8#$(stat -c %a "$runner") & 0222)) -eq 0
test -r "$trace" && test -r "$trace_config"
for mode in IO OO; do
  config=$repo/configs/dtc_l1/fast64/FAST64_${mode}_CAP32768.config
  row=fast64_4_Hotspot1_$(printf '%s' "$mode" | tr A-Z a-z)_cap32768_core95_a1_v1
  test -r "$config" && test "$(grep -Fxc -- '-gpgpu_dtc_l1_lower_outstanding_cap 32768' "$config")" = 1
  for path in "$run_root/$row" "$run_root/$row.launcher.log" "$run_root/$row.supervisor.tsv" "$output_root/$row.json" "$output_root/$row.json.lock"; do test ! -e "$path" || { echo "CAP32768_TARGET_EXISTS_REFUSE_RERUN $path" >&2; exit 1; }; done
done
if test "$dispatch" = 0; then printf 'FAST64_4_CAP32768_HOTSPOT_V1_DRY_RUN_PASS\tdispatcher_sha=%s\n' "$dispatcher_sha"; exit 0; fi
mkdir -p "$run_root" "$output_root"; exec 9>"$run_root/.fast64_4_cap32768_hotspot_dispatch.lock"; flock -n 9 || { echo CAP32768_DISPATCH_LOCK_HELD >&2; exit 1; }
for spec in IO:$cpu_io OO:$cpu_oo; do
  mode=$(printf '%s' "$spec" | cut -d: -f1); cpu=$(printf '%s' "$spec" | cut -d: -f2); lower=$(printf '%s' "$mode" | tr A-Z a-z); row=fast64_4_Hotspot1_${lower}_cap32768_core95_a1_v1
  run=$run_root/$row; output=$output_root/$row.json; config=$repo/configs/dtc_l1/fast64/FAST64_${mode}_CAP32768.config; uuid=$(cat /proc/sys/kernel/random/uuid)
  (exec 9>&-; exec setsid "$runner" --simulator "$runtime" --config "$config" --trace "$trace" --trace-config "$trace_config" --run-dir "$run" --cpu "$cpu" --attempt-uuid "$uuid" --runner-sha256 "$runner_sha" --immutable-runner-path "$runner" --framework-scientific-config-source-sha "$framework" --core-source-head "$core" --observer-overlay-sha "$observer" --result-classification "$classification") >"$run.launcher.log" 2>&1 &
  supervisor=$!
  printf 'row\tsupervisor_pid\tcpu_slot\tattempt_uuid\tdispatcher_sha256\trunner_sha256\tcore_sha\truntime_sha256\tconfig_sha256\tclassification\n%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$row" "$supervisor" "$cpu" "$uuid" "$dispatcher_sha" "$runner_sha" "$core" "$runtime_sha" "$(sha256sum "$config" | awk '{print $1}')" "$classification" >"$run.supervisor.tsv"
  setsid "$repo/util/dtc_l1/monitor_fast64_repaired_core_row_v2.sh" --run-dir "$run" --workload-id Hotspot1 --mode "$mode" --config-id "FAST64_${mode}_CAP32768_A1" --config-file "$config" --core-sha "$core" --runtime-sha "$runtime_sha" --classification "$classification" --output "$output" --log "$run.closeout.log" --poll-seconds 120 >"$run.monitor.log" 2>&1 &
  printf 'FAST64_4_CAP32768_HOTSPOT_V1_DISPATCHED\trow=%s\tcpu=%s\tsupervisor=%s\tuuid=%s\n' "$row" "$cpu" "$supervisor" "$uuid"
done
