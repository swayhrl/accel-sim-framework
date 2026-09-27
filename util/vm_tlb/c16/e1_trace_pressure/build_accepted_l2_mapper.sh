#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
repo_root=$(cd "$script_dir/../../../.." && pwd)

expected_core_sha=a2322069b9701597db7019080b5b54d29518e3a2
expected_config_sha=de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8
core_root=${C16_ACCEPTED_CORE_ROOT:-/root/workspace/gpgpu-sim-c16-trace-address-namespace-integration-v1}
config_rel=configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config
config_path="$repo_root/$config_rel"
out_dir=${C16_ACCEPTED_MAPPER_BUILD_DIR:-${TMPDIR:-/tmp}/c16_e1_accepted_l2_mapper}
binary=${C16_ACCEPTED_MAPPER_BINARY:-$out_dir/accepted_l2_mapper_cli}
if [[ -n "${CUDA_INSTALL_PATH:-}" ]]; then
  cuda_root=$CUDA_INSTALL_PATH
elif [[ -f /usr/local/cuda/include/vector_types.h ]]; then
  cuda_root=/usr/local/cuda
else
  cuda_root=/root/workspace/offline-sim-v1/toolchain/cuda-12.4
fi

[[ -d "$core_root" ]] || { echo "missing Core worktree: $core_root" >&2; exit 2; }
[[ -f "$config_path" ]] || { echo "missing accepted config: $config_path" >&2; exit 2; }
[[ -f "$cuda_root/include/vector_types.h" ]] || {
  echo "CUDA headers not found under $cuda_root" >&2
  exit 2
}

actual_core_sha=$(git -C "$core_root" rev-parse HEAD)
actual_config_sha=$(sha256sum "$config_path" | awk '{print $1}')
[[ "$actual_core_sha" == "$expected_core_sha" ]] || {
  echo "Core SHA mismatch: expected $expected_core_sha, got $actual_core_sha" >&2
  exit 2
}
if [[ -n "$(git -C "$core_root" status --porcelain --untracked-files=no)" ]]; then
  echo "Core worktree has tracked modifications; refusing non-exact source" >&2
  exit 2
fi
[[ "$actual_config_sha" == "$expected_config_sha" ]] || {
  echo "config SHA mismatch: expected $expected_config_sha, got $actual_config_sha" >&2
  exit 2
}

config_value() {
  local key=$1
  local value
  value=$(awk -v key="$key" '$1 == key { print $2 }' "$config_path")
  [[ -n "$value" ]] || { echo "missing config key: $key" >&2; exit 2; }
  [[ $(printf '%s\n' "$value" | wc -l) -eq 1 ]] || {
    echo "duplicate config key: $key" >&2
    exit 2
  }
  printf '%s' "$value"
}

n_mem=$(config_value -gpgpu_n_mem)
n_subpart=$(config_value -gpgpu_n_sub_partition_per_mchannel)
l2_config=$(config_value -gpgpu_cache:dl2)
mem_mask=$(config_value -gpgpu_mem_address_mask)
partition_indexing=$(config_value -gpgpu_memory_partition_indexing)
mem_mapping=$(config_value -gpgpu_mem_addr_mapping)

mkdir -p "$out_dir"
generated_header="$out_dir/accepted_l2_mapper_build_config.h"
{
  printf '#pragma once\n'
  printf '#define C16_ACCEPTED_CORE_SHA "%s"\n' "$actual_core_sha"
  printf '#define C16_ACCEPTED_CONFIG_SHA256 "%s"\n' "$actual_config_sha"
  printf '#define C16_ACCEPTED_CONFIG_PATH "%s"\n' "$config_rel"
  printf '#define C16_ACCEPTED_N_MEM %sU\n' "$n_mem"
  printf '#define C16_ACCEPTED_N_SUBPARTITIONS_PER_CHANNEL %sU\n' "$n_subpart"
  printf '#define C16_ACCEPTED_L2_CONFIG "%s"\n' "$l2_config"
  printf '#define C16_ACCEPTED_MEM_ADDRESS_MASK "%s"\n' "$mem_mask"
  printf '#define C16_ACCEPTED_PARTITION_INDEXING "%s"\n' "$partition_indexing"
  printf '#define C16_ACCEPTED_MEM_ADDR_MAPPING "%s"\n' "$mem_mapping"
} >"$generated_header"

cxx=${CXX:-g++}
common_flags=(
  -std=c++11 -O2 -Wall -Wextra -Wno-unused-parameter -Wno-reorder
  -ffunction-sections -fdata-sections
  -I"$out_dir" -I"$core_root/src" -I"$core_root/src/gpgpu-sim"
  -I"$cuda_root/include"
)

objects=("$out_dir/accepted_l2_mapper_cli.o")
"$cxx" "${common_flags[@]}" -Werror \
  -c "$script_dir/accepted_l2_mapper_cli.cc" -o "${objects[0]}"

core_sources=(
  "$core_root/src/option_parser.cc"
  "$core_root/src/gpgpu-sim/addrdec.cc"
  "$core_root/src/gpgpu-sim/gpu-cache.cc"
  "$core_root/src/gpgpu-sim/gpu-misc.cc"
  "$core_root/src/gpgpu-sim/hashing.cc"
  "$core_root/src/gpgpu-sim/oracle_elastic_residency.cc"
)
for source in "${core_sources[@]}"; do
  object="$out_dir/core_$(basename "${source%.cc}").o"
  "$cxx" "${common_flags[@]}" \
    -Wno-deprecated-copy -Wno-ignored-qualifiers -Wno-implicit-fallthrough \
    -Wno-sign-compare -c "$source" -o "$object"
  objects+=("$object")
done

"$cxx" -Wl,--gc-sections "${objects[@]}" -o "$binary"

printf '%s\n' "$binary"
