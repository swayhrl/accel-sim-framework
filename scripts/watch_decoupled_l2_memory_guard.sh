#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/watch_decoupled_l2_memory_guard.sh (--pid PID [--pid PID ...] | --auto)
       [--interval-sec N] [--max-memory-percent N]
       [--max-simulator-rss-gb N]
       [--memory-limit-cooldown-sec N] [--action log|stop|terminate-pair] [--log FILE]

Watch cgroup memory.events for a new OOM kill. Optionally, stop before an OOM
when host memory consumption reaches MAX-MEMORY-PERCENT of MemTotal. A
threshold event can also be logged without changing any workload. SIGSTOP
preserves simulator state for a later `kill -CONT PID`; it deliberately does
not claim to reclaim its already allocated memory. This is a last-resort
growth brake for live archive runs, not an admission controller.

`--max-simulator-rss-gb` limits only the aggregate RSS of Accel-Sim
executables whose cwd is below this experiment's `hw_run/` directory.  It is
the appropriate capacity limit on a shared host: unrelated users, page cache,
and IDE processes cannot cause an experiment workload to be terminated.
`--max-memory-percent` remains a legacy host-wide emergency guard. Use
`--action log` with an experiment RSS limit to monitor an in-flight pair
without ever changing it.

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
max_simulator_rss_gb=0
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
    --max-simulator-rss-gb) max_simulator_rss_gb="$2"; shift 2 ;;
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
[[ "$max_simulator_rss_gb" =~ ^[0-9]+$ ]] || {
  echo "error: --max-simulator-rss-gb must be a non-negative integer" >&2; exit 2;
}
[[ "$memory_limit_cooldown_sec" =~ ^[0-9]+$ ]] || {
  echo "error: --memory-limit-cooldown-sec must be non-negative" >&2; exit 2;
}
[[ "$action" == log || "$action" == stop || "$action" == terminate-pair ]] || {
  echo "error: --action must be log, stop, or terminate-pair" >&2; exit 2;
}
if [[ -z "$log" ]]; then log="memory_guard.$(date +%Y%m%d_%H%M%S).log"; fi
mkdir -p "$(dirname "$log")"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
experiment_root="$repo_root/hw_run"

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
is_accel_sim_pid() {
  local cwd comm
  # A process may exit after globbing /proc but before this read.  Treat that
  # normal race as a non-candidate instead of leaking a shell diagnostic into
  # the monitor log.
  { IFS= read -r comm < "/proc/$1/comm"; } 2>/dev/null || return 1
  [[ "$comm" == accel-sim.out ]] || return 1
  cwd="$(readlink "/proc/$1/cwd" 2>/dev/null || true)"
  [[ "$cwd" == "$experiment_root"/* ]]
}

simulator_rss_kib() {
  local pid rss total=0
  if (( auto )); then
    for pid_path in /proc/[0-9]*; do
      pid="${pid_path##*/}"
      is_accel_sim_pid "$pid" || continue
      rss="$(awk '/^VmRSS:/ {print $2; exit}' "/proc/$pid/status" 2>/dev/null || true)"
      total=$(( total + ${rss:-0} ))
    done
  else
    for pid in "${candidates[@]}"; do
      [[ -r "/proc/$pid/status" ]] || continue
      rss="$(awk '/^VmRSS:/ {print $2; exit}' "/proc/$pid/status")"
      total=$(( total + ${rss:-0} ))
    done
  fi
  printf '%s\n' "$total"
}
largest_running_pid() {
  local pid rss state best_pid="" best_rss=-1
  local -a current_candidates=()
  if (( auto )); then
    for pid in /proc/[0-9]*; do
      pid="${pid##*/}"
      is_accel_sim_pid "$pid" || continue
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

# For a hard ceiling, selection must reflect the memory that terminating an
# entire backend pair actually returns.  Choosing the single largest process
# can otherwise sacrifice a smaller pair when one member happens to have a
# larger RSS than either member of the real largest pair.
largest_running_pair() {
  local pid rss state cwd pair_dir best_pid="" best_rss=-1
  local -a current_candidates=()
  local -A pair_rss=() pair_pid=()
  if (( auto )); then
    for pid_path in /proc/[0-9]*; do
      pid="${pid_path##*/}"
      is_accel_sim_pid "$pid" || continue
      current_candidates+=("$pid")
    done
  else
    current_candidates=("${candidates[@]}")
  fi
  for pid in "${current_candidates[@]}"; do
    [[ -r "/proc/$pid/status" ]] || continue
    state="$(awk '/^State:/ {print $2; exit}' "/proc/$pid/status")"
    [[ "$state" != T && "$state" != t ]] || continue
    cwd="$(simulator_cwd "$pid")"
    pair_dir="$(dirname "$cwd")"
    [[ -n "$cwd" && "$pair_dir" != . ]] || continue
    rss="$(awk '/^VmRSS:/ {print $2; exit}' "/proc/$pid/status")"
    rss="${rss:-0}"
    pair_rss["$pair_dir"]=$(( ${pair_rss[$pair_dir]:-0} + rss ))
    pair_pid["$pair_dir"]="$pid"
  done
  for pair_dir in "${!pair_rss[@]}"; do
    if (( pair_rss[$pair_dir] > best_rss )); then
      best_rss=${pair_rss[$pair_dir]}
      best_pid=${pair_pid[$pair_dir]}
    fi
  done
  [[ -n "$best_pid" ]] && printf '%s %s\n' "$best_pid" "$best_rss"
}

simulator_cwd() {
  readlink "/proc/$1/cwd" 2>/dev/null || true
}

terminate_workload_pair() {
  local selected_pid="$1" selected_cwd pair_dir pid cwd
  selected_cwd="$(simulator_cwd "$selected_pid")"
  pair_dir="$(dirname "$selected_cwd")"
  [[ -n "$selected_cwd" && "$pair_dir" != . ]] || return 1

  for pid_path in /proc/[0-9]*; do
    pid="${pid_path##*/}"
    is_accel_sim_pid "$pid" || continue
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
  simulator_rss="$(simulator_rss_kib)"
  reason=""
  if (( now_oom > last_oom )); then reason="OOM"; fi
  if (( used_percent >= max_memory_percent &&
        now_epoch - last_memory_limit_epoch >= memory_limit_cooldown_sec )); then
    reason="${reason:+${reason}_}MEMORY_LIMIT"
    last_memory_limit_epoch="$now_epoch"
  fi
  if (( max_simulator_rss_gb > 0 &&
        simulator_rss >= max_simulator_rss_gb * 1000 * 1000 * 1000 / 1024 &&
        now_epoch - last_memory_limit_epoch >= memory_limit_cooldown_sec )); then
    reason="${reason:+${reason}_}SIMULATOR_RSS_LIMIT"
    last_memory_limit_epoch="$now_epoch"
  fi
  [[ -n "$reason" ]] || continue
  if [[ "$action" == log ]]; then
    selection=""
  elif [[ "$action" == terminate-pair ]]; then
    selection="$(largest_running_pair || true)"
  else
    selection="$(largest_running_pid || true)"
  fi
  if [[ "$action" == log ]]; then
      printf '%s %s oom_kill=%s used_percent=%s simulator_rss_kib=%s action=LOG\n' \
      "$(date --iso-8601=seconds)" "$reason" "$now_oom" "$used_percent" \
      "$simulator_rss" >> "$log"
  elif [[ -z "$selection" ]]; then
      printf '%s %s oom_kill=%s used_percent=%s simulator_rss_kib=%s action=none reason=no_live_candidate\n' \
      "$(date --iso-8601=seconds)" "$reason" "$now_oom" "$used_percent" "$simulator_rss" >> "$log"
  else
    read -r pid rss <<< "$selection"
    if [[ "$action" == terminate-pair ]]; then
      pair_pids="$(terminate_workload_pair "$pid" || true)"
      printf '%s %s oom_kill=%s used_percent=%s simulator_rss_kib=%s action=SIGTERM_PAIR selected_pid=%s rss_kib=%s pids="%s"\n' \
        "$(date --iso-8601=seconds)" "$reason" "$now_oom" "$used_percent" \
        "$simulator_rss" "$pid" "$rss" "$pair_pids" >> "$log"
    else
      kill -STOP "$pid"
      printf '%s %s oom_kill=%s used_percent=%s action=SIGSTOP pid=%s rss_kib=%s resume="kill -CONT %s"\n' \
        "$(date --iso-8601=seconds)" "$reason" "$now_oom" "$used_percent" \
        "$pid" "$rss" "$pid" >> "$log"
    fi
  fi
  last_oom="$now_oom"
done
