#!/usr/bin/env bash
# Read-only, autonomous resource audit for a future FAST64.1 immutable-R2
# admission.  It never launches a simulator; it records Codex's current N_safe
# decision from measured topology, host pressure, and existing-run footprints.
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
read_throttled() { awk '$1 == "nr_throttled" { print $2; exit }' /sys/fs/cgroup/cpu.stat; }
read_memory_psi() { awk '$1 == "some" { for (i = 1; i <= NF; ++i) if ($i ~ /^avg10=/) { sub(/^avg10=/, "", $i); print $i; exit } }' /sys/fs/cgroup/memory.pressure; }
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
historical_r1_p95_output_bytes() {
  local values count rank
  values=$(find /workspace/fast64-runs -maxdepth 1 -mindepth 1 -type d -name 'fast64_1r1_*' -print0 |
    xargs -0 -r du -sb 2>/dev/null | awk '{ print $1 }' | sort -n)
  count=$(printf '%s\n' "$values" | awk 'NF { n++ } END { print n+0 }')
  if [ "$count" -eq 0 ]; then printf '0\n'; return; fi
  rank=$(( (95 * count + 99) / 100 ))
  printf '%s\n' "$values" | awk -v rank="$rank" 'NR == rank { print; exit }'
}

read -r swap_in_0 swap_out_0 < <(read_vmstat)
read -r cpu_total_0 cpu_iowait_0 < <(read_cpu)
oom_0=$(awk '$1 == "oom_kill" { print $2; exit }' /sys/fs/cgroup/memory.events)
throttled_0=$(read_throttled)
sleep "$interval"
read -r swap_in_1 swap_out_1 < <(read_vmstat)
read -r cpu_total_1 cpu_iowait_1 < <(read_cpu)
oom_1=$(awk '$1 == "oom_kill" { print $2; exit }' /sys/fs/cgroup/memory.events)
throttled_1=$(read_throttled)

cpu_delta=$((cpu_total_1 - cpu_total_0))
iowait_delta=$((cpu_iowait_1 - cpu_iowait_0))
iowait_pct=$(awk -v total="$cpu_delta" -v wait="$iowait_delta" 'BEGIN {
  if (total <= 0) print "0.00"; else printf "%.2f", (100.0 * wait / total)
}')
output_parent=$(dirname "$output")
mkdir -p -- "$output_parent"
tmp_output="$output_parent/.${output##*/}.tmp.$$"
repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
selector="$repo_root/util/dtc_l1/select_fast64_r2_cpus.py"
test -r "$selector"
selection=$(python3 "$selector" --format tsv)
candidate_count=$(printf '%s\n' "$selection" | awk -F '\t' '$1 == "available_distinct_physical_cores" { print $2; exit }')
candidate_cpus=$(printf '%s\n' "$selection" | awk -F '\t' '$1 == "candidate_cpus" { print $2; exit }')
narrow_workers=$(printf '%s\n' "$selection" | awk -F '\t' '$1 == "narrow_affinity_simulator_count" { print $2; exit }')
broad_workers=$(printf '%s\n' "$selection" | awk -F '\t' '$1 == "broad_affinity_simulator_count" { print $2; exit }')
test "$candidate_count" -ge 0 && test -n "$candidate_cpus"
read -r quota_us period_us < <(read_cgroup cpu.max)
quota_cores=$((quota_us / period_us))
load_one=$(awk '{print $1}' /proc/loadavg)
worker_count=$(pgrep -cx accel-sim.out || true)
p95_rss=$(rss_p95_bytes)
historical_p95_output=$(historical_r1_p95_output_bytes)
memavailable=$(read_memavailable)
memory_current=$(read_cgroup memory.current)
memory_max=$(read_cgroup memory.max)
memory_headroom=$((memory_max - memory_current))
swap_si_delta=$((swap_in_1 - swap_in_0))
swap_so_delta=$((swap_out_1 - swap_out_0))
oom_kill_delta=$((oom_1 - oom_0))
throttled_delta=$((throttled_1 - throttled_0))
memory_psi=$(read_memory_psi)
output_free=$(df -B1 --output=avail /workspace/fast64-runs | awk 'NR == 2 { print $1 }')
# A two-worker ramp is the conservative maximum.  It reserves three observed
# p95 RSS footprints (two new rows plus one safety footprint) and uses an
# observed 1-GiB output floor in addition to three historical R1 p95 outputs.
# Swap-in is recorded but is not a standalone rejection: with no swap-out,
# zero memory PSI and sufficient measured headroom it can be harmless page
# reactivation.  Swap-out, PSI, OOM, or exhausted headroom remain fail-closed.
memory_required=$((p95_rss * 3))
output_required=$((1024 * 1024 * 1024 + historical_p95_output * 3))
safe=YES
authorized=2
reason=PASS_CONSERVATIVE_TWO_WORKER_RAMP
if [ "$candidate_count" -lt 1 ] || [ "$quota_cores" -le "$worker_count" ] ||
   [ "$swap_so_delta" -ne 0 ] ||
   [ "$oom_kill_delta" -ne 0 ] || [ "$throttled_delta" -ne 0 ] ||
   awk -v value="$iowait_pct" 'BEGIN { exit !(value > 5.00) }' ||
   awk -v value="$memory_psi" 'BEGIN { exit !(value > 0.00) }' ||
   [ "$memavailable" -lt "$memory_required" ] || [ "$memory_headroom" -lt "$memory_required" ] ||
   [ "$output_free" -lt "$output_required" ] ||
   awk -v current_load="$load_one" -v quota="$quota_cores" 'BEGIN { exit !(current_load > quota * 0.95) }'; then
  safe=NO
  authorized=0
  reason=RESOURCE_GATE_REJECTED_SEE_FIELDS
