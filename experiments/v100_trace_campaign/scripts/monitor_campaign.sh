#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: monitor_campaign.sh --work-root DIR [--watch SECONDS]

Shows archive completion, available disk, GPU state, and the tail of the most
recent phase log. With --watch it refreshes until interrupted (Ctrl-C).
EOF
}

work_root=""
watch_seconds=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --work-root) work_root="$2"; shift 2 ;;
    --watch) watch_seconds="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ -n "$work_root" ]] || { echo "error: --work-root is required" >&2; exit 2; }
[[ -d "$work_root" ]] || { echo "error: work root does not exist: $work_root" >&2; exit 1; }
if [[ -n "$watch_seconds" && ! "$watch_seconds" =~ ^[1-9][0-9]*$ ]]; then
  echo "error: --watch must be a positive integer" >&2
  exit 2
fi

show_once() {
  date -u '+timestamp_utc=%FT%TZ'
  df -h "$work_root" | tail -n 1
  nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu \
    --format=csv,noheader 2>/dev/null || true
  printf 'verified_archives=%s\n' "$(find "$work_root/archives" -maxdepth 1 -type f -name '*.tar.zst' 2>/dev/null | wc -l | tr -d ' ')"
  recent_log="$(find "$work_root/runs" -type f -name '*.log' -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -n 1 | cut -d' ' -f2-)"
  if [[ -n "$recent_log" ]]; then
    printf 'latest_log=%s\n' "$recent_log"
    tail -n 12 "$recent_log"
  fi
}

if [[ -z "$watch_seconds" ]]; then
  show_once
else
  while true; do
    clear
    show_once
    sleep "$watch_seconds"
  done
fi
