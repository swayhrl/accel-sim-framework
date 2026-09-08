#!/usr/bin/env bash
# Future-only B9 E01--E10 executor. Default is static dry-run; execution needs
# both --enable-execution and an external A-terminal attestation.
set -euo pipefail

framework_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
core_root=/workspace/worktrees/gpgpu-sim-vm-spec-farm
scratch_root=/workspace/vm-spec-farm
pack="$framework_root/docs/vm_tlb/review_packs/VM_SPECULATIVE_EXPERIMENT_FARM/B9_MINIMUM_EXPERIMENT_EXECUTION_PREFLIGHT"
manifest="$pack/E01_E10_EXECUTION_MANIFEST.tsv"
whitelist="$pack/ARM_DELTA_WHITELIST.tsv"
selector_doc="$pack/B9_MATCHED_16_KERNEL_SELECTOR.md"
runner="$framework_root/util/vm_tlb/run_m4c_replay.sh"
miner="$framework_root/util/vm_tlb/analyze_spec_farm_traces.py"
selector="$framework_root/util/vm_tlb/select_b9_matched_kernels.py"
validator="$framework_root/util/vm_tlb/validate_b9_execution_pack.py"
simulator="$framework_root/gpu-simulator/bin/release/accel-sim.out"
expected_binary=2d6f825faf71e4aa9acc8d62e98186c9d7c1a92ecd2c41cbfd108e918de44915
future_root="${B9_FUTURE_EVIDENCE_ROOT:-$scratch_root/future-evidence/b9-e01-e10}"
mode=dry-run
experiments=ALL
attestation=""
resume_valid=0
arms=ALL

usage() {
  cat <<'EOF'
Usage: run_b9_e01_e10_after_a_terminal.sh [--dry-run] [--experiment E01,...]
       run_b9_e01_e10_after_a_terminal.sh --enable-execution \
         --a-terminal-attestation FILE [--experiment E01,...] [--arm ARM,...] [--resume-valid]

Dry-run is the default and only performs static validation plus command
rendering. Execution is intentionally opt-in, sequential (effective
concurrency=1), refuses pre-existing output, and checks resource pressure
before every job. It never turns a stateful continuous ROI into per-kernel
processes; B9 E01--E06 are explicitly one-kernel smoke experiments only.

--resume-valid is for the B11 supervisor only.  It skips an existing simulator
arm only after checking its recorded zero exit status, exactly one kernel, and
the telemetry schema marker.  Incomplete or otherwise invalid evidence still
refuses execution and must be quarantined by the supervisor first.

--arm restricts an E01--E06 invocation to an exact manifest arm.  It is used
only by B11 so that each simulator run gets its own external ten-second
resource gate and shared heavy-slot lock.  It is rejected for miner tasks.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) mode=dry-run; shift ;;
    --enable-execution) mode=execute; shift ;;
    --experiment) experiments="$2"; shift 2 ;;
    --arm) arms="$2"; shift 2 ;;
    --a-terminal-attestation) attestation="$2"; shift 2 ;;
    --resume-valid) resume_valid=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "FAIL unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

static_validate() {
  python3 "$validator" --manifest "$manifest" --whitelist "$whitelist" --selector "$selector_doc"
  [[ "$(sha256sum "$simulator" | awk '{print $1}')" == "$expected_binary" ]] || {
    echo "FAIL simulator SHA-256 mismatch" >&2; exit 2;
  }
}

selected() {
  [[ "$experiments" == ALL ]] && return 0
  [[ ",$experiments," == *",$1,"* ]]
}

arm_selected() {
  [[ "$arms" == ALL ]] && return 0
  [[ ",$arms," == *",$1,"* ]]
}

proc_field() { awk -v key="$1" '$1 == key {print $2}' "$2"; }
cpu_iowait() { awk 'NR==1 {print $6, $2+$3+$4+$5+$6+$7+$8+$9+$10}' /proc/stat; }

