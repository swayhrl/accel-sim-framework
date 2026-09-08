#!/usr/bin/env bash
# Prepare, and only under an explicit audited --launch, the complete immutable
# FAST64.1 r2 qualification wave. It never addresses a historical r1 namespace.
set -euo pipefail

usage() {
  echo "usage: $0 [--dry-run | --launch --resource-audit FILE]" >&2
  exit 2
}

dispatch_mode=dry-run
resource_audit=
if [ "$#" -gt 0 ]; then
  case "$1" in
    --dry-run) shift ;;
    --launch) dispatch_mode=launch; shift ;;
    *) usage ;;
  esac
fi
if [ "$dispatch_mode" = launch ]; then
  test "${1:-}" = --resource-audit || usage
  resource_audit=${2:-}
  shift 2
fi
test "$#" = 0 || usage

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs_root=/workspace/fast64-runs
core_root=/workspace/worktrees/gpgpu-sim-decoupled-l1-m5
expected_core=bbcbb5e7565417102087bc80b14c349b4e568c05
# Frozen payload/config source, deliberately independent of controller commits.
scientific_config_source=037f008b330eb230353b60edf126d6be9f45afdc
runtime=/tmp/dtc-fast64-telemetry-build-sEWez4/accel-sim.out
expected_runtime=6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041
observer_sha=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
runner_source="$repo_root/util/dtc_l1/run_fast64_trace_v2.sh"
cpu_selector="$repo_root/util/dtc_l1/select_fast64_r2_cpus.py"
trace_config="$repo_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
immutable_root=/tmp/fast64-runners
rows=(
  'fast64_1r2_bicg_base_cap8192_a1|BICG|BASE|FAST64_BASE.config'
  'fast64_1r2_bicg_io_cap8192_a1|BICG|IO|FAST64_IO.config'
  'fast64_1r2_bicg_oo_cap8192_a1|BICG|OO|FAST64_OO.config'
  'fast64_1r2_bicg_io_cap1048576_a1|BICG|IO|FAST64_IO_CAP1048576.config'
  'fast64_1r2_bicg_oo_cap1048576_a1|BICG|OO|FAST64_OO_CAP1048576.config'
  'fast64_1r2_gesummv_io_cap8192_a1|GESUMMV|IO|FAST64_IO.config'
  'fast64_1r2_gesummv_io_cap1048576_a1|GESUMMV|IO|FAST64_IO_CAP1048576.config'
)
# Host placement is deliberately not part of a row's scientific identity.  The
# selector is topology-aware: it excludes only singleton/narrow affinity
# reservations, ranks remaining distinct physical cores by current scheduler
# occupancy, and treats broad affinity as soft throughput contention.
# Test-only proc/candidate overrides feed synthetic selector regression tests.
proc_root=${FAST64_PROC_ROOT:-/proc}
case "$proc_root" in
  /*) ;;
  *) echo "R2_PROC_ROOT_MUST_BE_ABSOLUTE $proc_root" >&2; exit 2 ;;
esac

test "$(git -C "$core_root" rev-parse HEAD)" = "$expected_core"
test -x "$runtime"
test "$(sha256sum "$runtime" | awk '{print $1}')" = "$expected_runtime"
test -x "$runner_source" && test -r "$trace_config" && test -r "$cpu_selector"
runner_sha=$(sha256sum "$runner_source" | awk '{print $1}')
immutable_dir="$immutable_root/$runner_sha"
immutable_runner="$immutable_dir/run_fast64_trace_v2.sh"
eligible_rows=()
for row in "${rows[@]}"; do
  IFS='|' read -r name workload row_mode config <<<"$row"
  trace_root=$(awk -F '\t' -v workload="${workload,,}" '$1 == workload { print $2; exit }' \
    "$repo_root/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv")
  test -n "$trace_root" && test -r "$trace_root/kernelslist.g"
  test -r "$repo_root/configs/dtc_l1/fast64/$config"
  if [ -e "$runs_root/$name" ]; then
    test -f "$runs_root/$name/RUN_MANIFEST.tsv" || {
      echo "R2_EXISTING_NAMESPACE_WITHOUT_MANIFEST $name" >&2
      exit 1
    }
  else
    test ! -e "$runs_root/$name.launcher.log" || { echo "R2_ORPHAN_LAUNCHER_LOG $name" >&2; exit 1; }
    test ! -e "$runs_root/$name.supervisor.tsv" || { echo "R2_ORPHAN_SUPERVISOR $name" >&2; exit 1; }
    eligible_rows+=("$row")
  fi
done

selection=$(python3 "$cpu_selector" --proc-root "$proc_root" --format tsv)
candidate_line=$(printf '%s\n' "$selection" | awk -F '\t' '$1 == "candidate_cpus" { print $2; exit }')
candidate_core_count=$(printf '%s\n' "$selection" | awk -F '\t' '$1 == "available_distinct_physical_cores" { print $2; exit }')
test -n "$candidate_line" && [[ "$candidate_core_count" =~ ^[0-9]+$ ]]
IFS=',' read -r -a free_cpus <<<"$candidate_line"
free_cpu_list=$(IFS=,; echo "${free_cpus[*]:-none}")

if [ "$dispatch_mode" = dry-run ]; then
  printf 'R2_TOPOLOGY_AWARE_DISPATCH_DRY_RUN_PASS\ttotal_rows=%s\teligible_rows=%s\tavailable_distinct_physical_cores=%s\tcandidate_cpus=%s\trunner_sha256=%s\timmutable_runner=%s\tscientific_config_source=%s\n' \
    "${#rows[@]}" "${#eligible_rows[@]}" "$candidate_core_count" "$free_cpu_list" "$runner_sha" "$immutable_runner" "$scientific_config_source"
  exit 0
fi

# The audit binds the number of new R2 workers admitted *now*.  Existing old
# diagnostic jobs are deliberately not a scientific launch barrier.
test -r "$resource_audit" || { echo "R2_RESOURCE_AUDIT_UNAVAILABLE" >&2; exit 1; }
authorized_workers=$(awk -F '\t' '
  $1 == "schema" && $2 == "FAST64_R2_RESOURCE_AUDIT_V1" { schema=1 }
  $1 == "safe_to_launch" && $2 == "YES" { safe=1 }
  $1 == "authorized_workers" { workers=$2 }
  $1 == "memavailable_bytes" && $2 ~ /^[0-9]+$/ { mem=1 }
  $1 == "memory_current_bytes" && $2 ~ /^[0-9]+$/ { current=1 }
  $1 == "memory_max_bytes" && $2 ~ /^[0-9]+$/ { maximum=1 }
  $1 == "swap_si_delta" && $2 ~ /^[0-9]+$/ { si=1 }
  $1 == "swap_so_delta" && $2 ~ /^[0-9]+$/ { so=1 }
  $1 == "oom_kill_delta" && $2 ~ /^[0-9]+$/ { oom=1 }
  $1 == "p95_rss_bytes" && $2 ~ /^[0-9]+$/ { rss=1 }
  $1 == "iowait_pct" && $2 ~ /^[0-9.]+$/ { iowait=1 }
  $1 == "output_free_bytes" && $2 ~ /^[0-9]+$/ { output=1 }
  END { if (schema && safe && mem && current && maximum && si && so && oom && rss && iowait && output && workers ~ /^[1-7]$/) print workers; else exit 1 }
' "$resource_audit") || { echo "R2_RESOURCE_AUDIT_INCOMPLETE_OR_UNSAFE" >&2; exit 1; }
test "$authorized_workers" -le "${#eligible_rows[@]}" || {
  echo "R2_AUDIT_EXCEEDS_ELIGIBLE_ROWS authorized=$authorized_workers eligible=${#eligible_rows[@]}" >&2
  exit 1
}
test "$authorized_workers" -le "${#free_cpus[@]}" || {
  echo "R2_INSUFFICIENT_TOPOLOGY_CANDIDATES authorized=$authorized_workers available=${#free_cpus[@]} candidates=$free_cpu_list" >&2
  exit 1
}

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

exec 9>"$runs_root/.fast64_1_r2_full_wave_dispatch.lock"
flock -n 9 || { echo "R2_FULL_WAVE_DISPATCH_LOCK_HELD" >&2; exit 1; }
for row in "${eligible_rows[@]:0:authorized_workers}"; do
  IFS='|' read -r name _ <<<"$row"
  for target in "$runs_root/$name" "$runs_root/$name.launcher.log" "$runs_root/$name.supervisor.tsv"; do
    test ! -e "$target" || { echo "R2_TARGET_RACED $target" >&2; exit 1; }
  done
done
for index in "${!eligible_rows[@]}"; do
  [ "$index" -lt "$authorized_workers" ] || break
  row=${eligible_rows[$index]}
  cpu=${free_cpus[$index]}
  IFS='|' read -r name workload row_mode config <<<"$row"
  trace_root=$(awk -F '\t' -v workload="${workload,,}" '$1 == workload { print $2; exit }' \
    "$repo_root/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv")
  attempt_uuid=$(cat /proc/sys/kernel/random/uuid)
  # Do not let the dispatch lock FD survive in the detached supervisor or in
  # its simulator descendants.  The namespace mkdir remains the exactly-once
  # witness; closing this inherited descriptor only makes the short-lived
  # dispatch lock release when this launcher exits.
  (
    exec 9>&-
    exec setsid "$immutable_runner" --simulator "$runtime" \
      --config "$repo_root/configs/dtc_l1/fast64/$config" --trace "$trace_root/kernelslist.g" \
      --trace-config "$trace_config" --run-dir "$runs_root/$name" --cpu "$cpu" \
      --attempt-uuid "$attempt_uuid" --runner-sha256 "$runner_sha" \
      --immutable-runner-path "$immutable_runner" \
      --framework-scientific-config-source-sha "$scientific_config_source" \
      --core-source-head "$expected_core" --observer-overlay-sha "$observer_sha" \
      --result-classification FAST64_1_R2_FULL_WAVE_IMMUTABLE_RECOVERY
  ) >"$runs_root/$name.launcher.log" 2>&1 &
  supervisor=$!
  printf 'row\tsupervisor_pid\tcpu_slot\tattempt_uuid\trunner_sha256\timmutable_runner\tscientific_config_source\tcore_sha\truntime_sha256\n' >"$runs_root/$name.supervisor.tsv"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$supervisor" "$cpu" "$attempt_uuid" \
    "$runner_sha" "$immutable_runner" "$scientific_config_source" "$expected_core" "$expected_runtime" >>"$runs_root/$name.supervisor.tsv"
  echo "R2_FULL_WAVE_DISPATCHED row=$name cpu_slot=$cpu supervisor=$supervisor attempt_uuid=$attempt_uuid"
done
