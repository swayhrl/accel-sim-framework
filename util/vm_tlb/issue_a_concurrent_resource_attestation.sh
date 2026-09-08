#!/usr/bin/env bash
set -euo pipefail

pid=""
output="/workspace/m4c-c3-formal-20260905-v1/A_CONCURRENT_RESOURCE_ATTESTATION.txt"
ttl_seconds=1200
sample_seconds=15

usage() {
  cat <<'EOF'
Usage: issue_a_concurrent_resource_attestation.sh --pid PID [--output FILE]
       [--ttl-seconds N] [--sample-seconds N]

Reads only /proc and CPU topology/frequency state. It never modifies process
priority, affinity, cgroups, simulator state, config, or scratch contents other
than replacing/removing the small attestation file named by --output.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --pid) pid="$2"; shift 2 ;;
    --output) output="$2"; shift 2 ;;
    --ttl-seconds) ttl_seconds="$2"; shift 2 ;;
    --sample-seconds) sample_seconds="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "FAIL unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ "$pid" =~ ^[1-9][0-9]*$ ]] || { echo "FAIL --pid required" >&2; exit 2; }
[[ "$ttl_seconds" =~ ^[1-9][0-9]*$ && "$sample_seconds" =~ ^[1-9][0-9]*$ ]] || {
  echo "FAIL invalid ttl/sample" >&2; exit 2;
}

fail() {
  rm -f "$output"
  echo "RESOURCE_DEFERRED $*" >&2
  exit 1
}

[[ -r "/proc/$pid/stat" ]] || fail "A_PID_NOT_FOUND pid=$pid"
mkdir -p "$(dirname "$output")"
rm -f "$output"

mem_field() { awk -v key="$1" '$1 == key {print $2}' /proc/meminfo; }
swap_counters() {
  awk '$1=="pswpin"{i=$2} $1=="pswpout"{o=$2} END{print i+0,o+0}' /proc/vmstat
}
cpu_counters() {
  awk '/^cpu / {total=0; for(i=2;i<=9;i++) total+=$i; print total,$5,$6; exit}' /proc/stat
}
proc_ticks() { awk '{print $14+$15}' "/proc/$pid/stat"; }
proc_state() { awk '{print $3}' "/proc/$pid/stat"; }
proc_cpu() { awk '{print $39}' "/proc/$pid/stat"; }

mem_total=$(mem_field MemTotal:)
mem_available_1=$(mem_field MemAvailable:)
swap_total=$(mem_field SwapTotal:)
swap_free_1=$(mem_field SwapFree:)
[[ -n "$mem_total" && -n "$mem_available_1" && -n "$swap_total" && -n "$swap_free_1" ]] || fail "MEMINFO_PARSE"

min_mem=$((64 * 1024 * 1024))
quarter_mem=$((mem_total / 4))
(( quarter_mem > min_mem )) && min_mem=$quarter_mem
min_swap=$((512 * 1024))
quarter_swap=$((swap_total / 4))
(( quarter_swap > min_swap )) && min_swap=$quarter_swap

(( mem_available_1 >= min_mem )) || fail "MEM_AVAILABLE initial=${mem_available_1} required=${min_mem}"
if (( swap_total > 0 )); then
  (( swap_free_1 >= min_swap )) || fail "SWAP_FREE initial=${swap_free_1} required=${min_swap}"
fi

read -r swapin_1 swapout_1 < <(swap_counters)
read -r total_1 idle_1 iowait_1 < <(cpu_counters)
ticks_1=$(proc_ticks)
state_1=$(proc_state)
cpu_1=$(proc_cpu)
[[ "$state_1" == R || "$state_1" == S || "$state_1" == D ]] || fail "A_BAD_STATE initial=$state_1"

sleep "$sample_seconds"

[[ -r "/proc/$pid/stat" ]] || fail "A_PID_EXITED_DURING_SAMPLE"
mem_available_2=$(mem_field MemAvailable:)
swap_free_2=$(mem_field SwapFree:)
read -r swapin_2 swapout_2 < <(swap_counters)
read -r total_2 idle_2 iowait_2 < <(cpu_counters)
ticks_2=$(proc_ticks)
state_2=$(proc_state)
cpu_2=$(proc_cpu)

