#!/usr/bin/env bash
# Read-only cgroup admission for future FAST64 precompute workers.  It is
# intentionally independent of the frozen R2 closeout chain.
set -euo pipefail

usage() { echo "usage: $0 --output FILE [--workers N] [--interval SECONDS]" >&2; exit 2; }
output= workers=1 interval=60
while [ "$#" -gt 0 ]; do
  case "$1" in
    --output) output=${2:-}; shift 2 ;;
    --workers) workers=${2:-}; shift 2 ;;
    --interval) interval=${2:-}; shift 2 ;;
    *) usage ;;
  esac
done
test -n "$output" && [[ "$workers" =~ ^[1-9][0-9]*$ ]] && [[ "$interval" =~ ^[1-9][0-9]*$ ]] || usage

cgroup=/sys/fs/cgroup
field() { awk -v key="$2" '$1 == key { print $2; exit }' "$1"; }
cpu_stat() { field "$cgroup/cpu.stat" "$1"; }
cpu_snapshot() { awk '/^cpu / { t=0; for(i=2;i<=NF;i++)t+=$i; print t "\t" $5; exit }' /proc/stat; }
percentile() {
  local values=$1 count rank
  count=$(printf '%s\n' "$values" | awk 'NF {n++} END {print n+0}')
  [ "$count" -gt 0 ] || { echo 0; return; }
  rank=$(( (95*count+99)/100 ))
  printf '%s\n' "$values" | awk -v r="$rank" 'NR==r {print;exit}'
}
rss_p95() {
  percentile "$(pgrep -x accel-sim.out | while read -r p; do ps -o rss= -p "$p" 2>/dev/null || true; done | awk '$1~/^[0-9]+$/ {print $1*1024}' | sort -n)"
}
out_p95() {
  percentile "$(find /workspace/fast64-runs -maxdepth 1 -mindepth 1 -type d -name 'fast64_*' -print0 | xargs -0 -r du -sb 2>/dev/null | awk '{print $1}' | sort -n)"
}

read -r host_total0 host_idle0 < <(cpu_snapshot)
usage0=$(cpu_stat usage_usec); n_throttle0=$(cpu_stat nr_throttled); throttle0=$(cpu_stat throttled_usec)
swap_out0=$(field /proc/vmstat pswpout); oom0=$(field "$cgroup/memory.events" oom_kill)
sleep "$interval"
read -r host_total1 host_idle1 < <(cpu_snapshot)
usage1=$(cpu_stat usage_usec); n_throttle1=$(cpu_stat nr_throttled); throttle1=$(cpu_stat throttled_usec)
swap_out1=$(field /proc/vmstat pswpout); oom1=$(field "$cgroup/memory.events" oom_kill)

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
selection=$(python3 "$repo_root/util/dtc_l1/select_fast64_r2_cpus.py" --format tsv)
candidates=$(printf '%s\n' "$selection" | awk -F '\t' '$1=="available_distinct_physical_cores" {print $2;exit}')
candidate_cpus=$(printf '%s\n' "$selection" | awk -F '\t' '$1=="candidate_cpus" {print $2;exit}')
read -r quota period < "$cgroup/cpu.max"; test "$quota" != max
quota_cores=$((quota/period)); usage_delta=$((usage1-usage0)); throttle_delta=$((throttle1-throttle0))
cpu_cores=$(awk -v u="$usage_delta" -v s="$interval" 'BEGIN {printf "%.3f",u/(s*1000000.0)}')
throttle_pct=$(awk -v t="$throttle_delta" -v s="$interval" -v c="$quota_cores" 'BEGIN {printf "%.4f",100*t/(s*1000000.0*c)}')
host_idle_pct=$(awk -v t=$((host_total1-host_total0)) -v i=$((host_idle1-host_idle0)) 'BEGIN {if(t<=0) print "0.00"; else printf "%.2f",100*i/t}')
p95=$(rss_p95); memory_required=$((p95*(workers+1)))
memory_current=$(cat "$cgroup/memory.current"); memory_max=$(cat "$cgroup/memory.max"); test "$memory_max" != max; memory_headroom=$((memory_max-memory_current))
memavailable=$(awk '/^MemAvailable:/ {print $2*1024;exit}' /proc/meminfo)
psi=$(awk '$1=="some" {for(i=1;i<=NF;i++)if($i~/^avg10=/){sub(/^avg10=/,"",$i);print $i;exit}}' "$cgroup/memory.pressure")
expected_out=$(out_p95); output_required=$((expected_out*workers+1024*1024*1024)); output_free=$(df -B1 --output=avail /workspace/fast64-runs | awk 'NR==2 {print $1}')
safe=YES reason=PASS_FUTURE_PRECOMPUTE_ADMISSION
if [ "$candidates" -lt "$workers" ] || [ $((swap_out1-swap_out0)) -ne 0 ] || [ $((oom1-oom0)) -ne 0 ] ||
   awk -v x="$psi" 'BEGIN{exit !(x>0)}' || awk -v x="$throttle_pct" 'BEGIN{exit !(x>=1)}' ||
   awk -v u="$cpu_cores" -v w="$workers" -v q="$quota_cores" 'BEGIN{exit !((u+w)>q*.90)}' ||
   [ "$memavailable" -lt "$memory_required" ] || [ "$memory_headroom" -lt "$memory_required" ] || [ "$output_free" -lt "$output_required" ]; then
  safe=NO; reason=RESOURCE_GATE_REJECTED_SEE_FIELDS
