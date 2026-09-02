#!/usr/bin/env bash
# Tiny pre-model NVBit test; it never touches Llama weights or M4A formal ROI.
set -euo pipefail
framework_root='' work_root='' cuda_home='' dry_run=0
while [[ $# -gt 0 ]]; do case "$1" in --framework-root) framework_root=$2;shift 2;; --work-root) work_root=$2;shift 2;; --cuda-home) cuda_home=$2;shift 2;; --dry-run) dry_run=1;shift;; *) echo "usage: $0 --framework-root DIR --work-root DIR --cuda-home DIR [--dry-run]" >&2;exit 2;; esac;done
[[ -n "$framework_root" && -n "$work_root" && -n "$cuda_home" ]] || { echo 'missing required argument' >&2;exit 2; }
[[ $dry_run == 1 || ${M4A_C_AUTHORIZED:-0} == 1 ]] || { echo 'BLOCKED: generic smoke requires future M4A-C authorization; --dry-run is safe now' >&2;exit 3; }
tracer="$framework_root/util/tracer_nvbit/tracer_tool/tracer_tool.so"; post="$framework_root/util/tracer_nvbit/tracer_tool/traces-processing/post-traces-processing"; out="$work_root/generic-nvbit-smoke"
if [[ $dry_run == 1 ]]; then printf 'DRY-RUN nvcc=%s/bin/nvcc\nptxas=%s/bin/ptxas\ninject=%s\npost=%s\noutput=%s\n' "$cuda_home" "$cuda_home" "$tracer" "$post" "$out"; exit 0;fi
[[ -x "$cuda_home/bin/nvcc" && -x "$cuda_home/bin/ptxas" && -f "$tracer" && -x "$post" ]] || { echo 'missing explicit nvcc/ptxas/tracer/postprocessor' >&2;exit 1; }
mkdir -p "$out/traces"; PATH="$cuda_home/bin:$PATH" "$cuda_home/bin/nvcc" "$framework_root/util/llm_trace_capture/nvbit_generic_smoke.cu" -o "$out/smoke"
TRACES_FOLDER="$out" ACTIVE_FROM_START=0 CUDA_INJECTION64_PATH="$tracer" "$out/smoke" |& tee "$out/injection.log"
"$post" "$out/traces" |& tee "$out/postprocess.log"; test -s "$out/traces/kernelslist.g"; find "$out/traces" -type f -name '*.traceg*' -size +0c | grep -q .
(cd "$out" && find . -type f -printf '%P\n' | sort | xargs -r sha256sum) > "$out/SHA256SUMS"; tar -czf "$out.tar.gz" -C "$(dirname "$out")" "$(basename "$out")"; sha256sum "$out.tar.gz" > "$out.tar.gz.sha256"; tar -tf "$out.tar.gz" >/dev/null; echo "PASS generic NVBit smoke archive=$out.tar.gz"