(( mem_available_2 >= min_mem )) || fail "MEM_AVAILABLE final=${mem_available_2} required=${min_mem}"
if (( swap_total > 0 )); then
  (( swap_free_2 >= min_swap )) || fail "SWAP_FREE final=${swap_free_2} required=${min_swap}"
fi
(( swapin_2 == swapin_1 && swapout_2 == swapout_1 )) || fail "SWAP_ACTIVITY in=$((swapin_2-swapin_1)) out=$((swapout_2-swapout_1))"
[[ "$state_2" == R || "$state_2" == S || "$state_2" == D ]] || fail "A_BAD_STATE final=$state_2"

cpu_delta=$((total_2 - total_1))
idle_delta=$((idle_2 - idle_1))
iowait_delta=$((iowait_2 - iowait_1))
(( cpu_delta > 0 )) || fail "CPU_SAMPLE_ZERO"
idle_pct=$((100 * idle_delta / cpu_delta))
iowait_pct=$((100 * iowait_delta / cpu_delta))
(( idle_pct >= 8 )) || fail "CPU_IDLE_PCT=${idle_pct}"
(( iowait_pct <= 5 )) || fail "IOWAIT_PCT=${iowait_pct}"

clk_tck=$(getconf CLK_TCK)
tick_delta=$((ticks_2 - ticks_1))
min_ticks=$((clk_tck * sample_seconds / 2))
(( tick_delta >= min_ticks )) || fail "A_CPU_PROGRESS ticks_delta=${tick_delta} required=${min_ticks}"

siblings="UNKNOWN"
if [[ -r "/sys/devices/system/cpu/cpu${cpu_2}/topology/thread_siblings_list" ]]; then
  siblings=$(cat "/sys/devices/system/cpu/cpu${cpu_2}/topology/thread_siblings_list")
fi
cur_freq="UNKNOWN"
max_freq="UNKNOWN"
governor="UNKNOWN"
[[ -r "/sys/devices/system/cpu/cpu${cpu_2}/cpufreq/scaling_cur_freq" ]] && cur_freq=$(cat "/sys/devices/system/cpu/cpu${cpu_2}/cpufreq/scaling_cur_freq")
[[ -r "/sys/devices/system/cpu/cpu${cpu_2}/cpufreq/scaling_max_freq" ]] && max_freq=$(cat "/sys/devices/system/cpu/cpu${cpu_2}/cpufreq/scaling_max_freq")
[[ -r "/sys/devices/system/cpu/cpu${cpu_2}/cpufreq/scaling_governor" ]] && governor=$(cat "/sys/devices/system/cpu/cpu${cpu_2}/cpufreq/scaling_governor")

issued=$(date +%s)
expires=$((issued + ttl_seconds))
tmp="${output}.tmp.$$"
cat > "$tmp" <<EOF
A_CONCURRENT_RESOURCE_GATE_PASS
issued_epoch\t${issued}
expires_epoch\t${expires}
a_pid\t${pid}
a_state\t${state_2}
a_cpu_ticks_delta\t${tick_delta}
a_logical_cpu\t${cpu_2}
a_thread_siblings\t${siblings}
a_scaling_cur_freq_khz\t${cur_freq}
a_scaling_max_freq_khz\t${max_freq}
a_scaling_governor\t${governor}
mem_total_kb\t${mem_total}
mem_available_kb\t${mem_available_2}
mem_required_kb\t${min_mem}
swap_total_kb\t${swap_total}
swap_free_kb\t${swap_free_2}
swap_required_kb\t${min_swap}
swapin_delta\t$((swapin_2-swapin_1))
swapout_delta\t$((swapout_2-swapout_1))
cpu_idle_pct\t${idle_pct}
cpu_iowait_pct\t${iowait_pct}
allowed_b_workers\t1
allowed_c_compile_jobs\t1
scope\tB_E01_CANARY_AND_C10B0_FOCUSED_COMPILE_ONLY
EOF
mv "$tmp" "$output"
echo "PASS A_CONCURRENT_RESOURCE_GATE attestation=$output expires_epoch=$expires"