fi
parent=$(dirname "$output"); mkdir -p -- "$parent"; tmp=$(mktemp "$parent/.${output##*/}.tmp.XXXXXX")
{
  printf 'schema\tFAST64_FUTURE_PRECOMPUTE_RESOURCE_AUDIT_V1\n'
  printf 'observed_utc\t%s\nsample_interval_seconds\t%s\nrequested_new_workers\t%s\n' "$(date -u +%FT%TZ)" "$interval" "$workers"
  printf 'cpu_max\t%s\ncpu_quota_cores\t%s\ncgroup_cpu_core_equivalents\t%s\ncgroup_nr_throttled_delta\t%s\ncgroup_throttled_pct_of_quota\t%s\n' "$(cat "$cgroup/cpu.max")" "$quota_cores" "$cpu_cores" "$((n_throttle1-n_throttle0))" "$throttle_pct"
  printf 'host_idle_pct_supplemental\t%s\nhost_loadavg_supplemental\t%s\n' "$host_idle_pct" "$(cut -d' ' -f1-3 /proc/loadavg)"
  printf 'available_distinct_physical_cores\t%s\ncandidate_cpus\t%s\n' "$candidates" "$candidate_cpus"
  printf 'p95_rss_bytes\t%s\nmemory_required_bytes\t%s\nmemavailable_bytes\t%s\nmemory_current_bytes\t%s\nmemory_max_bytes\t%s\nmemory_headroom_bytes\t%s\n' "$p95" "$memory_required" "$memavailable" "$memory_current" "$memory_max" "$memory_headroom"
  printf 'swap_so_delta\t%s\noom_kill_delta\t%s\nmemory_psi_avg10\t%s\n' "$((swap_out1-swap_out0))" "$((oom1-oom0))" "$psi"
  printf 'output_required_bytes\t%s\noutput_free_bytes\t%s\nsafe_to_launch\t%s\nauthorized_workers\t%s\nadmission_reason\t%s\n' "$output_required" "$output_free" "$safe" "$([ "$safe" = YES ] && echo "$workers" || echo 0)" "$reason"
} >"$tmp"
mv -f -- "$tmp" "$output"
printf 'FAST64_FUTURE_PRECOMPUTE_RESOURCE_AUDIT_WRITTEN\t%s\n' "$output"
