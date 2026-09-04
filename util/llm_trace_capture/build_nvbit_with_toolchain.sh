#!/usr/bin/env bash
# Build only through the explicitly selected CUDA toolkit; never trust PATH.
set -euo pipefail
framework_root='' work_root='' cuda_home=''
while [[ $# -gt 0 ]]; do
  case "$1" in
    --framework-root) framework_root=$2; shift 2 ;;
    --work-root) work_root=$2; shift 2 ;;
    --cuda-home) cuda_home=$2; shift 2 ;;
    *) echo "usage: $0 --framework-root DIR --work-root DIR --cuda-home DIR" >&2; exit 2 ;;
  esac
done
[[ -n "$framework_root" && -n "$work_root" && -n "$cuda_home" ]] || { echo 'missing required argument' >&2; exit 2; }
nvcc="$cuda_home/bin/nvcc"; ptxas="$cuda_home/bin/ptxas"
[[ -x "$nvcc" ]] || { echo "missing selected nvcc: $nvcc" >&2; exit 1; }
[[ -x "$ptxas" ]] || { echo "missing selected ptxas: $ptxas" >&2; exit 1; }
mkdir -p "$work_root/bootstrap"
selected_nvcc="$(realpath "$nvcc")"; selected_ptxas="$(realpath "$ptxas")"
path_before_nvcc="$(command -v nvcc || true)"; path_before_ptxas="$(command -v ptxas || true)"
"$selected_nvcc" --version > "$work_root/bootstrap/nvcc-version.txt"
"$selected_ptxas" --version > "$work_root/bootstrap/ptxas-version.txt"
{
  printf 'requested_cuda_home=%s\n' "$cuda_home"
  printf 'selected_nvcc=%s\nselected_ptxas=%s\n' "$selected_nvcc" "$selected_ptxas"
  printf 'path_before_nvcc=%s\npath_before_ptxas=%s\n' "$path_before_nvcc" "$path_before_ptxas"
  printf 'build_path_prefix=%s/bin\n' "$cuda_home"
} > "$work_root/bootstrap/toolchain-provenance.env"
# Makefile variables and the tightly scoped PATH agree. NVCC_PATH in the
# frozen Makefile therefore resolves to the selected toolkit too.
PATH="$cuda_home/bin:$PATH" CUDA_HOME="$cuda_home" \
  make -C "$framework_root/util/tracer_nvbit/tracer_tool" \
  NVCC="$selected_nvcc -ccbin=${CXX:-g++} -D_FORCE_INLINES" PTXAS="$selected_ptxas" \
  |& tee "$work_root/bootstrap/tracer-build.log"
PATH="$cuda_home/bin:$PATH" CUDA_HOME="$cuda_home" \
  make -C "$framework_root/util/tracer_nvbit/tracer_tool/traces-processing" \
  |& tee "$work_root/bootstrap/postprocess-build.log"
echo "PASS selected_nvcc=$selected_nvcc selected_ptxas=$selected_ptxas"
