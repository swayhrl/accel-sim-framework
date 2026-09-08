#!/usr/bin/env bash
# One-shot, future-only dispatch of exactly the five missing immutable FAST64
# R2 qualification rows.  It never opens, modifies, or names cohort-1 rows.
set -euo pipefail

usage() { echo "usage: $0 [--dry-run | --launch --resource-audit FILE]" >&2; exit 2; }
mode=dry-run
audit=
case "${1:-}" in
  ""|--dry-run) [ "$#" -le 1 ] || usage ;;
  --launch) mode=launch; test "${2:-}" = --resource-audit || usage; audit=${3:-}; [ "$#" = 3 ] || usage ;;
  *) usage ;;
esac

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs_root=/workspace/fast64-runs
core_root=/workspace/worktrees/gpgpu-sim-decoupled-l1-m5
expected_core=bbcbb5e7565417102087bc80b14c349b4e568c05
scientific_source=037f008b330eb230353b60edf126d6be9f45afdc
runtime=/tmp/dtc-fast64-telemetry-build-sEWez4/accel-sim.out
expected_runtime=6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041
observer_sha=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
expected_runner=bf9a84c8aab54ccd5d00a8465d69669cfac78012b783c3cfd9e0e4433062e6af
runner_source="$repo_root/util/dtc_l1/run_fast64_trace_v2.sh"
immutable_runner="/tmp/fast64-runners/$expected_runner/run_fast64_trace_v2.sh"
trace_config="$repo_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
selector="$repo_root/util/dtc_l1/select_fast64_r2_cpus.py"
rows=(
  'fast64_1r2_bicg_oo_cap8192_a1|BICG|OO|FAST64_OO.config'
  'fast64_1r2_bicg_io_cap1048576_a1|BICG|IO|FAST64_IO_CAP1048576.config'
  'fast64_1r2_bicg_oo_cap1048576_a1|BICG|OO|FAST64_OO_CAP1048576.config'
  'fast64_1r2_gesummv_io_cap8192_a1|GESUMMV|IO|FAST64_IO.config'
  'fast64_1r2_gesummv_io_cap1048576_a1|GESUMMV|IO|FAST64_IO_CAP1048576.config'
)

