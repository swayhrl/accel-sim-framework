#!/usr/bin/env bash
# Prepare, and only with explicit guarded --launch dispatch, the one invalidated
# FAST64.1 BICG OO@8192 replacement.  It can never address a historical r1 row.
set -euo pipefail

usage() {
  echo "usage: $0 [--dry-run | --launch --resource-audit FILE]" >&2
  exit 2
}

mode=dry-run
resource_audit=
if [ "$#" -gt 0 ]; then
  case "$1" in
    --dry-run) shift ;;
    --launch) mode=launch; shift ;;
    *) usage ;;
  esac
fi
if [ "$mode" = launch ]; then
  test "${1:-}" = --resource-audit || usage
  resource_audit=${2:-}
  shift 2
fi
test "$#" = 0 || usage

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs_root=/workspace/fast64-runs
core_root=/workspace/worktrees/gpgpu-sim-decoupled-l1-m5
expected_core=bbcbb5e7565417102087bc80b14c349b4e568c05
# This is the source snapshot of the frozen formal config/payload, not this
# controller's review commit or the immutable runner identity.
scientific_config_source=037f008b330eb230353b60edf126d6be9f45afdc
runtime=/tmp/dtc-fast64-telemetry-build-sEWez4/accel-sim.out
expected_runtime=6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041
observer_sha=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
runner_source="$repo_root/util/dtc_l1/run_fast64_trace_v2.sh"
trace_config="$repo_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
row=fast64_1r2_bicg_oo_cap8192_a1
run_dir="$runs_root/$row"
launcher_log="$runs_root/$row.launcher.log"
supervisor_tsv="$runs_root/$row.supervisor.tsv"
contaminated="$runs_root/fast64_1r1_bicg_oo_cap8192_a1"
immutable_root=/tmp/fast64-runners

test "$(git -C "$core_root" rev-parse HEAD)" = "$expected_core"
test -x "$runtime"
test "$(sha256sum "$runtime" | awk '{print $1}')" = "$expected_runtime"
test -x "$runner_source" && test -r "$trace_config"
runner_sha=$(sha256sum "$runner_source" | awk '{print $1}')
immutable_dir="$immutable_root/$runner_sha"
immutable_runner="$immutable_dir/run_fast64_trace_v2.sh"
trace_root=$(awk -F '\t' '$1 == "bicg" { print $2; exit }' \
  "$repo_root/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv")
test -n "$trace_root" && test -r "$trace_root/kernelslist.g"
config="$repo_root/configs/dtc_l1/fast64/FAST64_OO.config"
test -r "$config"
for target in "$run_dir" "$launcher_log" "$supervisor_tsv"; do
  test ! -e "$target" || { echo "R2_TARGET_ALREADY_EXISTS $target" >&2; exit 1; }
done

if [ "$mode" = dry-run ]; then
  printf 'R2_PREPARE_DRY_RUN_PASS\trow=%s\trunner_sha256=%s\timmutable_runner=%s\tscientific_config_source=%s\n' \
    "$row" "$runner_sha" "$immutable_runner" "$scientific_config_source"
  exit 0
fi

# Launch is fail-closed: a fresh audit must explicitly declare safe headroom,
# and the contaminated historical epoch must be terminal before replacement.
test -r "$resource_audit" || { echo "R2_RESOURCE_AUDIT_UNAVAILABLE" >&2; exit 1; }
awk -F '\t' '$1 == "schema" && $2 == "FAST64_R2_RESOURCE_AUDIT_V1" { schema=1 } $1 == "safe_to_launch" && $2 == "YES" { safe=1 } END { exit !(schema && safe) }' \
  "$resource_audit" || { echo "R2_RESOURCE_AUDIT_NOT_SAFE" >&2; exit 1; }
test -f "$contaminated/RUN_MANIFEST.tsv"
awk -F '\t' '$1 == "simulator_exit_status" { found=1 } END { exit !found }' \
  "$contaminated/RUN_MANIFEST.tsv" || { echo "R2_CONTAMINATED_EPOCH_NOT_TERMINAL" >&2; exit 1; }

# Materialize one SHA-addressed copy only. Existing bytes are accepted solely
# after exact re-verification; no mutable worktree path is ever executed.
if [ ! -d "$immutable_dir" ]; then
  mkdir -p -- "$immutable_dir"
fi
if [ ! -e "$immutable_runner" ]; then
  cp -- "$runner_source" "$immutable_runner"
  chmod 555 "$immutable_runner"
fi
test "$(sha256sum "$immutable_runner" | awk '{print $1}')" = "$runner_sha"
test $((8#$(stat -c %a "$immutable_runner") & 0222)) -eq 0
chmod 555 "$immutable_dir"

exec 9>"$runs_root/.fast64_1_r2_recovery_dispatch.lock"
flock -n 9 || { echo "R2_DISPATCH_LOCK_HELD" >&2; exit 1; }
for target in "$run_dir" "$launcher_log" "$supervisor_tsv"; do
  test ! -e "$target" || { echo "R2_TARGET_RACED $target" >&2; exit 1; }
done
attempt_uuid=$(cat /proc/sys/kernel/random/uuid)
setsid "$immutable_runner" --simulator "$runtime" --config "$config" \
  --trace "$trace_root/kernelslist.g" --trace-config "$trace_config" \
  --run-dir "$run_dir" --cpu 76 --attempt-uuid "$attempt_uuid" \
  --runner-sha256 "$runner_sha" --immutable-runner-path "$immutable_runner" \
  --framework-scientific-config-source-sha "$scientific_config_source" \
  --core-source-head "$expected_core" --observer-overlay-sha "$observer_sha" \
  --result-classification FAST64_1_R2_IMMUTABLE_RECOVERY \
  >"$launcher_log" 2>&1 &
supervisor=$!
printf 'row\tsupervisor_pid\tattempt_uuid\trunner_sha256\timmutable_runner\tscientific_config_source\tcore_sha\truntime_sha256\n' >"$supervisor_tsv"
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$row" "$supervisor" "$attempt_uuid" \
  "$runner_sha" "$immutable_runner" "$scientific_config_source" "$expected_core" "$expected_runtime" >>"$supervisor_tsv"
echo "R2_DISPATCHED row=$row supervisor=$supervisor attempt_uuid=$attempt_uuid"