resource_gate() {
  # The B11 supervisor performs the authoritative 10-second B11 gate before
  # acquiring its per-arm shared heavy slot.  Avoid a second legacy sleep while
  # that lock is held, but retain the original gate for direct B9 use.
  if [[ "${B9_EXTERNAL_RESOURCE_GATE:-0}" == 1 ]]; then
    echo "PASS B9 external B11 resource gate accepted"
    return 0
  fi
  local mem_total mem_available normal_required sw1 sw2 si1 so1 si2 so2 iw1 total1 iw2 total2 iowait
  mem_total=$(proc_field MemTotal: /proc/meminfo)
  mem_available=$(proc_field MemAvailable: /proc/meminfo)
  normal_required=$((mem_total / 5 + 4 * 1024 * 1024))
  if [[ -n "${B9_CALIBRATED_PEAK_KB:-}" ]]; then
    [[ "$B9_CALIBRATED_PEAK_KB" =~ ^[1-9][0-9]*$ && "${B9_MEMORY_SPAN_KB:-0}" =~ ^[0-9]+$ ]] || {
      echo "FAIL invalid calibrated resource inputs" >&2; return 1;
    }
    local calibrated=$((4 * B9_CALIBRATED_PEAK_KB))
    local swing=$((B9_MEMORY_SPAN_KB + 2 * B9_CALIBRATED_PEAK_KB))
    (( swing > calibrated )) && calibrated=$swing
    (( calibrated > normal_required )) && normal_required=$calibrated
  fi
  (( mem_available >= normal_required )) || { echo "RESOURCE_DEFERRED MemAvailable=${mem_available}KB required=${normal_required}KB" >&2; return 1; }
  read -r si1 so1 < <(awk '$1=="pswpin"{i=$2} $1=="pswpout"{o=$2} END{print i+0,o+0}' /proc/vmstat)
  read -r iw1 total1 < <(cpu_iowait)
  sleep 5
  mem_available=$(proc_field MemAvailable: /proc/meminfo)
  read -r si2 so2 < <(awk '$1=="pswpin"{i=$2} $1=="pswpout"{o=$2} END{print i+0,o+0}' /proc/vmstat)
  read -r iw2 total2 < <(cpu_iowait)
  (( mem_available >= normal_required && si2 == si1 && so2 == so1 )) || { echo "RESOURCE_DEFERRED persistent_swap_or_memory_pressure" >&2; return 1; }
  iowait=$((100 * (iw2 - iw1) / ((total2 - total1) + 1)))
  (( iowait <= 15 )) || { echo "RESOURCE_DEFERRED iowait_pct=${iowait}" >&2; return 1; }
}

require_execute_gate() {
  [[ "$mode" == execute ]] || return 0
  [[ -n "$attestation" && -f "$attestation" ]] || { echo "FAIL explicit A-terminal attestation required" >&2; exit 2; }
  grep -qx 'A_TERMINAL_CONFIRMED' "$attestation" || { echo "FAIL invalid A-terminal attestation" >&2; exit 2; }
  mkdir -p "$future_root"
}

run_sim() {
  # With set -u, do not refer to arm in the same local declaration that
  # initializes it: bash expands the complete declaration before assigning.
  local arm=$1 profile=$2 extra=$3
  local out="$future_root/$arm"
  local trace_file="$scratch_root/staging/llama-f96b7ea9-5bdd4b55/decode1/m4a-llama-decode1-20260903T004138Z/traces/kernel-1464-ctx_0x55d98da1ddf0.traceg.xz"
  resource_gate
  if [[ -e "$out" ]]; then
    if (( resume_valid )) && [[ -f "$out/RUN_MANIFEST.tsv" && -f "$out/run.log" ]] &&
       grep -q $'^simulator_exit_status\t0$' "$out/RUN_MANIFEST.tsv" &&
       [[ "$(grep -c '^Processing kernel ' "$out/run.log")" -eq 1 ]] &&
       grep -q '^m4c_telemetry_schema =' "$out/run.log"; then
      echo "SKIP_VALID arm=$arm"
      return 0
    fi
    echo "FAIL existing non-resumable arm evidence: $arm" >&2
    exit 2
  fi
  [[ ! -e "$future_root/$arm.PRELAUNCH.tsv" ]] || { echo "FAIL existing prelaunch evidence: $arm" >&2; exit 2; }
  local command=("$runner" --framework-root "$framework_root" --core-root "$core_root" --simulator "$simulator" --roi decode1 --profile "$profile" --trace-list "$scratch_root/inputs/semantic-rebuilt/decode1/compute-only-kernelslist.g" --trace-dir "$scratch_root/staging/llama-f96b7ea9-5bdd4b55/decode1/m4a-llama-decode1-20260903T004138Z/traces" --run-dir "$out" --max-kernels 1 --telemetry-level 3 --window-transactions 1000000)
  [[ "$extra" == NONE ]] || command+=(--extra-config "$extra")
  { printf 'field\tvalue\n'; printf 'arm_id\t%s\n' "$arm"; printf 'command\t'; printf '%q ' "${command[@]}"; printf '\n'; printf 'command_sha256\t'; printf '%q ' "${command[@]}" | sha256sum | awk '{print $1}'; printf 'binary_sha256\t%s\n' "$expected_binary"; sha256sum "$trace_file" "$scratch_root/inputs/semantic-rebuilt/decode1/compute-only-kernelslist.g" "$runner"; } > "$future_root/$arm.PRELAUNCH.tsv"
  if [[ -n "${B9_TIME_V_OUTPUT:-}" ]]; then
    [[ ! -e "$B9_TIME_V_OUTPUT" ]] || { echo "FAIL existing time-v evidence: $B9_TIME_V_OUTPUT" >&2; exit 2; }
    /usr/bin/time -v -o "$B9_TIME_V_OUTPUT" "${command[@]}"
  else
    "${command[@]}"
  fi
}

