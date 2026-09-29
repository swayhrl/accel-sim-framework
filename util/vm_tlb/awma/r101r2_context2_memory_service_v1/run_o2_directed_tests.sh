#!/usr/bin/env bash
set -euo pipefail

runtime=/root/awma_r101r2_context2_memory_service_174_v1_runtime/src/gpgpu-sim
repo=/root/workspace/accel-sim-framework-awma-r101r2-context2-memory-service-174-v1
test_dir="$runtime/tests/r101r2_o2"
mkdir -p "$test_dir"

g++ -std=c++11 -O2 -Wall -Wextra -Werror \
  -I"$runtime/src/gpgpu-sim" \
  "$repo/util/vm_tlb/awma/r101r2_context2_memory_service_v1/awma_o2_directed_test.cc" \
  -o "$test_dir/awma_o2_directed_test"

"$test_dir/awma_o2_directed_test"
python3 "$repo/util/vm_tlb/awma/r101r2_context2_memory_service_v1/verify_o2_integration_hooks.py"
