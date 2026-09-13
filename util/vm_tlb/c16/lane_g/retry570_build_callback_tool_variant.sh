#!/usr/bin/env bash
# Build one bounded Retry570 callback diagnostic variant against frozen NVBit.
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "usage: $0 <nvbit-release-root> <debug|raw|empty> <output-tool-path>" >&2
  exit 2
fi
release_root=$1
variant=$2
output_path=$3
source_directory=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
[[ -d "${release_root}/core" ]] || { echo "missing NVBit core" >&2; exit 2; }
[[ ! -e "${output_path}" ]] || { echo "refusing to overwrite tool: ${output_path}" >&2; exit 2; }
case "${variant}" in
  debug) source_path="${source_directory}/retry570_callback_census_debug_tool.cu"; flags=(-g -Og) ;;
  raw) source_path="${source_directory}/retry570_callback_census_raw_tool.cu"; flags=(-O2) ;;
  empty) source_path="${source_directory}/retry570_empty_callback_dispatch_tool.cu"; flags=(-O2) ;;
  *) echo "unknown variant: ${variant}" >&2; exit 2 ;;
esac
mkdir -p "$(dirname "${output_path}")"
PATH="/usr/local/cuda-12.4/bin:${PATH}" nvcc -std=c++17 -D_FORCE_INLINES -Xcompiler -fPIC -arch=sm_86 "${flags[@]}" \
  -I"${release_root}/core" "${source_path}" \
  -L"${release_root}/core" -Xlinker --whole-archive -lnvbit -Xlinker --no-whole-archive \
  -L/usr/local/cuda-12.4/lib64 -lcuda -lcudart_static -ldl -lrt -lpthread \
  -shared -o "${output_path}"
sha256sum "${output_path}"