run_miner() {
  local arm=$1 roi=$2 filename=$3 trace_dir=$4 object_map=$5 selected="$future_root/$arm.kernelslist.g" out="$future_root/$arm"
  resource_gate
  [[ ! -e "$out" && ! -e "$selected" && ! -e "$future_root/$arm.time-v.txt" ]] || { echo "FAIL existing miner evidence: $arm" >&2; exit 2; }
  printf '%s\n' "$filename" > "$selected"
  /usr/bin/time -v -o "$future_root/$arm.time-v.txt" python3 "$miner" --roi "$roi" --trace-list "$selected" --trace-dir "$trace_dir" --object-map "$object_map" --output-dir "$out" --workers 1 --sample-stride 1024 --partials-only
  [[ -s "$out/partials/00000.pkl.xz" ]] || { echo "FAIL calibration integrity" >&2; exit 2; }
}

run_static16() {
  local arm=$1 roi=$2 trace_list=$3 trace_dir=$4 object_map=$5 prerequisite=$6 out="$future_root/$arm" selected="$future_root/$arm.kernelslist.g" selector_out="$future_root/B9_MATCHED_16_SELECTOR.tsv"
  [[ -n "${B9_CALIBRATED_PEAK_KB:-}" && -n "${B9_MEMORY_SPAN_KB:-}" ]] || { echo "FAIL calibrated peak/span required for $arm" >&2; exit 2; }
  resource_gate
  [[ -s "$prerequisite/partials/00000.pkl.xz" ]] || { echo "FAIL prerequisite calibration missing: $prerequisite" >&2; exit 2; }
  [[ ! -e "$out" && ! -e "$selected" && ! -e "$future_root/$arm.time-v.txt" ]] || { echo "FAIL existing static-mining evidence: $arm" >&2; exit 2; }
  if [[ ! -e "$selector_out" ]]; then
    python3 "$selector" --output "$selector_out" --prefill-list "$scratch_root/inputs/semantic-rebuilt/prefill/compute-only-kernelslist.g" --prefill-trace-dir "$scratch_root/staging/llama-f96b7ea9-5bdd4b55/prefill/m4a-llama-prefill-20260902T182016Z/traces" --decode-list "$scratch_root/inputs/semantic-rebuilt/decode1/compute-only-kernelslist.g" --decode-trace-dir "$scratch_root/staging/llama-f96b7ea9-5bdd4b55/decode1/m4a-llama-decode1-20260903T004138Z/traces"
  fi
  awk -F '\t' -v wanted="$roi" 'NR > 1 && $1 == wanted {print $9}' "$selector_out" > "$selected"
  [[ "$(wc -l < "$selected")" -eq 16 ]] || { echo "FAIL selector cardinality for $roi" >&2; exit 2; }
  /usr/bin/time -v -o "$future_root/$arm.time-v.txt" python3 "$miner" --roi "$roi" --trace-list "$selected" --trace-dir "$trace_dir" --object-map "$object_map" --output-dir "$out" --workers 1 --sample-stride 1024
  grep -q $'lane_references_by_object\t.*\tPASS' "$out/TRACE_MINING_CONSERVATION.tsv" || { echo "FAIL static-mining conservation" >&2; exit 2; }
}

