#!/usr/bin/env bash
# Assemble an immutable-input M4C/M4B replay in a fresh scratch directory.
# It never writes to the archive, staged trace directory, object-map source, or
# either integration checkout except for the requested scratch run directory.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: run_m4c_replay.sh --framework-root DIR --core-root DIR --simulator PATH \
  --roi {prefill|decode1} --profile {disabled|ideal|generic|paper} \
  --trace-list LIST --trace-dir DIR --run-dir DIR [--max-kernels N] \
  [--telemetry-level {0|1|2|3}] [--window-transactions N]

The trace list must be one of the immutable semantic policy derivatives.  A
fresh `traces/` directory of symlinks is made below RUN-DIR so bounded and full
replays cannot alter the staged formal trace tree.
EOF
}

framework_root=""
core_root=""
simulator=""
roi=""
profile=""
trace_list=""
trace_dir=""
run_dir=""
max_kernels=0
telemetry_level=2
window_transactions=1000000
while [[ $# -gt 0 ]]; do
  case "$1" in
    --framework-root) framework_root="$2"; shift 2 ;;
    --core-root) core_root="$2"; shift 2 ;;
    --simulator) simulator="$2"; shift 2 ;;
    --roi) roi="$2"; shift 2 ;;
    --profile) profile="$2"; shift 2 ;;
    --trace-list) trace_list="$2"; shift 2 ;;
    --trace-dir) trace_dir="$2"; shift 2 ;;
    --run-dir) run_dir="$2"; shift 2 ;;
    --max-kernels) max_kernels="$2"; shift 2 ;;
    --telemetry-level) telemetry_level="$2"; shift 2 ;;
    --window-transactions) window_transactions="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -n "$framework_root" && -n "$core_root" && -x "$simulator" && -n "$roi" && -n "$profile" && -f "$trace_list" && -d "$trace_dir" && -n "$run_dir" ]] || {
  usage >&2; exit 2;
}
[[ "$roi" == prefill || "$roi" == decode1 ]] || { echo "invalid ROI" >&2; exit 2; }
[[ "$profile" == disabled || "$profile" == ideal || "$profile" == generic || "$profile" == paper ]] || { echo "invalid profile" >&2; exit 2; }
[[ "$telemetry_level" =~ ^[0-3]$ ]] || { echo "invalid telemetry level" >&2; exit 2; }
[[ "$max_kernels" =~ ^[0-9]+$ && "$window_transactions" =~ ^[1-9][0-9]*$ ]] || { echo "invalid bounded-run parameter" >&2; exit 2; }
[[ ! -e "$run_dir" ]] || { echo "run directory already exists: $run_dir" >&2; exit 2; }

case "$roi" in
  prefill) object_map="$framework_root/configs/vm_tlb/object_maps/M4C_PREFILL_OBJECT_MAP.tsv" ;;
  decode1) object_map="$framework_root/configs/vm_tlb/object_maps/M4C_DECODE1_OBJECT_MAP.tsv" ;;
esac
case "$profile" in
  disabled) profile_config="$framework_root/configs/vm_tlb/M4C_CONTROL_VM_DISABLED.config" ;;
  ideal) profile_config="$framework_root/configs/vm_tlb/M4C_CONTROL_VM_IDEAL_IDENTITY.config" ;;
  generic) profile_config="$framework_root/configs/vm_tlb/M4C_GENERIC_M3_LLM_BASELINE.config" ;;
  paper) profile_config="$framework_root/configs/vm_tlb/M4C_PAPER_PLATFORM_SHELL_NO_SUBENTRY.config" ;;
esac
base_config="$core_root/configs/tested-cfgs/SM86_RTX3070/gpgpusim.config"
trace_config="$framework_root/gpu-simulator/configs/tested-cfgs/SM86_RTX3070/trace.config"
for input in "$object_map" "$profile_config" "$base_config" "$trace_config"; do
  [[ -f "$input" ]] || { echo "missing immutable input: $input" >&2; exit 2; }
done

# Trace replay must bind to the locally built simulator runtime, never to a
# host CUDA libcudart with the same SONAME.  That binding is part of the run
# provenance and makes this launcher safe to invoke from a fresh shell.
sim_runtime=$(find "$core_root/lib" -type f -path '*/release/libcudart.so' -print -quit)
[[ -n "$sim_runtime" ]] || {
  echo "missing locally built simulator runtime below: $core_root/lib" >&2
  exit 2
}
export LD_LIBRARY_PATH="$(dirname "$sim_runtime"):${LD_LIBRARY_PATH:-}"

mkdir -p "$run_dir/traces"
selected_list="$run_dir/traces/kernelslist.g"
if [[ "$max_kernels" -eq 0 ]]; then
  cp --reflink=auto "$trace_list" "$selected_list"
else
  head -n "$max_kernels" "$trace_list" > "$selected_list"
fi
[[ -s "$selected_list" ]] || { echo "selected trace list is empty" >&2; exit 2; }
while IFS= read -r trace_name; do
  [[ "$trace_name" =~ ^[A-Za-z0-9._-]+\.traceg\.xz$ ]] || {
    echo "unsafe/unexpected trace-list entry: $trace_name" >&2; exit 2;
  }
  [[ -f "$trace_dir/$trace_name" ]] || { echo "missing trace: $trace_name" >&2; exit 2; }
  ln -s "$trace_dir/$trace_name" "$run_dir/traces/$trace_name"
done < "$selected_list"

cat "$base_config" "$trace_config" "$profile_config" > "$run_dir/gpgpusim.config"
printf '%s\n' "-gpgpu_vm_object_map $object_map" \
  "-gpgpu_memory_telemetry_level $telemetry_level" \
  "-gpgpu_memory_telemetry_window_transactions $window_transactions" \
  >> "$run_dir/gpgpusim.config"

{
  printf 'field\tvalue\n'
  printf 'roi\t%s\n' "$roi"
  printf 'profile\t%s\n' "$profile"
  printf 'telemetry_level\t%s\n' "$telemetry_level"
  printf 'window_transactions\t%s\n' "$window_transactions"
  printf 'max_kernels\t%s\n' "$max_kernels"
  printf 'framework_head\t%s\n' "$(git -C "$framework_root" rev-parse HEAD)"
  printf 'core_head\t%s\n' "$(git -C "$core_root" rev-parse HEAD)"
  sha256sum "$base_config" "$trace_config" "$profile_config" "$object_map" "$trace_list" "$selected_list" "$run_dir/gpgpusim.config" |
    awk '{print "sha256:" $2 "\t" $1}'
} > "$run_dir/RUN_MANIFEST.tsv"

set +e
/usr/bin/time -f 'WALL_SECONDS=%e RSS_KB=%M' \
  "$simulator" -config "$run_dir/gpgpusim.config" -trace "$selected_list" \
  2>&1 | tee "$run_dir/run.log"
sim_status=${PIPESTATUS[0]}
set -e
printf 'simulator_exit_status\t%s\n' "$sim_status" >> "$run_dir/RUN_MANIFEST.tsv"
exit "$sim_status"
