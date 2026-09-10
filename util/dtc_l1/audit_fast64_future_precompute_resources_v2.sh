#!/usr/bin/env bash
# Future-only FAST64 admission audit.  Unlike v1, it samples several windows
# and distinguishes one transient page-movement window from sustained pressure.
# It is intentionally independent of all live controller/collector bytes.
set -euo pipefail

usage() {
  echo "usage: $0 --output FILE [--workers N] [--interval SECONDS] [--samples N]" >&2
  exit 2
}

output= workers=1 interval=20 samples=3
while [ "$#" -gt 0 ]; do
  case "$1" in
    --output) output=${2:-}; shift 2 ;;
    --workers) workers=${2:-}; shift 2 ;;
    --interval) interval=${2:-}; shift 2 ;;
    --samples) samples=${2:-}; shift 2 ;;
    *) usage ;;
  esac
done
test -n "$output" && [[ "$workers" =~ ^[1-9][0-9]*$ ]] && \
  [[ "$interval" =~ ^[1-9][0-9]*$ ]] && [[ "$samples" =~ ^[2-9][0-9]*$ ]] || usage

cgroup=/sys/fs/cgroup
field() { awk -v key="$2" '$1 == key { print $2; exit }' "$1"; }
cpu_stat() { field "$cgroup/cpu.stat" "$1"; }
cpu_snapshot() { awk '/^cpu / { t=0; for (i=2;i<=NF;i++) t+=$i; print t "\t" $5; exit }' /proc/stat; }
memory_psi() { awk '$1=="some" {for(i=1;i<=NF;i++)if($i~/^avg10=/){sub(/^avg10=/,"",$i);print $i;exit}}' "$cgroup/memory.pressure"; }
major_faults() {
  local p sum=0 v
  while read -r p; do
    test -r "/proc/$p/stat" || continue
    v=$(awk '{print $12}' "/proc/$p/stat")
    sum=$((sum+v))
  done < <(pgrep -x accel-sim.out || true)
  echo "$sum"
}
io_bytes() {
  awk '{for(i=1;i<=NF;i++) if($i~/^(rbytes|wbytes)=/){split($i,a,"="); s+=a[2]}} END{print s+0}' "$cgroup/io.stat"
}
percentile() {
  local values=$1 count rank
  count=$(printf '%s\n' "$values" | awk 'NF {n++} END {print n+0}')
  [ "$count" -gt 0 ] || { echo 0; return; }
  rank=$(( (95*count+99)/100 ))
  printf '%s\n' "$values" | awk -v r="$rank" 'NR==r {print; exit}'
}
rss_p95() {
  percentile "$(pgrep -x accel-sim.out | while read -r p; do ps -o rss= -p "$p" 2>/dev/null || true; done | awk '$1~/^[0-9]+$/ {print $1*1024}' | sort -n)"
}
out_p95() {
  percentile "$(find /workspace/fast64-runs -maxdepth 1 -mindepth 1 -type d -name 'fast64_*' -print0 | xargs -0 -r du -sb 2>/dev/null | awk '{print $1}' | sort -n)"
}

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
selection=$(python3 "$repo_root/util/dtc_l1/select_fast64_r2_cpus.py" --format tsv)
candidates=$(printf '%s\n' "$selection" | awk -F '\t' '$1=="available_distinct_physical_cores" {print $2; exit}')
candidate_cpus=$(printf '%s\n' "$selection" | awk -F '\t' '$1=="candidate_cpus" {print $2; exit}')
read -r quota period < "$cgroup/cpu.max"; test "$quota" != max
quota_cores=$((quota/period))

declare -a sample_rows
sustained_swap_windows=0 max_psi=0 total_swapout=0 total_major_faults=0 total_iobytes=0
read -r host_total0 host_idle0 < <(cpu_snapshot)
usage0=$(cpu_stat usage_usec); throttle0=$(cpu_stat throttled_usec); nthrottle0=$(cpu_stat nr_throttled)
swap0=$(field /proc/vmstat pswpout); oom0=$(field "$cgroup/memory.events" oom_kill)
fault0=$(major_faults); io0=$(io_bytes)
for ((i=1; i<=samples; i++)); do
  sleep "$interval"
  read -r host_total1 host_idle1 < <(cpu_snapshot)
  usage1=$(cpu_stat usage_usec); throttle1=$(cpu_stat throttled_usec); nthrottle1=$(cpu_stat nr_throttled)
  swap1=$(field /proc/vmstat pswpout); oom1=$(field "$cgroup/memory.events" oom_kill)
  fault1=$(major_faults); io1=$(io_bytes); psi=$(memory_psi)
  swap_delta=$((swap1-swap0)); fault_delta=$((fault1-fault0)); io_delta=$((io1-io0))
  cpu_cores=$(awk -v u=$((usage1-usage0)) -v s="$interval" 'BEGIN{printf "%.3f",u/(s*1000000.0)}')
  throttle_pct=$(awk -v t=$((throttle1-throttle0)) -v s="$interval" -v c="$quota_cores" 'BEGIN{printf "%.4f",100*t/(s*1000000.0*c)}')
  idle_pct=$(awk -v t=$((host_total1-host_total0)) -v h=$((host_idle1-host_idle0)) 'BEGIN{if(t<=0)print "0.00";else printf "%.2f",100*h/t}')
  sample_rows+=("$i\t$swap_delta\t$fault_delta\t$io_delta\t$psi\t$((oom1-oom0))\t$cpu_cores\t$throttle_pct\t$idle_pct\t$((nthrottle1-nthrottle0))")
  [ "$swap_delta" -gt 0 ] && sustained_swap_windows=$((sustained_swap_windows+1))
  total_swapout=$((total_swapout+swap_delta)); total_major_faults=$((total_major_faults+fault_delta)); total_iobytes=$((total_iobytes+io_delta))
  awk -v a="$psi" -v b="$max_psi" 'BEGIN{exit !(a>b)}' && max_psi="$psi" || true
  host_total0=$host_total1; host_idle0=$host_idle1; usage0=$usage1; throttle0=$throttle1; nthrottle0=$nthrottle1
  swap0=$swap1; oom0=$oom1; fault0=$fault1; io0=$io1
