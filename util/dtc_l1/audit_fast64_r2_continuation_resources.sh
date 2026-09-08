#!/usr/bin/env bash
# Read-only full-wave admission audit for the five future FAST64.1 immutable
# R2 rows.  This is deliberately separate from the live, SHA-pinned ramp
# auditor.  It does not inspect or alter any namespace or simulator.
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

cgroup=/sys/fs/cgroup
field() { awk -v key="$2" '$1 == key { print $2; exit }' "$1"; }
cpu_stat() {
  local key=$1
  field "$cgroup/cpu.stat" "$key"
}
vmstat() { field /proc/vmstat "$1"; }
mem_available() { awk '/^MemAvailable:/ { print $2 * 1024; exit }' /proc/meminfo; }
memory_psi() {
  awk '$1 == "some" { for (i = 1; i <= NF; ++i) if ($i ~ /^avg10=/) { sub(/^avg10=/, "", $i); print $i; exit } }' "$cgroup/memory.pressure"
}
cpu_snapshot() { awk '/^cpu / { total=0; for (i=2; i<=NF; ++i) total += $i; print total "\t" $5; exit }' /proc/stat; }
rss_p95() {
  local values count rank
  values=$(pgrep -x accel-sim.out | while read -r pid; do ps -o rss= -p "$pid" 2>/dev/null || true; done | awk '$1 ~ /^[0-9]+$/ { print $1 * 1024 }' | sort -n)
  count=$(printf '%s\n' "$values" | awk 'NF { n++ } END { print n+0 }')
  if [ "$count" -eq 0 ]; then printf '0\n'; return; fi
  rank=$(( (95 * count + 99) / 100 ))
  printf '%s\n' "$values" | awk -v rank="$rank" 'NR == rank { print; exit }'
}
expected_output_p95() {
  local values count rank
  values=$(find /workspace/fast64-runs -maxdepth 1 -mindepth 1 -type d -name 'fast64_1r1_*' -print0 |
    xargs -0 -r du -sb 2>/dev/null | awk '{ print $1 }' | sort -n)
  count=$(printf '%s\n' "$values" | awk 'NF { n++ } END { print n+0 }')
  if [ "$count" -eq 0 ]; then printf '0\n'; return; fi
  rank=$(( (95 * count + 99) / 100 ))
  printf '%s\n' "$values" | awk -v rank="$rank" 'NR == rank { print; exit }'
}

read -r total0 idle0 < <(cpu_snapshot)
usage0=$(cpu_stat usage_usec)
nr_throttled0=$(cpu_stat nr_throttled)
throttled_usec0=$(cpu_stat throttled_usec)
swap_in0=$(vmstat pswpin)
swap_out0=$(vmstat pswpout)
oom0=$(field "$cgroup/memory.events" oom_kill)
sleep "$interval"
read -r total1 idle1 < <(cpu_snapshot)
usage1=$(cpu_stat usage_usec)
nr_throttled1=$(cpu_stat nr_throttled)
throttled_usec1=$(cpu_stat throttled_usec)
swap_in1=$(vmstat pswpin)
swap_out1=$(vmstat pswpout)
oom1=$(field "$cgroup/memory.events" oom_kill)

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
selector="$repo_root/util/dtc_l1/select_fast64_r2_cpus.py"
selection=$(python3 "$selector" --format tsv)
candidate_count=$(printf '%s\n' "$selection" | awk -F '\t' '$1 == "available_distinct_physical_cores" { print $2; exit }')
candidate_cpus=$(printf '%s\n' "$selection" | awk -F '\t' '$1 == "candidate_cpus" { print $2; exit }')
test "$candidate_count" -ge 0 && test -n "$candidate_cpus"

read -r quota period < "$cgroup/cpu.max"
test "$quota" != max && [[ "$quota" =~ ^[1-9][0-9]*$ ]] && [[ "$period" =~ ^[1-9][0-9]*$ ]]
quota_cores=$((quota / period))
cpu_usage_delta=$((usage1 - usage0))
cpu_usage_cores=$(awk -v usage="$cpu_usage_delta" -v seconds="$interval" 'BEGIN { printf "%.3f", usage / (seconds * 1000000.0) }')
host_total_delta=$((total1 - total0))
host_idle_delta=$((idle1 - idle0))
host_idle_pct=$(awk -v total="$host_total_delta" -v idle="$host_idle_delta" 'BEGIN { if (total <= 0) print "0.00"; else printf "%.2f", 100.0 * idle / total }')
nr_throttled_delta=$((nr_throttled1 - nr_throttled0))
throttled_usec_delta=$((throttled_usec1 - throttled_usec0))
throttled_pct_of_quota=$(awk -v throttled="$throttled_usec_delta" -v seconds="$interval" -v cores="$quota_cores" 'BEGIN { if (seconds <= 0 || cores <= 0) print "100.00"; else printf "%.4f", 100.0 * throttled / (seconds * 1000000.0 * cores) }')
swap_si_delta=$((swap_in1 - swap_in0))
swap_so_delta=$((swap_out1 - swap_out0))
oom_kill_delta=$((oom1 - oom0))
memory_current=$(cat "$cgroup/memory.current")
memory_max=$(cat "$cgroup/memory.max")
test "$memory_max" != max
memory_headroom=$((memory_max - memory_current))
p95_rss=$(rss_p95)
memory_required=$((p95_rss * 6)) # five continuation workers plus one safety footprint
output_p95=$(expected_output_p95)
output_required=$((output_p95 * 5 + 1024 * 1024 * 1024))
output_free=$(df -B1 --output=avail /workspace/fast64-runs | awk 'NR == 2 { print $1 }')
memavailable=$(mem_available)
psi=$(memory_psi)
worker_count=$(pgrep -cx accel-sim.out || true)

