#!/usr/bin/env bash
set -euo pipefail

framework_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
core_root=/workspace/worktrees/gpgpu-sim-vm-m4b-speculative
attestation="/workspace/m4c-c3-formal-20260905-v1/A_CONCURRENT_RESOURCE_ATTESTATION.txt"
output_root="${C10B0_CONCURRENT_ROOT:-/workspace/vm-m4b-speculative/c10b0-concurrent-compile-canary}"
cpu=""
mode=dry-run
sample_seconds=10
expected_core=12267bb7ed1dc0257d1d903f6baf7cbdc6ca550e

usage() {
  cat <<'EOF'
Usage: run_c10b0_concurrent_compile_canary.sh [--dry-run]
       run_c10b0_concurrent_compile_canary.sh --enable-execution --cpu LOGICAL_CPU
         [--attestation FILE] [--output-root DIR]

Only two direct translation-model unit targets are compiled/run. No full build
or simulator workload is started.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) mode=dry-run; shift ;;
    --enable-execution) mode=execute; shift ;;
    --cpu) cpu="$2"; shift 2 ;;
    --attestation) attestation="$2"; shift 2 ;;
    --output-root) output_root="$2"; shift 2 ;;
    --sample-seconds) sample_seconds="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "FAIL unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

attest_field() { awk -F '\t' -v key="$1" '$1==key {print $2; exit}' "$attestation"; }
mem_field() { awk -v key="$1" '$1==key {print $2}' /proc/meminfo; }
swap_counters() { awk '$1=="pswpin"{i=$2} $1=="pswpout"{o=$2} END{print i+0,o+0}' /proc/vmstat; }
cpu_counters() { awk '/^cpu / {t=0; for(i=2;i<=9;i++) t+=$i; print t,$5,$6; exit}' /proc/stat; }
proc_ticks() { awk '{print $14+$15}' "/proc/$1/stat"; }

validate_attestation() {
  [[ -f "$attestation" ]] || { echo "RESOURCE_DEFERRED missing_attestation" >&2; return 1; }
  [[ "$(head -n1 "$attestation")" == "A_CONCURRENT_RESOURCE_GATE_PASS" ]] || {
    echo "RESOURCE_DEFERRED wrong_attestation_type" >&2; return 1;
  }
  local expires now allowed a_pid siblings
  expires=$(attest_field expires_epoch); now=$(date +%s)
  allowed=$(attest_field allowed_c_compile_jobs); a_pid=$(attest_field a_pid)
  siblings=$(attest_field a_thread_siblings)
  [[ "$expires" =~ ^[0-9]+$ && "$now" -lt "$expires" ]] || { echo "RESOURCE_DEFERRED stale_attestation" >&2; return 1; }
  [[ "$allowed" == 1 ]] || { echo "RESOURCE_DEFERRED c_compile_not_authorized" >&2; return 1; }
  [[ "$a_pid" =~ ^[1-9][0-9]*$ && -r "/proc/$a_pid/stat" ]] || { echo "RESOURCE_DEFERRED a_pid_not_alive" >&2; return 1; }
  if [[ -n "$cpu" && "$siblings" != UNKNOWN ]]; then
    if echo ",$siblings," | grep -Eq ",${cpu},"; then
      echo "RESOURCE_DEFERRED selected_cpu_is_A_sibling cpu=$cpu siblings=$siblings" >&2
      return 1
    fi
  fi
}

