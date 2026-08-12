#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_decoupled_l2_archive_batch.sh --archive SUITE.tgz --suite NAME
       --case-list CASES.txt [--config FILE] [--trace-config FILE]
       [--run-root DIR] [--scratch-root DIR] [--min-free-gib N] [--reuse]
       [--build]
       [--staged-traces DIR]
       [--jobs N] [--pair-parallel] [--trusted-size-plan]
       [--max-memory-percent N] [--pair-memory-reserve-gib N]
       [--host-memory-reserve-gib N] [--max-live-pairs N]
       [--discard-failed-extract]

Extract all selected traces in one archive pass, then run independent workload
pairs concurrently. --staged-traces names a persistent stage prepared by
prepare_decoupled_l2_archive_stage.sh; completed cases are reused there and
only missing cases are extracted. --jobs limits concurrent workload pairs (default 1).
--pair-parallel additionally runs each pair's baseline and decoupled backends
concurrently. CASES.txt contains one relative workload path per line, such as
the cases.txt written by plan_decoupled_l2_archive_cases.sh; its compatible
sizes.csv may also be used directly.
The exact selected trace size is checked before extraction. A failed batch
retains its trace payload and failures.csv by default.

--trusted-size-plan accepts the selected cases.csv/sizes.csv as the exact
member-size result from a just-completed planner run and skips the otherwise
redundant second full archive listing. It does not weaken the extraction's
path checks; use it only with the unchanged archive that the planner scanned.

MAX-MEMORY-PERCENT (default 95) is an admission ceiling. Each new workload
pair also reserves PAIR-MEMORY-RESERVE-GIB (default 160) against that ceiling.
The same pair reservation must fit in the host's MemAvailable after retaining
HOST-MEMORY-RESERVE-GIB (default 20), preventing a busy unrelated workload
from invalidating a cgroup-only admission decision.
MAX-LIVE-PAIRS (default 1) limits concurrent pairs independently, so a new
batch cannot fan out while each newly started simulator is still building its
trace state. These gates never interrupt a pair already in flight. Disk-space
reserve is separately controlled by MIN-FREE-GIB.
EOF
}

archive=""; suite=""; case_list=""; config=""; trace_config=""; config_given=0
run_root=""; scratch_root=""; min_free_gib=80; keep_failed_extract=1; reuse=0
build=0
staged_traces=""
jobs=1; pair_parallel=0
trusted_size_plan=0
max_memory_percent=95
pair_memory_reserve_gib=160
host_memory_reserve_gib=20
max_live_pairs=1
while [[ $# -gt 0 ]]; do
  case "$1" in
    --archive) archive="$2"; shift 2 ;;
    --suite) suite="$2"; shift 2 ;;
    --case-list) case_list="$2"; shift 2 ;;
    --config) config="$2"; config_given=1; shift 2 ;;
    --trace-config) trace_config="$2"; shift 2 ;;
    --run-root) run_root="$2"; shift 2 ;;
    --scratch-root) scratch_root="$2"; shift 2 ;;
    --staged-traces) staged_traces="$2"; shift 2 ;;
    --min-free-gib) min_free_gib="$2"; shift 2 ;;
    --jobs) jobs="$2"; shift 2 ;;
    --pair-parallel) pair_parallel=1; shift ;;
    --trusted-size-plan) trusted_size_plan=1; shift ;;
    --max-memory-percent) max_memory_percent="$2"; shift 2 ;;
    --pair-memory-reserve-gib) pair_memory_reserve_gib="$2"; shift 2 ;;
    --host-memory-reserve-gib) host_memory_reserve_gib="$2"; shift 2 ;;
    --max-live-pairs) max_live_pairs="$2"; shift 2 ;;
    --discard-failed-extract) keep_failed_extract=0; shift ;;
    --reuse) reuse=1; shift ;;
    --build) build=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -f "$archive" ]] || { echo "error: --archive must be a readable .tgz" >&2; exit 2; }
