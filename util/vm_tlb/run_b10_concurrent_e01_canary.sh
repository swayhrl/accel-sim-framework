#!/usr/bin/env bash
set -euo pipefail

framework_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
core_root=/workspace/worktrees/gpgpu-sim-vm-spec-farm
scratch_root=/workspace/vm-spec-farm
attestation="/workspace/m4c-c3-formal-20260905-v1/A_CONCURRENT_RESOURCE_ATTESTATION.txt"
output_root="${B10_CONCURRENT_ROOT:-$scratch_root/future-evidence/b10-concurrent-e01-canary}"
cpu=""
mode=dry-run
sample_seconds=10
expected_binary=2d6f825faf71e4aa9acc8d62e98186c9d7c1a92ecd2c41cbfd108e918de44915
runner="$framework_root/util/vm_tlb/run_m4c_replay.sh"
validator="$framework_root/util/vm_tlb/validate_b9_execution_pack.py"
pack="$framework_root/docs/vm_tlb/review_packs/VM_SPECULATIVE_EXPERIMENT_FARM/B9_MINIMUM_EXPERIMENT_EXECUTION_PREFLIGHT"
simulator="$framework_root/gpu-simulator/bin/release/accel-sim.out"

usage() {
  cat <<'EOF'
Usage: run_b10_concurrent_e01_canary.sh [--dry-run]
       run_b10_concurrent_e01_canary.sh --enable-execution --cpu LOGICAL_CPU
         [--attestation FILE] [--output-root DIR]

Concurrent mode is limited to E01 generic + PWC32, sequentially. It never
executes E02-E10.
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
  expires=$(attest_field expires_epoch)
  now=$(date +%s)
  allowed=$(attest_field allowed_b_workers)
  a_pid=$(attest_field a_pid)
  siblings=$(attest_field a_thread_siblings)
  [[ "$expires" =~ ^[0-9]+$ && "$now" -lt "$expires" ]] || {
    echo "RESOURCE_DEFERRED stale_attestation" >&2; return 1;
  }
  [[ "$allowed" == 1 ]] || { echo "RESOURCE_DEFERRED b_not_authorized" >&2; return 1; }
  [[ "$a_pid" =~ ^[1-9][0-9]*$ && -r "/proc/$a_pid/stat" ]] || {
    echo "RESOURCE_DEFERRED a_pid_not_alive" >&2; return 1;
  }
  if [[ -n "$cpu" && "$siblings" != UNKNOWN ]]; then
    if echo ",$siblings," | grep -Eq ",${cpu},"; then
      echo "RESOURCE_DEFERRED selected_cpu_is_A_sibling cpu=$cpu siblings=$siblings" >&2
      return 1
    fi
  fi
}

resource_gate() {
  validate_attestation || return 1
  local mem_total mem_available_1 mem_available_2 swap_total swap_free_1 swap_free_2
  local min_mem quarter_mem min_swap quarter_swap si1 so1 si2 so2 t1 id1 iw1 t2 id2 iw2
  local delta idle_pct iowait_pct a_pid ticks1 ticks2 clk min_ticks
  mem_total=$(mem_field MemTotal:)
  mem_available_1=$(mem_field MemAvailable:)
  swap_total=$(mem_field SwapTotal:)
  swap_free_1=$(mem_field SwapFree:)
  min_mem=$((64 * 1024 * 1024)); quarter_mem=$((mem_total/4)); (( quarter_mem > min_mem )) && min_mem=$quarter_mem
  min_swap=$((512 * 1024)); quarter_swap=$((swap_total/4)); (( quarter_swap > min_swap )) && min_swap=$quarter_swap
  (( mem_available_1 >= min_mem )) || { echo "RESOURCE_DEFERRED mem_available=${mem_available_1}" >&2; return 1; }
  if (( swap_total > 0 )); then (( swap_free_1 >= min_swap )) || { echo "RESOURCE_DEFERRED swap_free=${swap_free_1}" >&2; return 1; }; fi
  read -r si1 so1 < <(swap_counters)
  read -r t1 id1 iw1 < <(cpu_counters)
  a_pid=$(attest_field a_pid)
  ticks1=$(proc_ticks "$a_pid")
  sleep "$sample_seconds"
  validate_attestation || return 1
  mem_available_2=$(mem_field MemAvailable:)
  swap_free_2=$(mem_field SwapFree:)
  read -r si2 so2 < <(swap_counters)
  read -r t2 id2 iw2 < <(cpu_counters)
  ticks2=$(proc_ticks "$a_pid")
  (( mem_available_2 >= min_mem )) || { echo "RESOURCE_DEFERRED mem_after=${mem_available_2}" >&2; return 1; }
  if (( swap_total > 0 )); then (( swap_free_2 >= min_swap )) || { echo "RESOURCE_DEFERRED swap_after=${swap_free_2}" >&2; return 1; }; fi
  (( si2 == si1 && so2 == so1 )) || { echo "RESOURCE_DEFERRED swap_activity" >&2; return 1; }
  delta=$((t2-t1)); (( delta > 0 )) || return 1
  idle_pct=$((100*(id2-id1)/delta)); iowait_pct=$((100*(iw2-iw1)/delta))
  (( idle_pct >= 8 )) || { echo "RESOURCE_DEFERRED idle_pct=${idle_pct}" >&2; return 1; }
  (( iowait_pct <= 5 )) || { echo "RESOURCE_DEFERRED iowait_pct=${iowait_pct}" >&2; return 1; }
  clk=$(getconf CLK_TCK); min_ticks=$((clk*sample_seconds/2))
  (( ticks2-ticks1 >= min_ticks )) || { echo "RESOURCE_DEFERRED A_cpu_progress" >&2; return 1; }
  echo "RESOURCE_PASS mem_kb=$mem_available_2 swap_kb=$swap_free_2 idle_pct=$idle_pct iowait_pct=$iowait_pct A_ticks_delta=$((ticks2-ticks1))"
}