done

p95=$(rss_p95); memory_required=$((p95*(workers+1)))
memory_current=$(cat "$cgroup/memory.current"); memory_max=$(cat "$cgroup/memory.max"); test "$memory_max" != max
memory_headroom=$((memory_max-memory_current)); memavailable=$(awk '/^MemAvailable:/ {print $2*1024;exit}' /proc/meminfo)
expected_out=$(out_p95); output_required=$((expected_out*workers+1024*1024*1024)); output_free=$(df -B1 --output=avail /workspace/fast64-runs | awk 'NR==2 {print $1}')

safe=YES; reason=PASS_FUTURE_PRECOMPUTE_ADMISSION_V2; swap_class=NO_SWAP_ACTIVITY
if [ "$sustained_swap_windows" -eq 1 ]; then swap_class=TRANSIENT_SWAP_ACTIVITY; fi
if [ "$sustained_swap_windows" -ge 2 ]; then swap_class=SUSTAINED_SWAP_ACTIVITY; safe=NO; reason=SUSTAINED_MEMORY_PRESSURE; fi
if awk -v x="$max_psi" 'BEGIN{exit !(x>0)}' || [ "$total_major_faults" -gt 1000 ] || \
   [ "$candidates" -lt "$workers" ] || [ "$memavailable" -lt "$memory_required" ] || \
   [ "$memory_headroom" -lt "$memory_required" ] || [ "$output_free" -lt "$output_required" ]; then
  safe=NO; reason=RESOURCE_GATE_REJECTED_SEE_FIELDS
fi

parent=$(dirname "$output"); mkdir -p -- "$parent"; tmp=$(mktemp "$parent/.${output##*/}.tmp.XXXXXX")
{
  printf 'schema\tFAST64_FUTURE_PRECOMPUTE_RESOURCE_AUDIT_V2\n'
  printf 'observed_utc\t%s\nrequested_new_workers\t%s\nsample_interval_seconds\t%s\nsample_count\t%s\n' "$(date -u +%FT%TZ)" "$workers" "$interval" "$samples"
  printf 'cpu_max\t%s\ncpu_quota_cores\t%s\navailable_distinct_physical_cores\t%s\ncandidate_cpus\t%s\n' "$(cat "$cgroup/cpu.max")" "$quota_cores" "$candidates" "$candidate_cpus"
  printf 'sample\tswap_so_delta_pages\tmajor_fault_delta\tcgroup_io_delta_bytes\tmemory_psi_avg10\toom_kill_delta\tcgroup_cpu_core_equivalents\tthrottled_pct_of_quota\thost_idle_pct_supplemental\tnr_throttled_delta\n'
  printf '%b\n' "${sample_rows[*]}" | tr ' ' '\n'
  printf 'swap_activity_class\t%s\nswap_so_total_pages\t%s\nmajor_fault_total\t%s\ncgroup_io_total_bytes\t%s\nmax_memory_psi_avg10\t%s\n' "$swap_class" "$total_swapout" "$total_major_faults" "$total_iobytes" "$max_psi"
  printf 'p95_rss_bytes\t%s\nmemory_required_bytes\t%s\nmemavailable_bytes\t%s\nmemory_current_bytes\t%s\nmemory_max_bytes\t%s\nmemory_headroom_bytes\t%s\n' "$p95" "$memory_required" "$memavailable" "$memory_current" "$memory_max" "$memory_headroom"
  printf 'output_required_bytes\t%s\noutput_free_bytes\t%s\nsafe_to_launch\t%s\nauthorized_workers\t%s\nadmission_reason\t%s\n' "$output_required" "$output_free" "$safe" "$([ "$safe" = YES ] && echo "$workers" || echo 0)" "$reason"
} > "$tmp"
mv -f -- "$tmp" "$output"
printf 'FAST64_FUTURE_PRECOMPUTE_RESOURCE_AUDIT_V2_WRITTEN\t%s\n' "$output"
