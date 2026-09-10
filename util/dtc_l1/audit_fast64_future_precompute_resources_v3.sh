#!/usr/bin/env bash
# Future-only wrapper around the multi-window v2 observation.  It adds the
# explicit FAST64-only RSS distribution, a fixed MemAvailable reserve and the
# CFS-throttling rejection omitted from v2.  It never edits a live controller.
set -euo pipefail

usage() {
  echo "usage: $0 --output FILE [--workers N] [--interval SECONDS] [--samples N] [--mem-reserve-gib N]" >&2
  exit 2
}

output= workers=1 interval=20 samples=3 reserve_gib=16
while [ "$#" -gt 0 ]; do
  case "$1" in
    --output) output=${2:-}; shift 2 ;;
    --workers) workers=${2:-}; shift 2 ;;
    --interval) interval=${2:-}; shift 2 ;;
    --samples) samples=${2:-}; shift 2 ;;
    --mem-reserve-gib) reserve_gib=${2:-}; shift 2 ;;
    *) usage ;;
  esac
done
test -n "$output" && [[ "$workers" =~ ^[1-9][0-9]*$ ]] && \
  [[ "$interval" =~ ^[1-9][0-9]*$ ]] && [[ "$samples" =~ ^[2-9][0-9]*$ ]] && \
  [[ "$reserve_gib" =~ ^[1-9][0-9]*$ ]] || usage

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
parent=$(dirname "$output")
mkdir -p -- "$parent"
v2_output=$(mktemp "$parent/.${output##*/}.v2.XXXXXX")
cleanup() { rm -f -- "$v2_output"; }
trap cleanup EXIT
"$repo_root/util/dtc_l1/audit_fast64_future_precompute_resources_v2.sh" \
  --output "$v2_output" --workers "$workers" --interval "$interval" --samples "$samples" >/dev/null

fast64_rss=$(
  while read -r pid; do
    test -r "/proc/$pid/cmdline" || continue
    state=$(ps -o stat= -p "$pid" 2>/dev/null | awk '{print $1}')
    case "$state" in Z*|'') continue ;; esac
    args=$(tr '\0' ' ' <"/proc/$pid/cmdline")
    case "$args" in *fast64*|*dtc-fast64*) ps -o rss= -p "$pid" 2>/dev/null ;; esac
  done < <(pgrep -x accel-sim.out || true) | awk '$1~/^[0-9]+$/ {print $1*1024}' | sort -n
)
fast64_workers=$(printf '%s\n' "$fast64_rss" | awk 'NF {n++} END {print n+0}')
fast64_p50=$(printf '%s\n' "$fast64_rss" | awk 'NF {a[++n]=$1} END {if(!n)print 0; else print a[int((n+1)/2)]}')
fast64_p95=$(printf '%s\n' "$fast64_rss" | awk 'NF {a[++n]=$1} END {if(!n)print 0; else {r=int((95*n+99)/100); print a[r]}}')
fast64_total_rss=$(printf '%s\n' "$fast64_rss" | awk '{s+=$1} END {print s+0}')
fast64_max_rss=$(printf '%s\n' "$fast64_rss" | tail -1); fast64_max_rss=${fast64_max_rss:-0}
memavailable=$(awk '/^MemAvailable:/ {print $2*1024; exit}' /proc/meminfo)
projected_new_rss=$((fast64_p95 * workers))
projected_memavailable=$((memavailable - projected_new_rss))
reserve_bytes=$((reserve_gib * 1024 * 1024 * 1024))
throttle_events=$(awk -F '\t' '$1~/^[0-9]+$/ && $10>0 {n+=$10} END {print n+0}' "$v2_output")
safe_v2=$(awk -F '\t' '$1=="safe_to_launch" {print $2; exit}' "$v2_output")
reason_v2=$(awk -F '\t' '$1=="admission_reason" {print $2; exit}' "$v2_output")
safe=$safe_v2
reason=$reason_v2
if [ "$safe" = YES ]; then reason=PASS_FUTURE_PRECOMPUTE_ADMISSION_V3; fi
if [ "$throttle_events" -gt 0 ]; then safe=NO; reason=CFS_THROTTLING_OBSERVED; fi
if [ "$projected_memavailable" -lt "$reserve_bytes" ]; then safe=NO; reason=MEMAVAILABLE_RESERVE_NOT_MET; fi

tmp=$(mktemp "$parent/.${output##*/}.tmp.XXXXXX")
FAST64_V3_SAFE="$safe" FAST64_V3_WORKERS="$workers" FAST64_V3_REASON="$reason" \
  awk -F '\t' 'BEGIN{OFS="\t"} $1=="schema" {$2="FAST64_FUTURE_PRECOMPUTE_RESOURCE_AUDIT_V3"} $1=="safe_to_launch" {$2=ENVIRON["FAST64_V3_SAFE"]} $1=="authorized_workers" {$2=(ENVIRON["FAST64_V3_SAFE"]=="YES" ? ENVIRON["FAST64_V3_WORKERS"] : 0)} $1=="admission_reason" {$2=ENVIRON["FAST64_V3_REASON"]} {print}' "$v2_output" > "$tmp"
{
  printf 'current_fast64_live_workers\t%s\n' "$fast64_workers"
  printf 'projected_fast64_workers\t%s\n' "$((fast64_workers + workers))"
  printf 'fast64_rss_p50_bytes\t%s\n' "$fast64_p50"
  printf 'fast64_rss_p95_bytes\t%s\n' "$fast64_p95"
  printf 'fast64_rss_max_bytes\t%s\n' "$fast64_max_rss"
  printf 'fast64_total_rss_bytes\t%s\n' "$fast64_total_rss"
  printf 'projected_new_rss_bytes\t%s\n' "$projected_new_rss"
  printf 'memavailable_reserve_bytes\t%s\n' "$reserve_bytes"
  printf 'projected_memavailable_after_bytes\t%s\n' "$projected_memavailable"
  printf 'cfs_throttle_event_windows\t%s\n' "$throttle_events"
} >> "$tmp"
mv -f -- "$tmp" "$output"
printf 'FAST64_FUTURE_PRECOMPUTE_RESOURCE_AUDIT_V3_WRITTEN\t%s\n' "$output"