# CPU admission is cgroup-scoped.  A nonzero throttling count alone is not
# material; reject only sustained throttled time (>=1% of the cgroup's quota),
# no distinct core candidates, or observed useful CPU plus five workers above
# a 90% cgroup-quota guard.  Host loadavg is recorded only as context.
safe=YES
reason=PASS_FULL_FIVE_WORKER_CONTINUATION
if [ "$candidate_count" -lt 5 ] ||
   awk -v used="$cpu_usage_cores" -v quota="$quota_cores" 'BEGIN { exit !((used + 5) > quota * 0.90) }' ||
   awk -v value="$throttled_pct_of_quota" 'BEGIN { exit !(value >= 1.00) }' ||
   [ "$swap_so_delta" -ne 0 ] || [ "$oom_kill_delta" -ne 0 ] ||
   awk -v value="$psi" 'BEGIN { exit !(value > 0.00) }' ||
   [ "$memavailable" -lt "$memory_required" ] || [ "$memory_headroom" -lt "$memory_required" ] ||
   [ "$output_free" -lt "$output_required" ]; then
  safe=NO
  reason=RESOURCE_GATE_REJECTED_SEE_FIELDS
fi

parent=$(dirname "$output")
mkdir -p -- "$parent"
tmp=$(mktemp "$parent/.${output##*/}.tmp.XXXXXX")
{
  printf 'schema\tFAST64_R2_CONTINUATION_RESOURCE_AUDIT_V1\n'
  printf 'observed_utc\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'sample_interval_seconds\t%s\n' "$interval"
  printf 'requested_new_workers\t5\n'
  printf 'cpuset_effective\t%s\n' "$(cat "$cgroup/cpuset.cpus.effective")"
  printf 'cpu_max\t%s\n' "$(cat "$cgroup/cpu.max")"
  printf 'cpu_quota_cores\t%s\n' "$quota_cores"
  printf 'cgroup_cpu_usage_usec_delta\t%s\n' "$cpu_usage_delta"
  printf 'cgroup_cpu_core_equivalents\t%s\n' "$cpu_usage_cores"
  printf 'cgroup_nr_throttled_delta\t%s\n' "$nr_throttled_delta"
  printf 'cgroup_throttled_usec_delta\t%s\n' "$throttled_usec_delta"
  printf 'cgroup_throttled_pct_of_quota\t%s\n' "$throttled_pct_of_quota"
  printf 'host_idle_pct_supplemental\t%s\n' "$host_idle_pct"
  printf 'host_loadavg_supplemental\t%s\n' "$(cut -d' ' -f1-3 /proc/loadavg)"
  printf 'simulator_worker_count\t%s\n' "$worker_count"
  printf 'available_distinct_physical_cores\t%s\n' "$candidate_count"
  printf 'candidate_cpus\t%s\n' "$candidate_cpus"
  printf 'p95_rss_bytes\t%s\n' "$p95_rss"
  printf 'memory_required_bytes\t%s\n' "$memory_required"
  printf 'memavailable_bytes\t%s\n' "$memavailable"
  printf 'memory_current_bytes\t%s\n' "$memory_current"
  printf 'memory_max_bytes\t%s\n' "$memory_max"
  printf 'memory_headroom_bytes\t%s\n' "$memory_headroom"
  printf 'swap_si_delta\t%s\n' "$swap_si_delta"
  printf 'swap_so_delta\t%s\n' "$swap_so_delta"
  printf 'oom_kill_delta\t%s\n' "$oom_kill_delta"
  printf 'memory_psi_avg10\t%s\n' "$psi"
  printf 'expected_output_p95_bytes\t%s\n' "$output_p95"
  printf 'output_required_bytes\t%s\n' "$output_required"
  printf 'output_free_bytes\t%s\n' "$output_free"
  printf 'safe_to_launch\t%s\n' "$safe"
  printf 'authorized_workers\t%s\n' "$([ "$safe" = YES ] && echo 5 || echo 0)"
  printf 'admission_reason\t%s\n' "$reason"
} >"$tmp"
mv -f -- "$tmp" "$output"
printf 'FAST64_R2_CONTINUATION_RESOURCE_AUDIT_WRITTEN\t%s\n' "$output"
