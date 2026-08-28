#!/usr/bin/env bash
# Run baseline-only replays and retain /usr/bin/time peak RSS through the
# normal run_decoupled_l2_smoke.sh resource recorder.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_decoupled_l2_rss_profile_queue.sh --manifest FILE
       [--run-root DIR] [--config FILE] [--trace-config FILE]
       [--jobs N] [--min-available-gib N] [--poll-sec N]
       [--reuse-completed]
       [--global-admission-lock PATH]

MANIFEST is tab-separated: logical-name<TAB>/absolute/path/to/kernelslist.g.
Every entry runs the current baseline backend exactly once.  The queue admits
only when MemAvailable meets the configured floor, then calls the normal smoke
runner so resource_usage.txt, runtime_metrics.txt and provenance are retained.
EOF
}

manifest=""
run_root=""
config=""
trace_config=""
jobs=1
min_available_gib=96
poll_sec=60
global_lock="${TMPDIR:-/tmp}/decoupled-l2-archive-pair.lock"
reuse_completed=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --manifest) manifest="$2"; shift 2 ;;
    --run-root) run_root="$2"; shift 2 ;;
    --config) config="$2"; shift 2 ;;
    --trace-config) trace_config="$2"; shift 2 ;;
    --jobs) jobs="$2"; shift 2 ;;
    --min-available-gib) min_available_gib="$2"; shift 2 ;;
    --poll-sec) poll_sec="$2"; shift 2 ;;
    --reuse-completed) reuse_completed=1; shift ;;
    --global-admission-lock) global_lock="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -f "$manifest" ]] || { echo "error: --manifest is required" >&2; exit 2; }
[[ "$jobs" =~ ^[0-9]+$ && "$jobs" -gt 0 ]] || { echo "error: invalid --jobs" >&2; exit 2; }
[[ "$min_available_gib" =~ ^[0-9]+$ && "$min_available_gib" -gt 0 ]] || {
  echo "error: invalid --min-available-gib" >&2; exit 2;
}
[[ "$poll_sec" =~ ^[0-9]+$ && "$poll_sec" -gt 0 ]] || { echo "error: invalid --poll-sec" >&2; exit 2; }
command -v flock >/dev/null 2>&1 || { echo "error: flock is required" >&2; exit 2; }

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
set +u
# shellcheck disable=SC1090
source "$repo_root/scripts/setup_decoupled_l2_env.sh" release
set -u
if [[ -z "$config" ]]; then
  config="$DECOUPLED_L2_GPGPUSIM_ROOT/configs/tested-cfgs/SM7_QV100/gpgpusim.config"
fi
if [[ -z "$trace_config" ]]; then
  trace_config="$repo_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
fi
[[ -f "$config" && -f "$trace_config" ]] || { echo "error: missing simulator config" >&2; exit 2; }

if [[ -z "$run_root" ]]; then
  run_root="$repo_root/hw_run/decoupled-l2-rss-profile-$(date +%Y%m%d_%H%M%S)"
fi
mkdir -p "$run_root"
run_root="$(cd "$run_root" && pwd)"
summary="$run_root/summary.tsv"
if [[ "$reuse_completed" -eq 0 || ! -s "$summary" ]]; then
  printf 'name\tstate\tpeak_rss_kib\trun_dir\ttrace\n' > "$summary"
fi

available_kib() { awk '/^MemAvailable:/ { print $2; exit }' /proc/meminfo; }
min_available_kib=$((min_available_gib * 1024 * 1024))

run_completed() {
  local run_dir="$1"
  [[ -f "$run_dir/resource_usage.txt" &&
     -f "$run_dir/smoke.out" &&
     -f "$run_dir/runtime_metrics.txt" ]] || return 1
  [[ "$(sed -n 's/^sim_exit_status=//p' "$run_dir/runtime_metrics.txt" | tail -1)" == 0 ]] || return 1
  rg -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$run_dir/smoke.out"
}

summary_has_name() {
  local name="$1"
  awk -F '\t' -v name="$name" 'NR > 1 && $1 == name { found = 1 } END { exit !found }' "$summary"
}

admit_one() {
  local name="$1" trace="$2" lock_fd
  while :; do
    if (( $(available_kib) < min_available_kib )); then
      printf 'WAIT_MEM name=%s available_gib=%s floor_gib=%s\n' "$name" \
        "$(awk -v kib="$(available_kib)" 'BEGIN { printf "%.1f", kib / 1024 / 1024 }')" \
        "$min_available_gib" >&2
      sleep "$poll_sec"
      continue
    fi
    exec {lock_fd}>"$global_lock"
    flock "$lock_fd"
    if (( $(available_kib) >= min_available_kib )); then
      flock -u "$lock_fd"
      exec {lock_fd}>&-
      return
    fi
    flock -u "$lock_fd"
    exec {lock_fd}>&-
  done
}

run_one() {
  local name="$1" trace="$2" slug run_dir peak_kib
  [[ -f "$trace" ]] || {
    printf '%s\tMISSING_TRACE\t\t\t%s\n' "$name" "$trace" >> "$summary"
    return 1
  }
  slug="$(printf '%s' "$name" | tr '/ :,' '____')"
  run_dir="$run_root/$slug/baseline"
  if [[ "$reuse_completed" -eq 1 ]] && run_completed "$run_dir"; then
    if ! summary_has_name "$name"; then
      peak_kib="$(sed -n 's/^\tMaximum resident set size (kbytes): \([0-9][0-9]*\)$/\1/p' \
        "$run_dir/resource_usage.txt" | tail -1)"
      printf '%s\tREUSE\t%s\t%s\t%s\n' "$name" "${peak_kib:--}" "$run_dir" "$trace" >> "$summary"
    fi
    return
  fi
  admit_one "$name" "$trace"
  printf 'START name=%s trace=%s run_dir=%s\n' "$name" "$trace" "$run_dir"
  if "$repo_root/scripts/run_decoupled_l2_smoke.sh" --backend baseline --trace "$trace" \
      --config "$config" --trace-config "$trace_config" --run-dir "$run_dir"; then
    peak_kib="$(sed -n 's/^\tMaximum resident set size (kbytes): \([0-9][0-9]*\)$/\1/p' \
      "$run_dir/resource_usage.txt" | tail -1)"
    printf '%s\tPASS\t%s\t%s\t%s\n' "$name" "${peak_kib:--}" "$run_dir" "$trace" >> "$summary"
    printf 'PASS name=%s peak_rss_kib=%s\n' "$name" "${peak_kib:--}"
  else
    printf '%s\tFAIL\t\t%s\t%s\n' "$name" "$run_dir" "$trace" >> "$summary"
    return 1
  fi
}

active=0
failed=0
while IFS=$'\t' read -r name trace; do
  [[ -n "${name:-}" && "${name:0:1}" != "#" ]] || continue
  [[ -n "${trace:-}" ]] || { echo "error: malformed manifest entry for $name" >&2; exit 2; }
  while (( active >= jobs )); do
    if ! wait -n; then failed=1; fi
    active=$((active - 1))
  done
  run_one "$name" "$trace" &
  active=$((active + 1))
done < "$manifest"
while (( active > 0 )); do
  if ! wait -n; then failed=1; fi
  active=$((active - 1))
done

(( failed == 0 )) || { echo "error: one or more RSS profiles failed; see $summary" >&2; exit 1; }
printf 'PASS summary=%s\n' "$summary"
