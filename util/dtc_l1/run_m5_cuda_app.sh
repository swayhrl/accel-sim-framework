#!/usr/bin/env bash
# Create one isolated M5 simulator run directory and execute a CUDA app through
# the pinned Core runtime.  The formal config is copied unchanged; mode/capacity
# variations must be made in separately reviewed config artifacts.
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "usage: $0 <run-directory> <binary> <ptx> [application arguments...]" >&2
  exit 2
fi

run_dir=$1
binary=$2
ptx=$3
shift 3

: "${M5_GPGPUSIM_CONFIG:?set M5_GPGPUSIM_CONFIG to the reviewed config}"
: "${M5_CORE_RUNTIME:?set M5_CORE_RUNTIME to the built M5 libcudart.so}"

if [[ -e $run_dir ]]; then
  echo "refusing to reuse run directory: $run_dir" >&2
  exit 2
fi
for file in "$binary" "$ptx" "$M5_GPGPUSIM_CONFIG" "$M5_CORE_RUNTIME"; do
  if [[ ! -f $file ]]; then
    echo "required file is missing: $file" >&2
    exit 2
  fi
done

mkdir "$run_dir"
# GPGPU-Sim discovers its configuration by this fixed name in the application
# directory.  Preserve the caller's config artifact in provenance below, but
# materialize every isolated run under the simulator-required filename.
cp "$binary" "$ptx" "$run_dir/"
cp "$M5_GPGPUSIM_CONFIG" "$run_dir/gpgpusim.config"
binary_name=$(basename "$binary")
ptx_name=$(basename "$ptx")
ln -s "$M5_CORE_RUNTIME" "$run_dir/libcudart.so.11.0"

{
  printf 'binary_sha256='; sha256sum "$run_dir/$binary_name" | awk '{print $1}'
  printf 'ptx_sha256='; sha256sum "$run_dir/$ptx_name" | awk '{print $1}'
  printf 'config_sha256='; sha256sum "$run_dir/gpgpusim.config" | awk '{print $1}'
  printf 'runtime_sha256='; sha256sum "$M5_CORE_RUNTIME" | awk '{print $1}'
  printf 'argv='; printf '%q ' "$binary_name" "$@"; printf '\n'
  if [[ -n ${M5_INPUT_FILES:-} ]]; then
    IFS=':' read -r -a input_files <<<"$M5_INPUT_FILES"
    for input_file in "${input_files[@]}"; do
      if [[ ! -f $input_file ]]; then
        echo "declared M5 input is missing: $input_file" >&2
        exit 2
      fi
      printf 'input_sha256=%s ' "$(sha256sum "$input_file" | awk '{print $1}')"
      printf '%s\n' "$input_file"
    done
  fi
} >"$run_dir/run_identity.txt"

cd "$run_dir"
CUOBJDUMP_SIM_FILE=unused \
PTX_SIM_USE_PTX_FILE=1 \
PTX_SIM_KERNELFILE="$run_dir/$ptx_name" \
LD_LIBRARY_PATH="$run_dir:$(dirname "$M5_CORE_RUNTIME"):/usr/local/cuda-11.8/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
"$run_dir/$binary_name" "$@" >m5_run.log 2>&1
