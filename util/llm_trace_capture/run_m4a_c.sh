#!/usr/bin/env bash
# Prepared M4A-C driver.  It is intentionally non-runnable in M4A-P.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage (only after explicit M4A-C authorization):
  M4A_C_AUTHORIZED=1 run_m4a_c.sh --framework-root DIR --work-root DIR \
    --cuda-home DIR --workload-command-file FILE --trace-region prefill|decode1|decode_reuse \
    [--minimum-free-gib N] [--required-gpu-count N]

The executable command file is run once normally (M4A_PHASE=smoke) and once
under the frozen NVBit tracer (M4A_PHASE=trace) for exactly one ROI. It must write
$M4A_METADATA_PATH in m4a-allocation-sidecar-v1.  This wrapper cannot infer or
approve the paper's unknown TP=4/dtype/model-revision details.
EOF
}

framework_root=""; work_root=""; cuda_home=""; command_file=""; minimum_free_gib=500; required_gpu_count=4
while [[ $# -gt 0 ]]; do
  case "$1" in
    --framework-root) framework_root="$2"; shift 2 ;;
    --work-root) work_root="$2"; shift 2 ;;
    --cuda-home) cuda_home="$2"; shift 2 ;;
    --workload-command-file) command_file="$2"; shift 2 ;;
    --minimum-free-gib) minimum_free_gib="$2"; shift 2 ;;
    --required-gpu-count) required_gpu_count="$2"; shift 2 ;;
    --trace-region) trace_region="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ "${M4A_C_AUTHORIZED:-0}" == 1 ]] || { echo "BLOCKED: M4A-C is not authorized" >&2; exit 3; }
[[ -n "$framework_root" && -n "$work_root" && -n "$cuda_home" && -n "$command_file" && -n "${trace_region:-}" ]] || { usage >&2; exit 2; }
[[ "$trace_region" =~ ^(prefill|decode1|decode_reuse)$ ]] || { echo "error: --trace-region must be prefill, decode1, or decode_reuse" >&2; exit 2; }
[[ -x "$command_file" ]] || { echo "error: command file must be executable" >&2; exit 2; }
[[ -n "${M4A_MODEL_LOCAL_PATH:-}" && -n "${M4A_MODEL_LOCAL_MANIFEST:-}" ]] || { echo "error: formal Route-E capture requires verified M4A_MODEL_LOCAL_PATH and M4A_MODEL_LOCAL_MANIFEST" >&2; exit 2; }
capture_status="${M4A_CAPTURE_STATUS:-FORMAL}"
[[ "$capture_status" =~ ^(DIAGNOSTIC_PILOT|FORMAL)$ ]] || { echo "error: M4A_CAPTURE_STATUS must be DIAGNOSTIC_PILOT or FORMAL for traced Route-E runs" >&2; exit 2; }
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
framework_root="$(cd "$framework_root" && pwd)"; mkdir -p "$work_root"; work_root="$(cd "$work_root" && pwd)"
python3 "$script_dir/capture_ready_preflight.py" --framework-root "$framework_root" --work-root "$work_root" --cuda-home "$cuda_home" --minimum-free-gib "$minimum_free_gib" --required-gpu-count "$required_gpu_count"
tracer="$framework_root/util/tracer_nvbit/tracer_tool/tracer_tool.so"
post="$framework_root/util/tracer_nvbit/tracer_tool/traces-processing/post-traces-processing"
run_id="m4a-llama-${trace_region}-$(date -u +%Y%m%dT%H%M%SZ)"; run_dir="$work_root/runs/$run_id"; trace_dir="$run_dir/traces"
mkdir -p "$trace_dir"
export M4A_RUN_DIR="$run_dir" M4A_METADATA_PATH="$run_dir/allocation-sidecar.json" M4A_REQUIRED_GPU_COUNT="$required_gpu_count" M4A_TRACE_REGION="$trace_region" M4A_CAPTURE_STATUS="$capture_status"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-$(seq -s, 0 $((required_gpu_count - 1)))}"
export PATH="$cuda_home/bin:$PATH"
unset CUDA_INJECTION64_PATH
M4A_PHASE=smoke "$command_file" |& tee "$run_dir/smoke.log"
python3 "$script_dir/validate_metadata.py" "$M4A_METADATA_PATH" | tee "$run_dir/metadata-smoke.json"
unset CUDA_INJECTION64_PATH
export M4A_PHASE=trace TRACES_FOLDER="$run_dir" M4A_NVBIT_PATH="$tracer" ACTIVE_FROM_START=0 TOOL_COMPRESS=1 TRACE_FILE_COMPRESS=1
"$command_file" |& tee "$run_dir/trace.log"
"$post" "$trace_dir" |& tee "$run_dir/postprocess.log"
test -s "$trace_dir/kernelslist.g" || { echo "error: missing kernelslist.g" >&2; exit 1; }
find "$trace_dir" -type f -name '*.traceg*' -size +0c | grep -q . || { echo "error: no nonempty traceg files" >&2; exit 1; }
python3 "$script_dir/classify_kernels.py" --kernelslist "$trace_dir/kernelslist.g" --output-dir "$run_dir/kernel-classification" |& tee "$run_dir/kernel-classification.log"
python3 "$script_dir/validate_metadata.py" "$M4A_METADATA_PATH" | tee "$run_dir/metadata-trace.json"
(cd "$run_dir" && find . -type f -printf '%P\n' | sort | xargs -r sha256sum) > "$run_dir/SHA256SUMS"
archive="$work_root/archives/$run_id.tar.zst"; mkdir -p "$(dirname "$archive")"
if command -v zstd >/dev/null 2>&1; then tar --use-compress-program='zstd -T0 -3' -cf "$archive" -C "$run_dir/.." "$run_id"; else archive="${archive%.zst}.gz"; tar -czf "$archive" -C "$run_dir/.." "$run_id"; fi
sha256sum "$archive" > "$archive.sha256"; tar -tf "$archive" >/dev/null
printf 'PASS archive=%s sha256=%s\n' "$archive" "$archive.sha256"
