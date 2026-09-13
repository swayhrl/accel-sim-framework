#!/usr/bin/env bash
# Build the introspection-free Retry570 CUDA-driver callback census tool.
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 <nvbit-release-root> <output-tool-path>" >&2
  exit 2
fi
release_root=$1
output_path=$2
source_directory=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
[[ -d "${release_root}/core" ]] || { echo "missing NVBit core" >&2; exit 2; }
[[ ! -e "${output_path}" ]] || { echo "refusing to overwrite tool: ${output_path}" >&2; exit 2; }
mkdir -p "$(dirname "${output_path}")"
PATH="/usr/local/cuda-12.4/bin:${PATH}" nvcc -std=c++17 -D_FORCE_INLINES -Xcompiler -fPIC -arch=sm_86 -O3 \
  -I"${release_root}/core" "${source_directory}/retry570_callback_census_tool.cu" \
  -L"${release_root}/core" -Xlinker --whole-archive -lnvbit -Xlinker --no-whole-archive \
  -L/usr/local/cuda-12.4/lib64 -lcuda -lcudart_static -ldl -lrt -lpthread \
  -shared -o "${output_path}"
sha256sum "${output_path}"
