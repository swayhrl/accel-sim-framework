#!/usr/bin/env bash
set -euo pipefail
runtime=/root/awma_r101r4_p1_post_l1_local_service_174_v1_runtime
repo=/root/workspace/accel-sim-framework-awma-r101r4-local-service-path-localization-174-v1
tools="$repo/util/vm_tlb/awma/r101r4_local_service_path_localization_v1"
mkdir -p "$runtime/tests"
g++ -std=c++11 -O2 -Wall -Wextra -Werror \
  -I"$runtime/src/gpgpu-sim/src/gpgpu-sim" \
  "$tools/awma_p0_directed_test.cc" \
  -o "$runtime/tests/awma_p1_finite_directed_test"
"$runtime/tests/awma_p1_finite_directed_test"
python3 "$tools/verify_p1_integration_hooks.py"