[[ -n "$suite" && -f "$case_list" ]] || { echo "error: --suite and --case-list are required" >&2; exit 2; }
[[ "$min_free_gib" =~ ^[0-9]+$ ]] || { echo "error: invalid --min-free-gib" >&2; exit 2; }
[[ "$jobs" =~ ^[0-9]+$ && "$jobs" -gt 0 ]] || { echo "error: --jobs must be positive" >&2; exit 2; }
[[ "$max_memory_percent" =~ ^[0-9]+$ && "$max_memory_percent" -gt 0 && "$max_memory_percent" -le 100 ]] || {
  echo "error: --max-memory-percent must be in 1..100" >&2; exit 2;
}
[[ "$pair_memory_reserve_gib" =~ ^[0-9]+$ && "$pair_memory_reserve_gib" -gt 0 ]] || {
  echo "error: --pair-memory-reserve-gib must be positive" >&2; exit 2;
}
[[ "$host_memory_reserve_gib" =~ ^[0-9]+$ ]] || {
  echo "error: --host-memory-reserve-gib must be non-negative" >&2; exit 2;
}
[[ "$max_live_pairs" =~ ^[0-9]+$ && "$max_live_pairs" -gt 0 ]] || {
  echo "error: --max-live-pairs must be positive" >&2; exit 2;
}
[[ -n "${DECOUPLED_L2_GPGPUSIM_ROOT:-}" ]] || { echo "error: set DECOUPLED_L2_GPGPUSIM_ROOT" >&2; exit 2; }

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ "$build" -eq 1 ]]; then
  make -C "$repo_root/gpu-simulator" -j"$(nproc)"
fi
sim_bin="$repo_root/gpu-simulator/bin/release/accel-sim.out"
[[ -x "$sim_bin" ]] || { echo "error: missing simulator binary $sim_bin" >&2; exit 2; }
sim_bin_sha256="$(sha256sum "$sim_bin" | awk '{print $1}')"
gpgpusim_source_commit="$(git -C "$DECOUPLED_L2_GPGPUSIM_ROOT" rev-parse HEAD)"
if [[ -z "$config" ]]; then
  config="$DECOUPLED_L2_GPGPUSIM_ROOT/configs/tested-cfgs/SM7_QV100/gpgpusim.config"
fi
[[ -f "$config" ]] || { echo "error: missing config $config" >&2; exit 2; }
if [[ -z "$trace_config" && "$config_given" -eq 0 ]]; then
  trace_config="$repo_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
fi
[[ -z "$trace_config" || -f "$trace_config" ]] || { echo "error: missing trace config" >&2; exit 2; }

if [[ -z "$run_root" ]]; then
  run_root="$repo_root/hw_run/decoupled-l2-runs/${suite}_batch_$(date +%Y%m%d_%H%M%S)"
fi
if [[ -z "$scratch_root" ]]; then scratch_root="$repo_root/hw_run/decoupled-l2-extract"; fi
mkdir -p "$run_root" "$scratch_root"
run_root="$(cd "$run_root" && pwd)"; scratch_root="$(cd "$scratch_root" && pwd)"
if [[ -z "$staged_traces" && -d "$scratch_root/$suite.stage/.decoupled_l2_stage_complete" ]]; then
  # The persistent default is intentionally discovered at execution time so a
  # capacity-waiting plan can reuse preparation that finishes in parallel.
  staged_traces="$scratch_root/$suite.stage"
fi
if [[ -n "$staged_traces" ]]; then
  mkdir -p "$staged_traces"
  staged_traces="$(cd "$staged_traces" && pwd)"
fi