elif [ "$candidate_count" -lt 2 ]; then
  authorized=1
  reason=PASS_ONE_WORKER_TOPOLOGY_LIMIT
fi
{
  printf 'schema\tFAST64_R2_RESOURCE_AUDIT_V1\n'
  printf 'observed_utc\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'sample_interval_seconds\t%s\n' "$interval"
  printf 'cpuset_effective\t%s\n' "$(read_cgroup cpuset.cpus.effective)"
  printf 'cpu_max\t%s\n' "$(read_cgroup cpu.max)"
  printf 'cpu_quota_cores\t%s\n' "$quota_cores"
  printf 'loadavg\t%s\n' "$(cut -d' ' -f1-3 /proc/loadavg)"
  printf 'simulator_worker_count\t%s\n' "$worker_count"
  printf 'p95_rss_bytes\t%s\n' "$p95_rss"
  printf 'historical_r1_p95_output_bytes\t%s\n' "$historical_p95_output"
  printf 'memavailable_bytes\t%s\n' "$memavailable"
  printf 'memory_current_bytes\t%s\n' "$memory_current"
  printf 'memory_max_bytes\t%s\n' "$memory_max"
  printf 'memory_headroom_bytes\t%s\n' "$memory_headroom"
  printf 'swap_si_delta\t%s\n' "$swap_si_delta"
  printf 'swap_so_delta\t%s\n' "$swap_so_delta"
  printf 'oom_kill_delta\t%s\n' "$oom_kill_delta"
  printf 'cgroup_throttled_delta\t%s\n' "$throttled_delta"
  printf 'memory_psi_avg10\t%s\n' "$memory_psi"
  printf 'iowait_pct\t%s\n' "$iowait_pct"
  printf 'output_free_bytes\t%s\n' "$output_free"
  printf 'available_distinct_physical_cores\t%s\n' "$candidate_count"
  printf 'candidate_cpus\t%s\n' "$candidate_cpus"
  printf 'narrow_affinity_simulator_count\t%s\n' "$narrow_workers"
  printf 'broad_affinity_simulator_count\t%s\n' "$broad_workers"
  printf 'safe_to_launch\t%s\n' "$safe"
  printf 'authorized_workers\t%s\n' "$authorized"
  printf 'admission_reason\t%s\n' "$reason"
} >"$tmp_output"
mv -f -- "$tmp_output" "$output"
printf 'FAST64_R2_RESOURCE_AUDIT_WRITTEN\t%s\n' "$output"
