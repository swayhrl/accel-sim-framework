#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/watch_decoupled_l2_memory_guard.sh (--pid PID [--pid PID ...] | --auto)
       [--interval-sec N] [--max-memory-percent N]
       [--memory-limit-cooldown-sec N] [--action stop|terminate-pair] [--log FILE]

Watch cgroup memory.events for a new OOM kill. Optionally, stop before an OOM
when host memory consumption reaches MAX-MEMORY-PERCENT of MemTotal. On either
event, send SIGSTOP to the largest-resident listed simulator still running and
record it in LOG. SIGSTOP preserves simulator state for a later `kill -CONT
PID`; it deliberately does not claim to reclaim its already allocated memory.
This is a last-resort growth brake for live archive runs, not an admission
controller.

With `--action terminate-pair`, terminate both backends of the selected
workload instead.  This is for a hard memory ceiling: stopping a process keeps
its RSS resident, while terminating the pair releases it and preserves both
run directories for diagnosis and replay.  The default `stop` retains the
historical behaviour.

MEMORY-LIMIT-COOLDOWN-SEC (default 30) is the minimum time before a sustained
threshold breach can stop another simulator. This matters because SIGSTOP
preserves state but does not immediately return RSS to the host.

--auto discovers the current Accel-Sim release executable on every OOM event.
Use it for a long archive campaign whose workload PIDs change between waves.
EOF
}

interval_sec=5
max_memory_percent=100
memory_limit_cooldown_sec=30
action=stop
log=""
auto=0
declare -a candidates=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --pid) candidates+=("$2"); shift 2 ;;
    --auto) auto=1; shift ;;
    --interval-sec) interval_sec="$2"; shift 2 ;;
    --max-memory-percent) max_memory_percent="$2"; shift 2 ;;
    --memory-limit-cooldown-sec) memory_limit_cooldown_sec="$2"; shift 2 ;;
    --action) action="$2"; shift 2 ;;
    --log) log="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done