render() {
  awk -F '\t' 'NR==1 || $1 ~ /^E0([1-9]|10)$/ {print}' "$manifest"
}

static_validate
if [[ "$arms" != ALL ]]; then
  [[ "$experiments" != ALL ]] || { echo "FAIL --arm requires one --experiment" >&2; exit 2; }
  case ",$arms," in
    *,E01-generic,*|*,E01-pwc32,*|*,E02-generic,*|*,E02-pwc512,*|*,E03-generic,*|*,E03-pwcideal,*|*,E04-generic64k,*|*,E04-page2mb,*|*,E05-generic,*|*,E05-disabled,*|*,E06-generic,*|*,E06-ideal,*) ;;
    *) echo "FAIL --arm only accepts exact E01--E06 simulator arms" >&2; exit 2 ;;
  esac
  [[ ",${arms}," == *",${experiments}-"* ]] || { echo "FAIL --arm is not part of --experiment" >&2; exit 2; }
fi
if [[ "$mode" == dry-run ]]; then
  echo "PASS B9_DRY_RUN_ONLY effective_concurrency=1 no_simulator_or_worker_started"
  render
  exit 0
fi
require_execute_gate
selected E01 && { arm_selected E01-generic && run_sim E01-generic generic NONE; arm_selected E01-pwc32 && run_sim E01-pwc32 generic "$scratch_root/configs/b2/b2-pwc-finite32.config"; }
selected E02 && { arm_selected E02-generic && run_sim E02-generic generic NONE; arm_selected E02-pwc512 && run_sim E02-pwc512 generic "$scratch_root/configs/b2/b2-pwc-finite512.config"; }
selected E03 && { arm_selected E03-generic && run_sim E03-generic generic NONE; arm_selected E03-pwcideal && run_sim E03-pwcideal generic "$scratch_root/configs/b2/b2-pwc-ideal.config"; }
selected E04 && { arm_selected E04-generic64k && run_sim E04-generic64k generic NONE; arm_selected E04-page2mb && run_sim E04-page2mb generic "$scratch_root/configs/b2/b2-page-2mb-diagnostic.config"; }
selected E05 && { arm_selected E05-generic && run_sim E05-generic generic NONE; arm_selected E05-disabled && run_sim E05-disabled disabled NONE; }
selected E06 && { arm_selected E06-generic && run_sim E06-generic generic NONE; arm_selected E06-ideal && run_sim E06-ideal ideal NONE; }
selected E07 && run_miner E07-decode-rss decode1 kernel-1464-ctx_0x55d98da1ddf0.traceg.xz "$scratch_root/staging/llama-f96b7ea9-5bdd4b55/decode1/m4a-llama-decode1-20260903T004138Z/traces" "$framework_root/configs/vm_tlb/object_maps/M4C_DECODE1_OBJECT_MAP.tsv"
selected E08 && run_miner E08-prefill-rss prefill kernel-735-ctx_0x55f2413c4de0.traceg.xz "$scratch_root/staging/llama-f96b7ea9-5bdd4b55/prefill/m4a-llama-prefill-20260902T182016Z/traces" "$framework_root/configs/vm_tlb/object_maps/M4C_PREFILL_OBJECT_MAP.tsv"
selected E09 && run_static16 E09-prefill-static16 prefill "$scratch_root/inputs/semantic-rebuilt/prefill/compute-only-kernelslist.g" "$scratch_root/staging/llama-f96b7ea9-5bdd4b55/prefill/m4a-llama-prefill-20260902T182016Z/traces" "$framework_root/configs/vm_tlb/object_maps/M4C_PREFILL_OBJECT_MAP.tsv" "$future_root/E08-prefill-rss"
selected E10 && run_static16 E10-decode-static16 decode1 "$scratch_root/inputs/semantic-rebuilt/decode1/compute-only-kernelslist.g" "$scratch_root/staging/llama-f96b7ea9-5bdd4b55/decode1/m4a-llama-decode1-20260903T004138Z/traces" "$framework_root/configs/vm_tlb/object_maps/M4C_DECODE1_OBJECT_MAP.tsv" "$future_root/E07-decode-rss"
echo "PASS B9 execution package completed selected=$experiments"
