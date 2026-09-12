#!/usr/bin/env bash
# Run exactly one C14 selected kernel in a fresh, isolated directory.
# The original trace list is read only and supplies membership validation only.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: run_c14_microdiagnostic.sh --framework-root DIR --core-root DIR --simulator PATH \
  --roi {prefill|decode1} --base-config PATH --geometry-config PATH \
  --trace-list PATH --trace-dir DIR --trace-name NAME --run-dir DIR \
  [--segment-map PATH] [--telemetry-line OPTION] [--label TEXT]
EOF
}

framework_root=""; core_root=""; simulator=""; roi=""; base_config=""; geometry_config=""
trace_list=""; trace_dir=""; trace_name=""; run_dir=""; segment_map=""; telemetry_line=""; label=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --framework-root) framework_root="$2"; shift 2 ;;
    --core-root) core_root="$2"; shift 2 ;;
    --simulator) simulator="$2"; shift 2 ;;
    --roi) roi="$2"; shift 2 ;;
    --base-config) base_config="$2"; shift 2 ;;
    --geometry-config) geometry_config="$2"; shift 2 ;;
    --trace-list) trace_list="$2"; shift 2 ;;
    --trace-dir) trace_dir="$2"; shift 2 ;;
    --trace-name) trace_name="$2"; shift 2 ;;
    --run-dir) run_dir="$2"; shift 2 ;;
    --segment-map) segment_map="$2"; shift 2 ;;
    --telemetry-line) telemetry_line="$2"; shift 2 ;;
    --label) label="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -n "$framework_root" && -n "$core_root" && -x "$simulator" && -n "$roi" && -f "$base_config" && -f "$geometry_config" && -f "$trace_list" && -d "$trace_dir" && -n "$trace_name" && -n "$run_dir" ]] || { usage >&2; exit 2; }
[[ "$roi" == prefill || "$roi" == decode1 ]] || { echo "invalid ROI" >&2; exit 2; }
[[ "$trace_name" =~ ^[A-Za-z0-9._-]+\.traceg\.xz$ ]] || { echo "unsafe trace name" >&2; exit 2; }
[[ ! -e "$run_dir" ]] || { echo "run directory already exists: $run_dir" >&2; exit 2; }
[[ -f "$trace_dir/$trace_name" ]] || { echo "selected trace missing" >&2; exit 2; }
[[ "$(grep -Fxc "$trace_name" "$trace_list")" == 1 ]] || { echo "selected trace must occur exactly once in source list" >&2; exit 2; }
if [[ -n "$segment_map" ]]; then [[ -f "$segment_map" ]] || { echo "missing Segment map" >&2; exit 2; }; fi

case "$roi" in
  prefill) object_map="$framework_root/configs/vm_tlb/object_maps/M4C_PREFILL_OBJECT_MAP.tsv" ;;
  decode1) object_map="$framework_root/configs/vm_tlb/object_maps/M4C_DECODE1_OBJECT_MAP.tsv" ;;
esac
trace_config="$framework_root/gpu-simulator/configs/tested-cfgs/SM86_RTX3070/trace.config"
[[ -f "$object_map" && -f "$trace_config" ]] || { echo "missing C14 immutable map/config" >&2; exit 2; }
runtime=$(find "$core_root/lib" -type f -path '*/release/libcudart.so' -print -quit)
[[ -n "$runtime" ]] || { echo "missing C14 Core runtime" >&2; exit 2; }
export LD_LIBRARY_PATH="$(dirname "$runtime"):${LD_LIBRARY_PATH:-}"

mkdir -p "$run_dir/traces"
printf '%s\n' "$trace_name" > "$run_dir/traces/kernelslist.g"
ln -s "$trace_dir/$trace_name" "$run_dir/traces/$trace_name"
cat "$base_config" "$trace_config" "$geometry_config" > "$run_dir/gpgpusim.config"
printf '%s\n' "-gpgpu_vm_object_map $object_map" >> "$run_dir/gpgpusim.config"
if [[ -n "$segment_map" ]]; then printf '%s\n' "-gpgpu_vm_weight_segment_map $segment_map" >> "$run_dir/gpgpusim.config"; fi
if [[ -n "$telemetry_line" ]]; then printf '%s\n' "$telemetry_line" >> "$run_dir/gpgpusim.config"; fi

{
  printf 'field\tvalue\n'
  printf 'label\t%s\n' "$label"
  printf 'scope\tEXPLORATORY_MICRODIAGNOSTIC;STATE_CONTEXT_NOT_FULL_ROI_EQUIVALENT\n'
  printf 'roi\t%s\n' "$roi"
  printf 'trace_name\t%s\n' "$trace_name"
  printf 'framework_head\t%s\n' "$(git -C "$framework_root" rev-parse HEAD)"
  printf 'core_head\t%s\n' "$(git -C "$core_root" rev-parse HEAD)"
  sha256sum "$base_config" "$geometry_config" "$trace_config" "$object_map" "$trace_list" "$run_dir/traces/kernelslist.g" "$run_dir/gpgpusim.config" | awk '{print "sha256:" $2 "\t" $1}'
  if [[ -n "$segment_map" ]]; then sha256sum "$segment_map" | awk '{print "sha256:" $2 "\t" $1}'; fi
} > "$run_dir/RUN_MANIFEST.tsv"

set +e
(
  cd "$run_dir"
  /usr/bin/time -f 'WALL_SECONDS=%e RSS_KB=%M' "$simulator" -config "$run_dir/gpgpusim.config" -trace "$run_dir/traces/kernelslist.g"
) 2>&1 | tee "$run_dir/run.log"
status=${PIPESTATUS[0]}
set -e
printf 'simulator_exit_status\t%s\n' "$status" >> "$run_dir/RUN_MANIFEST.tsv"
exit "$status"
