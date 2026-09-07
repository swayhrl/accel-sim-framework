#!/usr/bin/env bash
# Read-only resource observation for a future FAST64.1 immutable-R2 admission.
# It deliberately does not decide safe_to_launch or dispatch a simulator:
# N_safe is a contemporaneous scheduling judgment bound to the observed host.
set -euo pipefail

usage() {
  echo "usage: $0 --output FILE [--interval SECONDS]" >&2
  exit 2
}

output=
interval=60
while [ "$#" -gt 0 ]; do
  case "$1" in
    --output) output=${2:-}; shift 2 ;;
    --interval) interval=${2:-}; shift 2 ;;
    *) usage ;;
  esac
done
test -n "$output" && [[ "$interval" =~ ^[1-9][0-9]*$ ]] || usage

read_vmstat() {
  awk '$1 == "pswpin" { pin=$2 } $1 == "pswpout" { pout=$2 }
       END { if (pin != "" && pout != "") print pin "\t" pout; else exit 1 }' /proc/vmstat
}
read_cpu() {
  awk '/^cpu / { total=0; for (i=2; i<=NF; ++i) total+=$i; print total "\t" $6; exit }' /proc/stat
}
read_memavailable() { awk '/^MemAvailable:/ { print $2 * 1024; exit }' /proc/meminfo; }
read_cgroup() {
  local key=$1
  cat "/sys/fs/cgroup/$key"
}
rss_p95_bytes() {
  local values count rank
  values=$(pgrep -x accel-sim.out | while read -r pid; do
    ps -o rss= -p "$pid" 2>/dev/null || true
  done | awk '{ if ($1 ~ /^[0-9]+$/) print $1 * 1024 }' | sort -n)
  count=$(printf '%s\n' "$values" | awk 'NF { n++ } END { print n+0 }')
  if [ "$count" -eq 0 ]; then
    printf '0\n'
    return
  fi
  rank=$(( (95 * count + 99) / 100 ))
  printf '%s\n' "$values" | awk -v rank="$rank" 'NR == rank { print; exit }'
}

read -r swap_in_0 swap_out_0 < <(read_vmstat)
read -r cpu_total_0 cpu_iowait_0 < <(read_cpu)
oom_0=$(awk '$1 == "oom_kill" { print $2; exit }' /sys/fs/cgroup/memory.events)
sleep "$interval"
read -r swap_in_1 swap_out_1 < <(read_vmstat)
read -r cpu_total_1 cpu_iowait_1 < <(read_cpu)
oom_1=$(awk '$1 == "oom_kill" { print $2; exit }' /sys/fs/cgroup/memory.events)

cpu_delta=$((cpu_total_1 - cpu_total_0))
iowait_delta=$((cpu_iowait_1 - cpu_iowait_0))
iowait_pct=$(awk -v total="$cpu_delta" -v wait="$iowait_delta" 'BEGIN {
  if (total <= 0) print "0.00"; else printf "%.2f", (100.0 * wait / total)
}')
output_parent=$(dirname "$output")
mkdir -p -- "$output_parent"
tmp_output="$output_parent/.${output##*/}.tmp.$$"
{
  printf 'schema\tFAST64_R2_RESOURCE_OBSERVATION_V1\n'
  printf 'observed_utc\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'sample_interval_seconds\t%s\n' "$interval"
  printf 'cpuset_effective\t%s\n' "$(read_cgroup cpuset.cpus.effective)"
  printf 'cpu_max\t%s\n' "$(read_cgroup cpu.max)"
  printf 'loadavg\t%s\n' "$(cut -d' ' -f1-3 /proc/loadavg)"
  printf 'simulator_worker_count\t%s\n' "$(pgrep -cx accel-sim.out || true)"
  printf 'p95_rss_bytes\t%s\n' "$(rss_p95_bytes)"
  printf 'memavailable_bytes\t%s\n' "$(read_memavailable)"
  printf 'memory_current_bytes\t%s\n' "$(read_cgroup memory.current)"
  printf 'memory_max_bytes\t%s\n' "$(read_cgroup memory.max)"
  printf 'swap_si_delta\t%s\n' "$((swap_in_1 - swap_in_0))"
  printf 'swap_so_delta\t%s\n' "$((swap_out_1 - swap_out_0))"
  printf 'oom_kill_delta\t%s\n' "$((oom_1 - oom_0))"
  printf 'iowait_pct\t%s\n' "$iowait_pct"
  printf 'output_free_bytes\t%s\n' "$(df -B1 --output=avail /workspace/fast64-runs | awk 'NR == 2 { print $1 }')"
  printf 'safe_to_launch\tUNASSESSED_REQUIRES_CURRENT_N_SAFE_JUDGMENT\n'
} >"$tmp_output"
mv -f -- "$tmp_output" "$output"
printf 'FAST64_R2_RESOURCE_OBSERVATION_WRITTEN\t%s\n' "$output"