resource_gate() {
  validate_attestation || return 1
  local mem_total mem1 mem2 swap_total swap1 swap2 min_mem qmem min_swap qswap
  local si1 so1 si2 so2 t1 id1 iw1 t2 id2 iw2 delta idle_pct iowait_pct
  local a_pid ticks1 ticks2 clk min_ticks
  mem_total=$(mem_field MemTotal:); mem1=$(mem_field MemAvailable:)
  swap_total=$(mem_field SwapTotal:); swap1=$(mem_field SwapFree:)
  min_mem=$((64*1024*1024)); qmem=$((mem_total/4)); (( qmem > min_mem )) && min_mem=$qmem
  min_swap=$((512*1024)); qswap=$((swap_total/4)); (( qswap > min_swap )) && min_swap=$qswap
  (( mem1 >= min_mem )) || { echo "RESOURCE_DEFERRED mem=${mem1}" >&2; return 1; }
  if (( swap_total > 0 )); then (( swap1 >= min_swap )) || { echo "RESOURCE_DEFERRED swap=${swap1}" >&2; return 1; }; fi
  read -r si1 so1 < <(swap_counters); read -r t1 id1 iw1 < <(cpu_counters)
  a_pid=$(attest_field a_pid); ticks1=$(proc_ticks "$a_pid")
  sleep "$sample_seconds"
  validate_attestation || return 1
  mem2=$(mem_field MemAvailable:); swap2=$(mem_field SwapFree:)
  read -r si2 so2 < <(swap_counters); read -r t2 id2 iw2 < <(cpu_counters)
  ticks2=$(proc_ticks "$a_pid")
  (( mem2 >= min_mem )) || { echo "RESOURCE_DEFERRED mem_after=${mem2}" >&2; return 1; }
  if (( swap_total > 0 )); then (( swap2 >= min_swap )) || { echo "RESOURCE_DEFERRED swap_after=${swap2}" >&2; return 1; }; fi
  (( si2 == si1 && so2 == so1 )) || { echo "RESOURCE_DEFERRED swap_activity" >&2; return 1; }
  delta=$((t2-t1)); (( delta > 0 )) || return 1
  idle_pct=$((100*(id2-id1)/delta)); iowait_pct=$((100*(iw2-iw1)/delta))
  (( idle_pct >= 8 )) || { echo "RESOURCE_DEFERRED idle_pct=${idle_pct}" >&2; return 1; }
  (( iowait_pct <= 5 )) || { echo "RESOURCE_DEFERRED iowait_pct=${iowait_pct}" >&2; return 1; }
  clk=$(getconf CLK_TCK); min_ticks=$((clk*sample_seconds/2))
  (( ticks2-ticks1 >= min_ticks )) || { echo "RESOURCE_DEFERRED A_cpu_progress" >&2; return 1; }
  echo "RESOURCE_PASS mem_kb=$mem2 swap_kb=$swap2 idle_pct=$idle_pct iowait_pct=$iowait_pct A_ticks_delta=$((ticks2-ticks1))"
}

compile_one() {
  local source="$1" binary="$2" log="$3"
  resource_gate
  (
    cd "$core_root"
    ionice -c2 -n7 nice -n 10 taskset -c "$cpu" \
      g++ -std=c++11 -Isrc "$source" src/gpgpu-sim/vm_translation.cc -o "$binary"
  ) >"$log" 2>&1
}

run_one() {
  local binary="$1" log="$2"
  resource_gate
  ionice -c2 -n7 nice -n 10 taskset -c "$cpu" "$binary" >"$log" 2>&1
}

if [[ "$mode" == dry-run ]]; then
  echo "PASS C10B0_CONCURRENT_DRY_RUN_ONLY"
  echo "Core expected=$expected_core"
  echo "Targets: vm_c10a2_static_model_test.cc, vm_c10a_registered_segment_test.cc"
  exit 0
fi

[[ "$cpu" =~ ^[0-9]+$ && -d "/sys/devices/system/cpu/cpu${cpu}" ]] || { echo "FAIL --cpu required" >&2; exit 2; }
validate_attestation
[[ "$(git -C "$core_root" rev-parse HEAD)" == "$expected_core" ]] || {
  echo "FAIL Core HEAD mismatch: $(git -C "$core_root" rev-parse HEAD)" >&2; exit 2;
}
[[ -z "$(git -C "$core_root" status --porcelain)" ]] || { echo "FAIL Core worktree not clean" >&2; exit 2; }
mkdir -p "$output_root"
[[ -z "$(find "$output_root" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]] || { echo "FAIL output root not empty" >&2; exit 2; }

static_bin="$output_root/vm_c10a2_static_model_test"
registered_bin="$output_root/vm_c10a_registered_segment_test"
compile_one tests/vm_c10a2_static_model_test.cc "$static_bin" "$output_root/compile_static.log"
compile_one tests/vm_c10a_registered_segment_test.cc "$registered_bin" "$output_root/compile_registered.log"
run_one "$static_bin" "$output_root/run_static.log"
run_one "$registered_bin" "$output_root/run_registered.log"
resource_gate

cat > "$output_root/CANARY_COMPLETE.tsv" <<EOF
field\tvalue
status\tC10B0_CONCURRENT_FOCUSED_CANARY_PASS
core_head\t$expected_core
cpu\t$cpu
attestation\t$attestation
completed_epoch\t$(date +%s)
EOF
echo "PASS C10B0_CONCURRENT_FOCUSED_CANARY_PASS; STOP before full build/regression"