selected="$run_root/${suite}_selected_cases.txt"
awk -F, 'NF && $1 != "case" { sub(/^\.\//, "", $1); print $1 }' "$case_list" | sort -u > "$selected"
[[ -s "$selected" ]] || { echo "error: case list has no paths" >&2; exit 2; }
while IFS= read -r case_path; do
  [[ "$case_path" != /* && "$case_path" != *".."* ]] || {
    echo "error: invalid relative case path $case_path" >&2; exit 2;
  }
done < "$selected"

tar_read() {
  if command -v pigz >/dev/null 2>&1; then tar --use-compress-program=pigz "$@"
  else tar --gzip "$@"; fi
}
available_kib() { df -Pk "$scratch_root" | awk 'NR == 2 { print $4 }'; }
cgroup_memory_bytes() { cat /sys/fs/cgroup/memory.current; }
cgroup_memory_limit_bytes() {
  local limit
  limit="$(cat /sys/fs/cgroup/memory.max)"
  [[ "$limit" =~ ^[0-9]+$ && "$limit" -gt 0 ]] && printf '%s\n' "$limit" || printf '0\n'
}
cgroup_oom_kill_count() {
  awk '$1 == "oom_kill" { print $2; found = 1 } END { if (!found) print 0 }' \
    /sys/fs/cgroup/memory.events
}
host_memory_available_bytes() {
  awk '/^MemAvailable:/ { print $2 * 1024; found = 1 } END { if (!found) print 0 }' /proc/meminfo
}
pair_memory_admit() {
  local used limit ceiling reserve host_available host_reserve
  used="$(cgroup_memory_bytes)"
  limit="$(cgroup_memory_limit_bytes)"
  reserve=$((pair_memory_reserve_gib * 1024 * 1024 * 1024))
  host_available="$(host_memory_available_bytes)"
  host_reserve=$((host_memory_reserve_gib * 1024 * 1024 * 1024))
  if (( limit != 0 )); then
    ceiling=$((limit * max_memory_percent / 100))
    (( used + reserve <= ceiling )) || return 1
  fi
  (( host_available >= reserve + host_reserve ))
}
min_free_kib=$((min_free_gib * 1024 * 1024))

# A single verbose member list provides both the exact capacity gate and proof
# that every selected item is a complete workload trace directory.
selected_sizes="$run_root/${suite}_selected_sizes.csv"
if [[ "$trusted_size_plan" -eq 1 ]]; then
  awk -F, -v selected="$selected" '
    BEGIN { while ((getline x < selected) > 0) want[x] = 1; close(selected) }
    $1 != "case" && want[$1] { bytes[$1] = $2; found[$1] = 1 }
    END {
      for (work in want) {
        if (!found[work] || bytes[work] !~ /^[0-9]+$/) {
          printf "missing exact byte count in trusted plan: %s\n", work > "/dev/stderr"; bad = 1
        } else printf "%s,%s\n", work, bytes[work]
      }
      exit bad
    }
  ' "$case_list" | sort > "$selected_sizes"
else
  tar_read --list --verbose --file "$archive" | awk -v selected="$selected" '
    BEGIN { while ((getline x < selected) > 0) want[x] = 1; close(selected) }
    $6 ~ /\/traces\// {
      path = $6; sub(/^\.\//, "", path); split(path, part, "/traces/")
      work = part[1]
      if (want[work]) {
        bytes[work] += $3
        if (path ~ /\/traces\/kernelslist\.g$/) kernels[work] = 1
      }
    }
    END {
      for (work in want) {
        if (!kernels[work]) { printf "missing kernelslist.g: %s\n", work > "/dev/stderr"; bad = 1 }
        else printf "%s,%d\n", work, bytes[work]
      }
      exit bad
    }
  ' | sort > "$selected_sizes"
fi
trace_kib="$(awk -F, '{ bytes += $2 } END { print int((bytes + 1023) / 1024) }' "$selected_sizes")"
[[ "$trace_kib" =~ ^[0-9]+$ && "$trace_kib" -gt 0 ]] || { echo "error: cannot size selected traces" >&2; exit 1; }
missing="$run_root/${suite}_missing_cases.txt"
: > "$missing"
while IFS=, read -r case_path case_bytes; do
  [[ -n "$case_path" ]] || continue
  marker="${staged_traces:-/nonexistent}/.decoupled_l2_stage_complete/${case_path//\//__}"
  if [[ -z "$staged_traces" || ! -f "$marker" ||
        ! -f "$staged_traces/$case_path/traces/kernelslist.g" ]]; then
    printf '%s\n' "$case_path" >> "$missing"
  fi
done < "$selected_sizes"
missing_kib="$(awk -F, -v missing="$missing" '
  BEGIN { while ((getline x < missing) > 0) want[x] = 1; close(missing) }
  want[$1] { bytes += $2 } END { print int((bytes + 1023) / 1024) }
' "$selected_sizes")"
available="$(available_kib)"
if (( available < min_free_kib + missing_kib )); then
  printf 'error: batch needs %d GiB additional traces plus %d GiB reserve; only %d GiB free\n' \
    "$(((missing_kib + 1024 * 1024 - 1) / 1024 / 1024))" "$min_free_gib" \
    "$((available / 1024 / 1024))" >&2
  exit 1
fi

patterns="$run_root/${suite}_trace_patterns.txt"
awk '{ printf "./%s/traces/*\n", $0 }' "$missing" > "$patterns"
summary="$run_root/summary.csv"; failures="$run_root/failures.csv"
printf 'suite,case,backend,cycles,run_dir\n' > "$summary"
printf 'time,suite,case,backend,stage,run_dir,trace_dir,smoke_out\n' > "$failures"
batch_dir=""; owns_batch=1; current_case=""; current_backend=""; current_stage="setup"; current_run_dir=""
cleanup_batch() { [[ "$owns_batch" -eq 1 && -n "$batch_dir" && "$batch_dir" == "$scratch_root"/* ]] && rm -rf "$batch_dir"; }
finish() {
  status="$?"
  if (( status != 0 )); then
    printf '%s,%s,%s,%s,%s,%s,%s,%s\n' "$(date --iso-8601=seconds)" \
      "$suite" "$current_case" "$current_backend" "$current_stage" \
      "$current_run_dir" "$batch_dir" "$current_run_dir/smoke.out" >> "$failures"
    if (( keep_failed_extract )) && [[ -n "$batch_dir" ]]; then
      printf 'FAIL preserved traces=%s log=%s manifest=%s\n' "$batch_dir" "$current_run_dir/smoke.out" "$failures" >&2
      batch_dir=""
    else
      cleanup_batch
    fi
  else
    cleanup_batch
  fi
}
trap finish EXIT

if [[ -n "$staged_traces" ]]; then
  batch_dir="$staged_traces"
  owns_batch=0
else
  batch_dir="$(mktemp -d "$scratch_root/${suite}.batch.XXXXXX")"
fi
current_stage="extract"
# GNU tar's --directory is positional: it must precede --files-from so the
# names read from that file are extracted below the staging directory.
if [[ -s "$missing" ]]; then
  tar_read --extract --wildcards --directory "$batch_dir" --files-from="$patterns" --file "$archive"
  if [[ "$owns_batch" -eq 0 ]]; then
    marker_dir="$batch_dir/.decoupled_l2_stage_complete"
    mkdir -p "$marker_dir"
    while IFS= read -r case_path; do
      [[ -f "$batch_dir/$case_path/traces/kernelslist.g" ]] || {
        echo "error: staged extraction lost $case_path" >&2; exit 1;
      }
      : > "$marker_dir/${case_path//\//__}"
    done < "$missing"
  fi
fi

run_backend() {
  local case_path="$1" backend="$2" trace="$3" case_run_dir cycles
  case_run_dir="$run_root/$suite/$case_path/$backend"
  smoke_args=(--backend "$backend" --trace "$trace" --config "$config" --run-dir "$case_run_dir")
  [[ -n "$trace_config" ]] && smoke_args+=(--trace-config "$trace_config")
  if [[ ( "$reuse" -eq 1 || "$owns_batch" -eq 0 ) ]] && run_is_reusable "$case_run_dir"; then
    printf 'REUSE backend=%s run_dir=%s\n' "$backend" "$case_run_dir"
  elif ! "$repo_root/scripts/run_decoupled_l2_smoke.sh" "${smoke_args[@]}"; then
    printf '%s,%s,%s,simulate,%s,%s,%s\n' "$(date --iso-8601=seconds)" \
      "$suite" "$case_path" "$case_run_dir" "$batch_dir" "$case_run_dir/smoke.out" >> "$failures"
    return 1
  fi
  if [[ "$backend" == decoupled ]] && ! rg -q 'decoupled_l2\[.*access=[1-9]' "$case_run_dir/smoke.out"; then
    printf '%s,%s,%s,counter_gate,%s,%s,%s\n' "$(date --iso-8601=seconds)" \
      "$suite" "$case_path" "$case_run_dir" "$batch_dir" "$case_run_dir/smoke.out" >> "$failures"
    return 1
  fi
  cycles="$(sed -n 's/.*gpu_tot_sim_cycle = \([0-9][0-9]*\).*/\1/p' "$case_run_dir/smoke.out" | tail -1)"
  [[ -n "$cycles" ]] || return 1
  printf '%s,%s,%s,%s,%s\n' "$suite" "$case_path" "$backend" "$cycles" "$case_run_dir" >> "$summary"
}

run_is_reusable() {
  local case_run_dir="$1" provenance recorded_sha recorded_commit
  [[ -f "$case_run_dir/smoke.out" ]] || return 1
  rg -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$case_run_dir/smoke.out" || return 1
  provenance="$case_run_dir/simulator_provenance.txt"
  [[ -f "$provenance" ]] || return 1
  recorded_sha="$(sed -n 's/^sim_bin_sha256=//p' "$provenance" | tail -1)"
  recorded_commit="$(sed -n 's/^gpgpusim_source_commit=//p' "$provenance" | tail -1)"
  [[ "$recorded_sha" == "$sim_bin_sha256" &&
     "$recorded_commit" == "$gpgpusim_source_commit" ]]
}

run_case() {
  local case_path="$1" trace baseline_status decoupled_status
  trace="$batch_dir/$case_path/traces/kernelslist.g"
  [[ -f "$trace" ]] || { echo "error: extraction lost $case_path" >&2; return 1; }
  if [[ "$pair_parallel" -eq 1 ]]; then
    run_backend "$case_path" baseline "$trace" & baseline_pid="$!"
    run_backend "$case_path" decoupled "$trace" & decoupled_pid="$!"
    if wait "$baseline_pid"; then baseline_status=0; else baseline_status=1; fi
    if wait "$decoupled_pid"; then decoupled_status=0; else decoupled_status=1; fi
    (( baseline_status == 0 && decoupled_status == 0 ))
  else
    run_backend "$case_path" baseline "$trace" && run_backend "$case_path" decoupled "$trace"
  fi
}

case_count=0; active=0; failed=0
oom_kill_start="$(cgroup_oom_kill_count)"
while IFS= read -r case_path; do
  case_count=$((case_count + 1))
  while (( active >= jobs || active >= max_live_pairs )); do
    if ! wait -n; then failed=1; fi
    active=$((active - 1))
  done
  if (( $(cgroup_oom_kill_count) > oom_kill_start )); then
    printf 'error: cgroup OOM kill detected during batch; retain logs and do not start further cases\n' >&2
    failed=1
    break
  fi
  while ! pair_memory_admit; do
    if (( $(cgroup_oom_kill_count) > oom_kill_start )); then
      printf 'error: cgroup OOM kill detected during batch; retain logs and do not start further cases\n' >&2
      failed=1
      break 2
    fi
    printf 'WAIT_MEMORY used_gib=%s host_available_gib=%s pair_reserve_gib=%s host_reserve_gib=%s limit_percent=%s active_pairs=%s\n' \
      "$(( $(cgroup_memory_bytes) / 1024 / 1024 / 1024 ))" \
      "$(( $(host_memory_available_bytes) / 1024 / 1024 / 1024 ))" \
      "$pair_memory_reserve_gib" "$host_memory_reserve_gib" \
      "$max_memory_percent" "$active" >&2
    sleep 30
  done
  run_case "$case_path" &
  active=$((active + 1))
done < "$selected"
while (( active > 0 )); do
  if ! wait -n; then failed=1; fi
  active=$((active - 1))
done
(( failed == 0 )) || { echo "error: one or more workload pairs failed; see $failures" >&2; exit 1; }

current_stage="cleanup"
(( $(available_kib) >= min_free_kib )) || { echo "error: post-run reserve violated" >&2; exit 1; }
printf 'PASS cases=%s trace_gib=%.3f summary=%s\n' "$case_count" \
  "$(awk -v kib="$trace_kib" 'BEGIN { print kib / 1024 / 1024 }')" "$summary"
