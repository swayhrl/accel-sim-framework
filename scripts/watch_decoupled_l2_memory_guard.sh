#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/watch_decoupled_l2_memory_guard.sh --pid PID [--pid PID ...]
       [--interval-sec N] [--log FILE]

Watch cgroup memory.events for a new OOM kill. On each new event, send SIGSTOP
to the largest-resident listed simulator still running and record it in LOG.
SIGSTOP preserves simulator state for a later `kill -CONT PID`; it deliberately
does not claim to reclaim its already allocated memory. This is a last-resort
growth brake for live archive runs, not an admission controller.
EOF
}

interval_sec=5
log=""
declare -a candidates=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --pid) candidates+=("$2"); shift 2 ;;
    --interval-sec) interval_sec="$2"; shift 2 ;;
    --log) log="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ "${#candidates[@]}" -gt 0 ]] || { echo "error: at least one --pid is required" >&2; exit 2; }
[[ "$interval_sec" =~ ^[0-9]+$ && "$interval_sec" -gt 0 ]] || {
  echo "error: --interval-sec must be positive" >&2; exit 2;
}
if [[ -z "$log" ]]; then log="memory_guard.$(date +%Y%m%d_%H%M%S).log"; fi
mkdir -p "$(dirname "$log")"

oom_kill_count() {
  awk '$1 == "oom_kill" { print $2; found = 1 } END { if (!found) print 0 }' \
    /sys/fs/cgroup/memory.events
}
largest_running_pid() {
  local pid rss state best_pid="" best_rss=-1
  for pid in "${candidates[@]}"; do
    [[ -r "/proc/$pid/status" ]] || continue
    state="$(awk '/^State:/ {print $2; exit}' "/proc/$pid/status")"
    [[ "$state" != T && "$state" != t ]] || continue
    rss="$(awk '/^VmRSS:/ {print $2; exit}' "/proc/$pid/status")"
    rss="${rss:-0}"
    if (( rss > best_rss )); then best_rss="$rss"; best_pid="$pid"; fi
  done
  [[ -n "$best_pid" ]] && printf '%s %s\n' "$best_pid" "$best_rss"
}

last_oom="$(oom_kill_count)"
printf '%s START oom_kill=%s candidates=%s\n' "$(date --iso-8601=seconds)" \
  "$last_oom" "${candidates[*]}" >> "$log"
while :; do
  sleep "$interval_sec"
  now_oom="$(oom_kill_count)"
  (( now_oom > last_oom )) || continue
  selection="$(largest_running_pid || true)"
  if [[ -z "$selection" ]]; then
    printf '%s OOM oom_kill=%s action=none reason=no_live_candidate\n' \
      "$(date --iso-8601=seconds)" "$now_oom" >> "$log"
  else
    read -r pid rss <<< "$selection"
    kill -STOP "$pid"
    printf '%s OOM oom_kill=%s action=SIGSTOP pid=%s rss_kib=%s resume="kill -CONT %s"\n' \
      "$(date --iso-8601=seconds)" "$now_oom" "$pid" "$rss" "$pid" >> "$log"
  fi
  last_oom="$now_oom"
done
