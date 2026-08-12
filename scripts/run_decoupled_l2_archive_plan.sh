#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_decoupled_l2_archive_plan.sh --archive SUITE.tgz --suite NAME
       [--plan-dir DIR] [--run-root DIR] [--min-free-gib N]
       [--max-parallel N] [--jobs N] [--pair-parallel]
       [--max-memory-percent N] [--staged-traces DIR]
       [--wait-for-plan-pid PID]

Create (or wait for) an exact tar-member capacity plan, then run each planned
wave through run_decoupled_l2_archive_batch.sh.  The pipeline stores status,
per-wave logs, summaries, and failures under RUN-ROOT.  A successful wave
deletes its temporary traces; a failed wave preserves them for replay.

WAIT-FOR-PLAN-PID allows this script to attach to an already-running planner
instead of starting a redundant second full gzip scan.  The given process must
write PLAN-DIR/sizes.csv and PLAN-DIR/schedule.csv before it exits.
EOF
}

archive=""; suite=""; plan_dir=""; run_root=""; min_free_gib=80
max_parallel=16; jobs=16; pair_parallel=0; wait_for_plan_pid=""
max_memory_percent=95
staged_traces=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --archive) archive="$2"; shift 2 ;;
    --suite) suite="$2"; shift 2 ;;
    --plan-dir) plan_dir="$2"; shift 2 ;;
    --run-root) run_root="$2"; shift 2 ;;
    --min-free-gib) min_free_gib="$2"; shift 2 ;;
    --max-parallel) max_parallel="$2"; shift 2 ;;
    --jobs) jobs="$2"; shift 2 ;;
    --pair-parallel) pair_parallel=1; shift ;;
    --max-memory-percent) max_memory_percent="$2"; shift 2 ;;
    --staged-traces) staged_traces="$2"; shift 2 ;;
    --wait-for-plan-pid) wait_for_plan_pid="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -f "$archive" ]] || { echo "error: --archive must be readable" >&2; exit 2; }
[[ -n "$suite" ]] || { echo "error: --suite is required" >&2; exit 2; }
[[ -n "${DECOUPLED_L2_GPGPUSIM_ROOT:-}" ]] || {
  echo "error: set DECOUPLED_L2_GPGPUSIM_ROOT" >&2; exit 2;
}
[[ -d "$DECOUPLED_L2_GPGPUSIM_ROOT" ]] || {
  echo "error: missing GPGPU-Sim root $DECOUPLED_L2_GPGPUSIM_ROOT" >&2; exit 2;
}
for value in "$min_free_gib" "$max_parallel" "$jobs" "$max_memory_percent"; do
  [[ "$value" =~ ^[0-9]+$ && "$value" -gt 0 ]] || {
    echo "error: numeric limits must be positive" >&2; exit 2;
  }
done
if [[ -n "$wait_for_plan_pid" ]]; then
  [[ "$wait_for_plan_pid" =~ ^[0-9]+$ ]] || { echo "error: invalid planner PID" >&2; exit 2; }
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "$plan_dir" ]]; then plan_dir="$repo_root/hw_run/decoupled-l2-plans/$suite"; fi
if [[ -z "$run_root" ]]; then run_root="$repo_root/hw_run/decoupled-l2-archive-plan/$suite"; fi
mkdir -p "$plan_dir" "$run_root"
plan_dir="$(cd "$plan_dir" && pwd)"; run_root="$(cd "$run_root" && pwd)"
if [[ -n "$staged_traces" ]]; then mkdir -p "$staged_traces"; staged_traces="$(cd "$staged_traces" && pwd)"; fi
status="$run_root/pipeline.status"
status_log="$run_root/pipeline.log"
failure="$run_root/pipeline.failure"
set_status() {
  printf 'time=%s\nstage=%s\nwave=%s\n' "$(date --iso-8601=seconds)" "$1" "${2:-0}" > "$status"
  printf '%s stage=%s wave=%s\n' "$(date --iso-8601=seconds)" "$1" "${2:-0}" >> "$status_log"
}
fail() {
  local failed_wave="${1:-0}" command="${2:-unknown}" exit_status="${3:-1}"
  trap - ERR
  {
    printf 'time=%s\n' "$(date --iso-8601=seconds)"
    printf 'stage=FAILED\nwave=%s\nstatus=%s\ncommand=%q\n' \
      "$failed_wave" "$exit_status" "$command"
  } > "$failure"
  set_status FAILED "$failed_wave"
  exit "$exit_status"
}
trap 'exit_status=$?; fail "${wave:-0}" "$BASH_COMMAND" "$exit_status"' ERR

