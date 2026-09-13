#!/usr/bin/env bash
# Build the diagnostic-only NVBit timing probe against one frozen NVBit tree.
# This script stages sources under the official tool Makefile names so the
# injection callback receives NVBit's required --keep-device-functions flag.
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 <nvbit-release-root> <empty-output-directory>" >&2
  exit 2
fi

release_root=$1
output_directory=$2
source_directory=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
makefile_source="${release_root}/tools/instr_count_bb/Makefile"

[[ -d "${release_root}/core" ]] || { echo "missing NVBit core: ${release_root}/core" >&2; exit 2; }
[[ -f "${makefile_source}" ]] || { echo "missing official NVBit Makefile: ${makefile_source}" >&2; exit 2; }
[[ ! -e "${output_directory}" ]] || { echo "refusing to overwrite output directory: ${output_directory}" >&2; exit 2; }

mkdir -p "${output_directory}"
cp "${source_directory}/retry570_nvbit_timing_probe_tool.cu" "${output_directory}/timing_probe.cu"
cp "${source_directory}/retry570_nvbit_timing_probe_inject.cu" "${output_directory}/inject_funcs.cu"
cp "${makefile_source}" "${output_directory}/Makefile"

# NVBit's stock Makefile has a special `inject_funcs.o` rule.  Preserve that
# rule by using the filename it recognizes, and bind the absolute frozen core.
PATH="/usr/local/cuda-12.4/bin:${PATH}" make -C "${output_directory}" NVBIT_PATH="${release_root}/core" ARCH=sm_86
tool_path="${output_directory}/$(basename "${output_directory}").so"
[[ -f "${tool_path}" ]] || { echo "expected tool was not built: ${tool_path}" >&2; exit 2; }
sha256sum "${tool_path}"
