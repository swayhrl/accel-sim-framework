#!/usr/bin/env bash
# Dispatch the seven isolated bbcbb5e FAST64.1 qualification rows now.
# This deliberately does not inspect, signal, or modify the telemetry-
# incomplete original-Core anchors. Existing target namespaces are a hard
# failure, so this controller cannot overwrite or duplicate a formal row.
set -euo pipefail

dry_run=0
if [ "${1:-}" = "--dry-run" ]; then
  dry_run=1
  shift
fi
test "$#" = 0 || { echo "usage: $0 [--dry-run]" >&2; exit 2; }

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs_root=/workspace/fast64-runs
core_root=/workspace/worktrees/gpgpu-sim-decoupled-l1-m5
expected_core=bbcbb5e7565417102087bc80b14c349b4e568c05
runtime=/tmp/dtc-fast64-telemetry-build-sEWez4/accel-sim.out
expected_runtime=6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041
observer_sha=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
# Existing r1 jobs retain the historical runner they already mapped.  Any
# recovery dispatch uses the v2 atomic-namespace runner and can never reopen a
# historical output directory.
runner="$repo_root/util/dtc_l1/run_fast64_trace_v2.sh"
lock_file="$runs_root/.fast64_1_r1_immediate_dispatch.lock"

new_rows=(
  'fast64_1r1_bicg_base_cap8192_a1|BICG|BASE|FAST64_BASE.config|8192|74'
  'fast64_1r1_bicg_io_cap8192_a1|BICG|IO|FAST64_IO.config|8192|75'
  'fast64_1r1_bicg_oo_cap8192_a1|BICG|OO|FAST64_OO.config|8192|76'
  'fast64_1r1_bicg_io_cap1048576_a1|BICG|IO|FAST64_IO_CAP1048576.config|1048576|77'
  'fast64_1r1_bicg_oo_cap1048576_a1|BICG|OO|FAST64_OO_CAP1048576.config|1048576|78'
  'fast64_1r1_gesummv_io_cap8192_a1|GESUMMV|IO|FAST64_IO.config|8192|79'
  'fast64_1r1_gesummv_io_cap1048576_a1|GESUMMV|IO|FAST64_IO_CAP1048576.config|1048576|80'
)

test "$(git -C "$core_root" rev-parse HEAD)" = "$expected_core"
test -x "$runtime"
test "$(sha256sum "$runtime" | awk '{print $1}')" = "$expected_runtime"
test -x "$runner"
framework_sha=$(git -C "$repo_root" rev-parse HEAD)

# Lock only covers preflight and detached launch. The target directory created
# by the runner is the persistent exactly-once witness.
exec 9>"$lock_file"
flock -n 9 || { echo "R1_DISPATCH_LOCK_HELD $lock_file" >&2; exit 1; }

for row in "${new_rows[@]}"; do
  IFS='|' read -r name workload mode config cap cpu <<<"$row"
  test ! -e "$runs_root/$name" || { echo "TARGET_EXISTS $name" >&2; exit 1; }
  trace_root=$(awk -F '\t' -v workload="${workload,,}" '$1 == workload { print $2; exit }' \
    "$repo_root/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv")
  test -n "$trace_root"
  test -r "$trace_root/kernelslist.g"
  test -r "$repo_root/configs/dtc_l1/fast64/$config"
  printf 'PREFLIGHT_OK\t%s\t%s\t%s\t%s\t%s\n' "$name" "$workload" "$mode" "$cap" "$cpu"
done

if [ "$dry_run" = 1 ]; then
  printf 'DRY_RUN_PASS\tframework_source_head=%s\tcore_source_head=%s\n' \
    "$framework_sha" "$expected_core"
  exit 0
fi

for row in "${new_rows[@]}"; do
  IFS='|' read -r name workload mode config cap cpu <<<"$row"
  trace_root=$(awk -F '\t' -v workload="${workload,,}" '$1 == workload { print $2; exit }' \
    "$repo_root/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv")
  setsid "$runner" --simulator "$runtime" \
    --config "$repo_root/configs/dtc_l1/fast64/$config" \
    --trace "$trace_root/kernelslist.g" --run-dir "$runs_root/$name" --cpu "$cpu" \
    --framework-source-head "$framework_sha" --core-source-head "$expected_core" \
    --observer-overlay-sha "$observer_sha" \
    >"$runs_root/$name.launcher.log" 2>&1 &
  supervisor=$!
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$name" "$supervisor" "$cpu" "$workload" "$mode" "$cap" "$framework_sha" "$expected_core" \
    >"$runs_root/$name.supervisor.tsv"
  echo "DISPATCHED $name supervisor=$supervisor cpu=$cpu cap=$cap"
done