if [[ -n "$wait_for_plan_pid" ]]; then
  set_status WAIT_PLAN 0
  while kill -0 "$wait_for_plan_pid" 2>/dev/null; do sleep 30; done
fi
if [[ ! -s "$plan_dir/sizes.csv" || ! -s "$plan_dir/schedule.csv" ]]; then
  set_status PLAN 0
  "$repo_root/scripts/plan_decoupled_l2_archive_cases.sh" \
    --archive "$archive" --min-free-gib "$min_free_gib" \
    --max-parallel "$max_parallel" --output-dir "$plan_dir"
fi
[[ -s "$plan_dir/sizes.csv" && -s "$plan_dir/schedule.csv" ]] || {
  echo "error: planner did not produce sizes.csv and schedule.csv" >&2; exit 1;
}

printf 'suite,wave,case,backend,cycles,run_dir\n' > "$run_root/summary.csv"
printf 'wave,manifest,summary,failures\n' > "$run_root/waves.csv"
wave_count="$(awk -F, 'NR > 1 && $1 > max { max = $1 } END { print max + 0 }' "$plan_dir/schedule.csv")"
(( wave_count > 0 )) || { echo "error: plan has no waves" >&2; exit 1; }
min_free_kib=$((min_free_gib * 1024 * 1024))
available_kib() { df -Pk "$run_root" | awk 'NR == 2 { print $4 }'; }

for ((wave = 1; wave <= wave_count; ++wave)); do
  set_status RUN "$wave"
  wave_dir="$run_root/wave_${wave}"
  mkdir -p "$wave_dir"
  wave_sizes="$wave_dir/sizes.csv"
  awk -F, -v wave="$wave" '
    BEGIN { print "case,trace_bytes" }
    NR > 1 && $1 == wave { print $2 "," $3 }
  ' "$plan_dir/schedule.csv" > "$wave_sizes"
  [[ "$(wc -l < "$wave_sizes")" -gt 1 ]] || {
    echo "error: wave $wave has no workload" >&2; exit 1;
  }
  wave_kib="$(awk -F, 'NR > 1 { bytes += $2 } END { print int((bytes + 1023) / 1024) }' "$wave_sizes")"
  [[ "$wave_kib" =~ ^[0-9]+$ && "$wave_kib" -gt 0 ]] || {
    echo "error: cannot size wave $wave" >&2; exit 1;
  }
  # A plan may have been made before another suite claimed temporary staging
  # space. Wait rather than fail the whole plan or violate the free-space
  # reserve; a successful earlier wave always releases its own staging tree.
  staged_kib=0
  if [[ -n "$staged_traces" ]]; then
    staged_kib="$(awk -F, -v stage="$staged_traces" '
      NR > 1 { name = $1; gsub("/", "__", name); marker = stage "/.decoupled_l2_stage_complete/" name; cmd = "test -f \"" marker "\""; if (system(cmd) == 0) bytes += $2 }
      END { print int((bytes + 1023) / 1024) }
    ' "$wave_sizes")"
  fi
  need_kib=$((wave_kib - staged_kib))
  while (( $(available_kib) < min_free_kib + need_kib )); do
    set_status WAIT_CAPACITY "$wave"
    sleep 30
  done
  batch_args=(--archive "$archive" --suite "$suite" --case-list "$wave_sizes"
              --trusted-size-plan --min-free-gib "$min_free_gib"
              --jobs "$jobs" --max-memory-percent "$max_memory_percent"
              --run-root "$wave_dir")
  [[ "$pair_parallel" -eq 1 ]] && batch_args+=(--pair-parallel)
  [[ -n "$staged_traces" ]] && batch_args+=(--staged-traces "$staged_traces")
  "$repo_root/scripts/run_decoupled_l2_archive_batch.sh" "${batch_args[@]}" \
    > "$wave_dir/pipeline.out" 2>&1
  awk -F, -v wave="$wave" 'NR > 1 { print $1 "," wave "," $2 "," $3 "," $4 "," $5 }' \
    "$wave_dir/summary.csv" >> "$run_root/summary.csv"
  printf '%s,%s,%s,%s\n' "$wave" "$wave_sizes" "$wave_dir/summary.csv" \
    "$wave_dir/failures.csv" >> "$run_root/waves.csv"
done

set_status DONE "$wave_count"
printf 'PASS suite=%s waves=%s summary=%s\n' "$suite" "$wave_count" "$run_root/summary.csv"