(( auto || ${#candidates[@]} > 0 )) || {
  echo "error: provide --auto or at least one --pid" >&2; exit 2;
}
[[ "$interval_sec" =~ ^[0-9]+$ && "$interval_sec" -gt 0 ]] || {
  echo "error: --interval-sec must be positive" >&2; exit 2;
}
[[ "$max_memory_percent" =~ ^[0-9]+$ && "$max_memory_percent" -gt 0 &&
   "$max_memory_percent" -le 100 ]] || {
  echo "error: --max-memory-percent must be in 1..100" >&2; exit 2;
}
[[ "$memory_limit_cooldown_sec" =~ ^[0-9]+$ ]] || {
  echo "error: --memory-limit-cooldown-sec must be non-negative" >&2; exit 2;
}
[[ "$action" == stop || "$action" == terminate-pair ]] || {
  echo "error: --action must be stop or terminate-pair" >&2; exit 2;
}
if [[ -z "$log" ]]; then log="memory_guard.$(date +%Y%m%d_%H%M%S).log"; fi
mkdir -p "$(dirname "$log")"

oom_kill_count() {
  awk '$1 == "oom_kill" { print $2; found = 1 } END { if (!found) print 0 }' \
    /sys/fs/cgroup/memory.events
}
host_memory_used_percent() {
  awk '
    /^MemTotal:/ { total = $2 }
    /^MemAvailable:/ { available = $2 }
    END {
      if (total > 0 && available >= 0) print int((total - available) * 100 / total)
      else print 0
    }
  ' /proc/meminfo
}
largest_running_pid() {
  local pid rss state target best_pid="" best_rss=-1
  local -a current_candidates=()
  if (( auto )); then
    for pid in /proc/[0-9]*; do
      pid="${pid##*/}"
      target="$(readlink "/proc/$pid/exe" 2>/dev/null || true)"
      [[ "$target" == */gpu-simulator/bin/release/accel-sim.out ||
         "$target" == */gpu-simulator/bin/release/accel-sim.out\ \(deleted\) ]] || continue
      current_candidates+=("$pid")
    done
  else
    current_candidates=("${candidates[@]}")
  fi
  for pid in "${current_candidates[@]}"; do
    [[ -r "/proc/$pid/status" ]] || continue
    state="$(awk '/^State:/ {print $2; exit}' "/proc/$pid/status")"
    [[ "$state" != T && "$state" != t ]] || continue
    rss="$(awk '/^VmRSS:/ {print $2; exit}' "/proc/$pid/status")"
    rss="${rss:-0}"
    if (( rss > best_rss )); then best_rss="$rss"; best_pid="$pid"; fi
  done
  [[ -n "$best_pid" ]] && printf '%s %s\n' "$best_pid" "$best_rss"
}

simulator_cwd() {
  readlink "/proc/$1/cwd" 2>/dev/null || true
}

terminate_workload_pair() {
  local selected_pid="$1" selected_cwd pair_dir pid target cwd
  selected_cwd="$(simulator_cwd "$selected_pid")"
  pair_dir="$(dirname "$selected_cwd")"
  [[ -n "$selected_cwd" && "$pair_dir" != . ]] || return 1

  for pid_path in /proc/[0-9]*; do
    pid="${pid_path##*/}"
    target="$(readlink "/proc/$pid/exe" 2>/dev/null || true)"
    [[ "$target" == */gpu-simulator/bin/release/accel-sim.out ||
       "$target" == */gpu-simulator/bin/release/accel-sim.out\ \(deleted\) ]] || continue
    cwd="$(simulator_cwd "$pid")"
    [[ "$(dirname "$cwd")" == "$pair_dir" ]] || continue
    kill -TERM "$pid" 2>/dev/null || true
    printf '%s ' "$pid"
  done
}

last_oom="$(oom_kill_count)"
last_memory_limit_epoch=0
if (( auto )); then candidate_label="auto"; else candidate_label="${candidates[*]}"; fi
printf '%s START oom_kill=%s candidates=%s\n' "$(date --iso-8601=seconds)" \
  "$last_oom" "$candidate_label" >> "$log"
while :; do
  sleep "$interval_sec"
  now_oom="$(oom_kill_count)"
  now_epoch="$(date +%s)"
  used_percent="$(host_memory_used_percent)"
  reason=""
  if (( now_oom > last_oom )); then reason="OOM"; fi
  if (( used_percent >= max_memory_percent &&
        now_epoch - last_memory_limit_epoch >= memory_limit_cooldown_sec )); then
    reason="${reason:+${reason}_}MEMORY_LIMIT"
    last_memory_limit_epoch="$now_epoch"
  fi
  [[ -n "$reason" ]] || continue
  selection="$(largest_running_pid || true)"
  if [[ -z "$selection" ]]; then
    printf '%s %s oom_kill=%s used_percent=%s action=none reason=no_live_candidate\n' \
      "$(date --iso-8601=seconds)" "$reason" "$now_oom" "$used_percent" >> "$log"
  else
    read -r pid rss <<< "$selection"
    if [[ "$action" == terminate-pair ]]; then
      pair_pids="$(terminate_workload_pair "$pid" || true)"
      printf '%s %s oom_kill=%s used_percent=%s action=SIGTERM_PAIR selected_pid=%s rss_kib=%s pids="%s"\n' \
        "$(date --iso-8601=seconds)" "$reason" "$now_oom" "$used_percent" \
        "$pid" "$rss" "$pair_pids" >> "$log"
    else
      kill -STOP "$pid"
      printf '%s %s oom_kill=%s used_percent=%s action=SIGSTOP pid=%s rss_kib=%s resume="kill -CONT %s"\n' \
        "$(date --iso-8601=seconds)" "$reason" "$now_oom" "$used_percent" \
        "$pid" "$rss" "$pid" >> "$log"
    fi
  fi
  last_oom="$now_oom"
done
