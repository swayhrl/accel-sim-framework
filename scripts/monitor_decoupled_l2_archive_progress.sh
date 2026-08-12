#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/monitor_decoupled_l2_archive_progress.sh --output-dir DIR
       [--interval-sec N] [--watch-pid PID]... [--status-file FILE]...
       [--run-root DIR]... [--archive FILE]...

Writes an immediate snapshot, a detailed snapshot every INTERVAL-SEC seconds
(default 1200), and an immediate event snapshot whenever a watched PID or
status file changes. This monitor intentionally runs until it is stopped.
EOF
}

output_dir=""; interval_sec=1200
declare -a watch_pids status_files run_roots archives
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir) output_dir="$2"; shift 2 ;;
    --interval-sec) interval_sec="$2"; shift 2 ;;
    --watch-pid) watch_pids+=("$2"); shift 2 ;;
    --status-file) status_files+=("$2"); shift 2 ;;
    --run-root) run_roots+=("$2"); shift 2 ;;
    --archive) archives+=("$2"); shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -n "$output_dir" ]] || { echo "error: --output-dir is required" >&2; exit 2; }
[[ "$interval_sec" =~ ^[0-9]+$ && "$interval_sec" -gt 0 ]] || {
  echo "error: --interval-sec must be positive" >&2; exit 2;
}
for pid in "${watch_pids[@]:-}"; do
  [[ "$pid" =~ ^[0-9]+$ ]] || { echo "error: invalid --watch-pid $pid" >&2; exit 2; }
done
mkdir -p "$output_dir"
output_dir="$(cd "$output_dir" && pwd)"
started_epoch="$(date +%s)"
latest="$output_dir/latest.txt"
history="$output_dir/history.csv"
printf 'time,reason,elapsed_sec,free_gib,cgroup_mem_gib,completed_runs,failed_runs\n' > "$history"

read_signature() {
  {
    for pid in "${watch_pids[@]:-}"; do
      if kill -0 "$pid" 2>/dev/null; then printf 'pid:%s:running\n' "$pid"
      else printf 'pid:%s:exited\n' "$pid"; fi
    done
    for file in "${status_files[@]:-}"; do
      printf 'status:%s:' "$file"
      [[ -f "$file" ]] && sha256sum "$file" | awk '{print $1}' || printf 'missing'
    done
    for root in "${run_roots[@]:-}"; do
      [[ -d "$root" ]] || continue
      # Summary/failure changes are discrete completion events. Do not include
      # smoke.out: its frequent progress writes would turn monitoring into a
      # 30-second polling log instead of meaningful archive-status snapshots.
      find "$root" -type f \( -name summary.csv -o -name failures.csv \) \
        -printf 'result:%p:%s:%T@\n' 2>/dev/null | sort
    done
  } | sha256sum | awk '{print $1}'
}

snapshot() {
  local reason="$1" now elapsed free_kib free_gib mem_bytes mem_gib completed=0 failed=0
  now="$(date --iso-8601=seconds)"; elapsed="$(( $(date +%s) - started_epoch ))"
  free_kib="$(df -Pk "$output_dir" | awk 'NR == 2 {print $4}')"
  free_gib="$((free_kib / 1024 / 1024))"
  mem_bytes="$(cat /sys/fs/cgroup/memory.current 2>/dev/null || printf 0)"
  mem_gib="$((mem_bytes / 1024 / 1024 / 1024))"
  for root in "${run_roots[@]:-}"; do
    [[ -d "$root" ]] || continue
    while IFS= read -r summary; do
      completed=$((completed + $(awk 'END { print (NR ? NR - 1 : 0) }' "$summary")))
    done < <(find "$root" -type f -name summary.csv -print 2>/dev/null)
    while IFS= read -r failures; do
      failed=$((failed + $(awk 'END { print (NR ? NR - 1 : 0) }' "$failures")))
    done < <(find "$root" -type f -name failures.csv -print 2>/dev/null)
  done
  {
    printf 'time=%s\nreason=%s\nelapsed_sec=%s\nfree_gib=%s\ncgroup_memory_gib=%s\n' \
      "$now" "$reason" "$elapsed" "$free_gib" "$mem_gib"
    printf 'completed_backend_runs=%s\nfailed_backend_runs=%s\n' "$completed" "$failed"
    printf '\n[watched_pids]\n'
    for pid in "${watch_pids[@]:-}"; do
      if kill -0 "$pid" 2>/dev/null; then ps -o pid,stat,etime,%cpu,%mem,cmd -p "$pid" | tail -1
      else printf 'pid=%s exited\n' "$pid"; fi
    done
    printf '\n[status_files]\n'
    for file in "${status_files[@]:-}"; do
      printf 'file=%s\n' "$file"
      [[ -f "$file" ]] && sed -n '1,32p' "$file" || printf 'missing\n'
    done
    printf '\n[archives]\n'
    for archive in "${archives[@]:-}"; do
      [[ -f "$archive" ]] && stat -c '%n bytes=%s mtime=%y' "$archive" || printf 'missing %s\n' "$archive"
    done
  } > "$latest"
  printf '%s,%s,%s,%s,%s,%s,%s\n' "$now" "$reason" "$elapsed" "$free_gib" \
    "$mem_gib" "$completed" "$failed" >> "$history"
}

last_signature="$(read_signature)"
snapshot START
next_report="$(( $(date +%s) + interval_sec ))"
while true; do
  sleep 30
  signature="$(read_signature)"
  now_epoch="$(date +%s)"
  if [[ "$signature" != "$last_signature" ]]; then
    snapshot EVENT
    last_signature="$signature"
    next_report="$((now_epoch + interval_sec))"
  elif (( now_epoch >= next_report )); then
    snapshot PERIODIC
    next_report="$((now_epoch + interval_sec))"
  fi
done
