#!/usr/bin/env bash
# Future-only BICG fallback for FAST64.2's coupled stress.  It will not launch
# without a fresh safe audit, and it never touches frozen R2 infrastructure.
set -euo pipefail

usage() { echo "usage: $0 [--dry-run | --launch --resource-audit FILE]" >&2; exit 2; }
mode=dry-run audit=
case "${1:-}" in
  ""|--dry-run) [ "$#" -le 1 ] || usage ;;
  --launch) mode=launch; test "${2:-}" = --resource-audit || usage; audit=${3:-}; [ "$#" = 3 ] || usage ;;
  *) usage ;;
esac

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs=/workspace/fast64-runs
core=/workspace/worktrees/gpgpu-sim-decoupled-l1-m5
core_sha=bbcbb5e7565417102087bc80b14c349b4e568c05
framework_sha=037f008b330eb230353b60edf126d6be9f45afdc
runtime=/tmp/dtc-fast64-telemetry-build-sEWez4/accel-sim.out
runtime_sha=6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041
observer_sha=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
runner_sha=bf9a84c8aab54ccd5d00a8465d69669cfac78012b783c3cfd9e0e4433062e6af
runner=/tmp/fast64-runners/$runner_sha/run_fast64_trace_v2.sh
config="$runs/overlays/FAST64_IO_COUPLED_STRESS_CAP512_PIB1.config"
provenance="$config.PROVENANCE.tsv"
trace_config="$repo/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
row=fast64_2_precomputed_bicg_io_coupled_cap512_pib1_a1_r2
run="$runs/$row"
classification=PRECOMPUTED_FAST64_2_COUPLED_STRESS_PENDING_FAST64_1_ACCEPTANCE

test "$(git -C "$core" rev-parse HEAD)" = "$core_sha"
git -C "$repo" rev-parse --verify "$framework_sha^{commit}" >/dev/null
test -x "$runtime" && test "$(sha256sum "$runtime" | awk '{print $1}')" = "$runtime_sha"
test -x "$runner" && test "$(sha256sum "$runner" | awk '{print $1}')" = "$runner_sha"
test $((8#$(stat -c %a "$runner") & 0222)) -eq 0
test -r "$config" && test -r "$provenance" && test -r "$trace_config"
test "$(sha256sum "$trace_config" | awk '{print $1}')" = "$(git -C "$repo" show "$framework_sha:gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config" | sha256sum | awk '{print $1}')"
test "$(grep -F -- '-gpgpu_dtc_l1_lower_outstanding_cap ' "$config" | tail -1)" = '-gpgpu_dtc_l1_lower_outstanding_cap 512'
test "$(grep -Fxc -- '-gpgpu_dtc_l1_io_pib_entries 1' "$config")" = 1
test "$(awk -F '\t' '$1=="output_config_sha256" {print $2}' "$provenance")" = "$(sha256sum "$config" | awk '{print $1}')"
test "$(sha256sum "$config" | awk '{print $1}')" = 9b01eb0c163ad825743a19e7192f4e4a934791ae11aee30699d2eda5fe42d4ba
trace_root=$(awk -F '\t' '$1=="bicg" {print $2;exit}' "$repo/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv")
test -n "$trace_root" && test -r "$trace_root/kernelslist.g"
for p in "$run" "$run.launcher.log" "$run.supervisor.tsv"; do test ! -e "$p" || { echo "FAST64_2_BICG_TARGET_EXISTS $p" >&2; exit 1; }; done
cpu=$(python3 "$repo/util/dtc_l1/select_fast64_r2_cpus.py" --format tsv | awk -F '\t' '$1=="candidate_cpus" {split($2,a,",");print a[1];exit}')
test -n "$cpu"

if [ "$mode" = dry-run ]; then
  printf 'FAST64_2_BICG_FALLBACK_DRY_RUN_PASS\trow=%s\tcpu=%s\trunner_sha256=%s\n' "$row" "$cpu" "$runner_sha"
  exit 0
fi
test -r "$audit"
awk -F '\t' '
  $1=="schema"&&$2=="FAST64_FUTURE_PRECOMPUTE_RESOURCE_AUDIT_V1"{s=1}
  $1=="safe_to_launch"&&$2=="YES"{y=1}
  $1=="authorized_workers"&&$2=="1"{w=1}
  $1=="swap_so_delta"&&$2=="0"{a=1}
  $1=="oom_kill_delta"&&$2=="0"{b=1}
  $1=="memory_psi_avg10"&&($2=="0"||$2=="0.00"){c=1}
  END{exit !(s&&y&&w&&a&&b&&c)}
' "$audit" || { echo FAST64_2_BICG_RESOURCE_AUDIT_UNSAFE >&2; exit 1; }
exec 9>"$runs/.fast64_2_bicg_coupled_stress_v2_dispatch.lock"
flock -n 9 || { echo FAST64_2_BICG_DISPATCH_LOCK_HELD >&2; exit 1; }
for p in "$run" "$run.launcher.log" "$run.supervisor.tsv"; do test ! -e "$p" || { echo "FAST64_2_BICG_TARGET_RACED $p" >&2; exit 1; }; done
uuid=$(cat /proc/sys/kernel/random/uuid)
(
  exec 9>&-
  exec setsid "$runner" --simulator "$runtime" --config "$config" --trace "$trace_root/kernelslist.g" --trace-config "$trace_config" --run-dir "$run" --cpu "$cpu" --attempt-uuid "$uuid" --runner-sha256 "$runner_sha" --immutable-runner-path "$runner" --framework-scientific-config-source-sha "$framework_sha" --core-source-head "$core_sha" --observer-overlay-sha "$observer_sha" --result-classification "$classification"
) >"$run.launcher.log" 2>&1 &
supervisor=$!
printf 'row\tsupervisor_pid\tcpu_slot\tattempt_uuid\trunner_sha256\timmutable_runner\tcore_sha\truntime_sha256\tclassification\n%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$row" "$supervisor" "$cpu" "$uuid" "$runner_sha" "$runner" "$core_sha" "$runtime_sha" "$classification" >"$run.supervisor.tsv"
printf 'FAST64_2_BICG_FALLBACK_DISPATCHED\trow=%s\tcpu=%s\tsupervisor=%s\tattempt_uuid=%s\n' "$row" "$cpu" "$supervisor" "$uuid"