test "$(git -C "$core_root" rev-parse HEAD)" = "$expected_core"
git -C "$repo_root" rev-parse --verify "$scientific_source^{commit}" >/dev/null
test -x "$runtime" && test "$(sha256sum "$runtime" | awk '{print $1}')" = "$expected_runtime"
test -x "$runner_source" && test "$(sha256sum "$runner_source" | awk '{print $1}')" = "$expected_runner"
test -x "$immutable_runner" && test "$(sha256sum "$immutable_runner" | awk '{print $1}')" = "$expected_runner"
test $((8#$(stat -c %a "$immutable_runner") & 0222)) -eq 0
test -r "$trace_config" && test -r "$selector"

for row in "${rows[@]}"; do
  IFS='|' read -r name workload _ config <<<"$row"
  for path in "$runs_root/$name" "$runs_root/$name.launcher.log" "$runs_root/$name.supervisor.tsv"; do
    test ! -e "$path" || { echo "R2_CONTINUATION_TARGET_NOT_ABSENT $path" >&2; exit 1; }
  done
  test "$(sha256sum "$repo_root/configs/dtc_l1/fast64/$config" | awk '{print $1}')" = \
       "$(git -C "$repo_root" show "$scientific_source:configs/dtc_l1/fast64/$config" | sha256sum | awk '{print $1}')"
  trace_root=$(awk -F '\t' -v workload="${workload,,}" '$1 == workload { print $2; exit }' "$repo_root/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv")
  test -n "$trace_root" && test -r "$trace_root/kernelslist.g"
done
test "$(sha256sum "$trace_config" | awk '{print $1}')" = \
     "$(git -C "$repo_root" show "$scientific_source:gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config" | sha256sum | awk '{print $1}')"

selection=$(python3 "$selector" --format tsv)
candidate_count=$(printf '%s\n' "$selection" | awk -F '\t' '$1 == "available_distinct_physical_cores" { print $2; exit }')
candidate_cpus=$(printf '%s\n' "$selection" | awk -F '\t' '$1 == "candidate_cpus" { print $2; exit }')
IFS=',' read -r -a cpus <<<"$candidate_cpus"
test "$candidate_count" -ge 5 && test "${#cpus[@]}" -ge 5

if [ "$mode" = dry-run ]; then
  printf 'FAST64_R2_CONTINUATION_DRY_RUN_PASS\trows=5\tavailable_distinct_physical_cores=%s\tcandidate_cpus=%s\trunner_sha256=%s\n' "$candidate_count" "$candidate_cpus" "$expected_runner"
  exit 0
fi

test -r "$audit" || { echo 'R2_CONTINUATION_AUDIT_UNAVAILABLE' >&2; exit 1; }
awk -F '\t' '
  $1 == "schema" && $2 == "FAST64_R2_CONTINUATION_RESOURCE_AUDIT_V1" { schema=1 }
  $1 == "safe_to_launch" && $2 == "YES" { safe=1 }
  $1 == "authorized_workers" && $2 == "5" { workers=1 }
  $1 == "requested_new_workers" && $2 == "5" { requested=1 }
  $1 == "swap_so_delta" && $2 == "0" { swap=1 }
  $1 == "oom_kill_delta" && $2 == "0" { oom=1 }
  $1 == "memory_psi_avg10" && ($2 == "0" || $2 == "0.00") { psi=1 }
  $1 == "available_distinct_physical_cores" && $2 >= 5 { cpu=1 }
  $1 == "memory_required_bytes" && $2 ~ /^[0-9]+$/ { memory=1 }
  $1 == "output_required_bytes" && $2 ~ /^[0-9]+$/ { output=1 }
  END { exit !(schema && safe && workers && requested && swap && oom && psi && cpu && memory && output) }
' "$audit" || { echo 'R2_CONTINUATION_AUDIT_INCOMPLETE_OR_UNSAFE' >&2; exit 1; }

exec 9>"$runs_root/.fast64_1_r2_full_wave_continuation_dispatch.lock"
flock -n 9 || { echo 'R2_CONTINUATION_LOCK_HELD' >&2; exit 1; }
for row in "${rows[@]}"; do
  IFS='|' read -r name _ <<<"$row"
  for path in "$runs_root/$name" "$runs_root/$name.launcher.log" "$runs_root/$name.supervisor.tsv"; do
    test ! -e "$path" || { echo "R2_CONTINUATION_TARGET_RACED $path" >&2; exit 1; }
  done
done
for i in "${!rows[@]}"; do
  IFS='|' read -r name workload _ config <<<"${rows[$i]}"
  trace_root=$(awk -F '\t' -v workload="${workload,,}" '$1 == workload { print $2; exit }' "$repo_root/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv")
  uuid=$(cat /proc/sys/kernel/random/uuid)
  (
    exec 9>&-
    exec setsid "$immutable_runner" --simulator "$runtime" \
      --config "$repo_root/configs/dtc_l1/fast64/$config" --trace "$trace_root/kernelslist.g" \
      --trace-config "$trace_config" --run-dir "$runs_root/$name" --cpu "${cpus[$i]}" \
      --attempt-uuid "$uuid" --runner-sha256 "$expected_runner" --immutable-runner-path "$immutable_runner" \
      --framework-scientific-config-source-sha "$scientific_source" --core-source-head "$expected_core" \
      --observer-overlay-sha "$observer_sha" --result-classification FAST64_1_R2_FULL_WAVE_IMMUTABLE_RECOVERY
  ) >"$runs_root/$name.launcher.log" 2>&1 &
  supervisor=$!
  {
    printf 'row\tsupervisor_pid\tcpu_slot\tattempt_uuid\trunner_sha256\timmutable_runner\tscientific_config_source\tcore_sha\truntime_sha256\n'
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$supervisor" "${cpus[$i]}" "$uuid" "$expected_runner" "$immutable_runner" "$scientific_source" "$expected_core" "$expected_runtime"
  } >"$runs_root/$name.supervisor.tsv"
  printf 'FAST64_R2_CONTINUATION_DISPATCHED\trow=%s\tcpu_slot=%s\tsupervisor=%s\tattempt_uuid=%s\n' "$name" "${cpus[$i]}" "$supervisor" "$uuid"
done