static_validate() {
  python3 "$validator" \
    --manifest "$pack/E01_E10_EXECUTION_MANIFEST.tsv" \
    --whitelist "$pack/ARM_DELTA_WHITELIST.tsv" \
    --selector "$pack/B9_MATCHED_16_KERNEL_SELECTOR.md"
  [[ "$(sha256sum "$simulator" | awk '{print $1}')" == "$expected_binary" ]] || {
    echo "FAIL simulator SHA-256 mismatch" >&2; exit 2;
  }
}

run_arm() {
  local arm="$1" profile="$2" extra="$3" out="$output_root/$arm"
  resource_gate
  [[ ! -e "$out" ]] || { echo "FAIL existing evidence $out" >&2; exit 2; }
  local cmd=("$runner" --framework-root "$framework_root" --core-root "$core_root" --simulator "$simulator" --roi decode1 --profile "$profile" --trace-list "$scratch_root/inputs/semantic-rebuilt/decode1/compute-only-kernelslist.g" --trace-dir "$scratch_root/staging/llama-f96b7ea9-5bdd4b55/decode1/m4a-llama-decode1-20260903T004138Z/traces" --run-dir "$out" --max-kernels 1 --telemetry-level 3 --window-transactions 1000000)
  [[ "$extra" == NONE ]] || cmd+=(--extra-config "$extra")
  printf 'RUN %s cpu=%s\n' "$arm" "$cpu"
  ionice -c2 -n7 nice -n 10 taskset -c "$cpu" "${cmd[@]}"
}

static_validate
if [[ "$mode" == dry-run ]]; then
  echo "PASS B10_CONCURRENT_E01_DRY_RUN_ONLY"
  echo "E01-generic -> generic, one kernel"
  echo "E01-pwc32 -> generic + b2-pwc-finite32.config, one kernel"
  exit 0
fi

[[ "$cpu" =~ ^[0-9]+$ && -d "/sys/devices/system/cpu/cpu${cpu}" ]] || { echo "FAIL --cpu required" >&2; exit 2; }
validate_attestation
mkdir -p "$output_root"
[[ -z "$(find "$output_root" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]] || { echo "FAIL output root not empty" >&2; exit 2; }

run_arm E01-generic generic NONE
run_arm E01-pwc32 generic "$scratch_root/configs/b2/b2-pwc-finite32.config"
resource_gate
cat > "$output_root/CANARY_COMPLETE.tsv" <<EOF
field\tvalue
status\tB10_CONCURRENT_E01_CANARY_COMPLETE
completed_arms\tE01-generic,E01-pwc32
cpu\t${cpu}
attestation\t${attestation}
completed_epoch\t$(date +%s)
EOF
echo "PASS B10_CONCURRENT_E01_CANARY_COMPLETE; STOP before E02-E10"
