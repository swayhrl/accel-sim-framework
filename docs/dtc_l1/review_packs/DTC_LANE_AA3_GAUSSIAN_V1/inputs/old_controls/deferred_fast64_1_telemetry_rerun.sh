#!/usr/bin/env bash
# Wait for telemetry-incomplete FAST64.1 anchors to terminate naturally, then
# dispatch their required new-Core evidence replacements without overwriting.
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs_root=/workspace/fast64-runs
core_root=/workspace/worktrees/gpgpu-sim-decoupled-l1-m5
expected_core=bbcbb5e7565417102087bc80b14c349b4e568c05
runtime=/tmp/dtc-fast64-telemetry-build-sEWez4/accel-sim.out
expected_runtime=6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041
runner="$repo_root/util/dtc_l1/run_fast64_trace.sh"

old_rows=(
  fast64_1_bicg_base_cap8192_a1
  fast64_1_bicg_io_cap8192_a1
  fast64_1_bicg_oo_cap8192_a1
  fast64_1_bicg_io_cap1048576_a1
  fast64_1_bicg_oo_cap1048576_a1
  fast64_1_gesummv_io_cap8192_a1
  fast64_1_gesummv_io_cap1048576_a1
)
new_rows=(
  'fast64_1r1_bicg_base_cap8192_a1|BICG|BASE|FAST64_BASE.config|8192|74'
  'fast64_1r1_bicg_io_cap8192_a1|BICG|IO|FAST64_IO.config|8192|75'
  'fast64_1r1_bicg_oo_cap8192_a1|BICG|OO|FAST64_OO.config|8192|76'
  'fast64_1r1_bicg_io_cap1048576_a1|BICG|IO|FAST64_IO_CAP1048576.config|1048576|77'
  'fast64_1r1_bicg_oo_cap1048576_a1|BICG|OO|FAST64_OO_CAP1048576.config|1048576|78'
  'fast64_1r1_gesummv_io_cap8192_a1|GESUMMV|IO|FAST64_IO.config|8192|79'
  'fast64_1r1_gesummv_io_cap1048576_a1|GESUMMV|IO|FAST64_IO_CAP1048576.config|1048576|80'
)

terminal_status() {
  awk -F '\t' '$1 == "simulator_exit_status" { value=$2 } END { print value }' \
    "$runs_root/$1/RUN_MANIFEST.tsv" 2>/dev/null
}

while :; do
  pending=0
  for old in "${old_rows[@]}"; do
    status=$(terminal_status "$old")
    if [ -z "$status" ]; then
      pending=1
      continue
    fi
    if [ "$status" != 0 ]; then
      echo "OLD_ROW_NONZERO $old status=$status" >&2
      exit 1
    fi
  done
  [ "$pending" -eq 0 ] && break
  sleep 60
done

test "$(git -C "$core_root" rev-parse HEAD)" = "$expected_core"
test -x "$runtime"
test "$(sha256sum "$runtime" | awk '{print $1}')" = "$expected_runtime"
test -x "$runner"

for row in "${new_rows[@]}"; do
  IFS='|' read -r name workload mode config cap cpu <<<"$row"
  test ! -e "$runs_root/$name" || { echo "TARGET_EXISTS $name" >&2; exit 1; }
  trace_root=$(awk -F '\t' -v workload="${workload,,}" '$1 == workload { print $2; exit }' \
    "$repo_root/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv")
  test -r "$trace_root/kernelslist.g"
  test -r "$repo_root/configs/dtc_l1/fast64/$config"
done

for row in "${new_rows[@]}"; do
  IFS='|' read -r name workload mode config cap cpu <<<"$row"
  trace_root=$(awk -F '\t' -v workload="${workload,,}" '$1 == workload { print $2; exit }' \
    "$repo_root/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv")
  setsid "$runner" --simulator "$runtime" \
    --config "$repo_root/configs/dtc_l1/fast64/$config" \
    --trace "$trace_root/kernelslist.g" --run-dir "$runs_root/$name" --cpu "$cpu" \
    >"$runs_root/$name.launcher.log" 2>&1 &
  supervisor=$!
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$supervisor" "$cpu" "$workload" "$mode" "$cap" \
    >"$runs_root/$name.supervisor.tsv"
  echo "DISPATCHED $name supervisor=$supervisor cpu=$cpu cap=$cap"
done
