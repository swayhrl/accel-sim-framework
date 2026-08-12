#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_decoupled_l2_archive_plan.sh --archive SUITE.tgz --suite NAME
       [--plan-dir DIR] [--run-root DIR] [--min-free-gib N]
       [--max-parallel N] [--jobs N] [--pair-parallel]
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
    --wait-for-plan-pid) wait_for_plan_pid="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -f "$archive" ]] || { echo "error: --archive must be readable" >&2; exit 2; }
[[ -n "$suite" ]] || { echo "error: --suite is required" >&2; exit 2; }
for value in "$min_free_gib" "$max_parallel" "$jobs"; do
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
status="$run_root/pipeline.status"
status_log="$run_root/pipeline.log"
set_status() {
  printf 'time=%s\nstage=%s\nwave=%s\n' "$(date --iso-8601=seconds)" "$1" "${2:-0}" > "$status"
  printf '%s stage=%s wave=%s\n' "$(date --iso-8601=seconds)" "$1" "${2:-0}" >> "$status_log"
}
fail() {
  set_status FAILED "${1:-0}"
  exit 1
}
trap 'fail "${wave:-0}"' ERR

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
  batch_args=(--archive "$archive" --suite "$suite" --case-list "$wave_sizes"
              --trusted-size-plan --min-free-gib "$min_free_gib"
              --jobs "$jobs" --run-root "$wave_dir")
  [[ "$pair_parallel" -eq 1 ]] && batch_args+=(--pair-parallel)
  "$repo_root/scripts/run_decoupled_l2_archive_batch.sh" "${batch_args[@]}" \
    > "$wave_dir/pipeline.out" 2>&1
  awk -F, -v wave="$wave" 'NR > 1 { print $1 "," wave "," $2 "," $3 "," $4 "," $5 }' \
    "$wave_dir/summary.csv" >> "$run_root/summary.csv"
  printf '%s,%s,%s,%s\n' "$wave" "$wave_sizes" "$wave_dir/summary.csv" \
    "$wave_dir/failures.csv" >> "$run_root/waves.csv"
done

set_status DONE "$wave_count"
printf 'PASS suite=%s waves=%s summary=%s\n' "$suite" "$wave_count" "$run_root/summary.csv"
