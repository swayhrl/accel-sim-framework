#!/usr/bin/env bash
set -euo pipefail

runtime_root=/root/awma_r101r3_bounded_service_handoff_174_v1_runtime
repo=/root/workspace/accel-sim-framework-awma-r101r3-bounded-service-handoff-174-v1
tool_root="$repo/util/vm_tlb/awma/r101r3_bounded_service_handoff_v1"

mkdir -p "$runtime_root/tests"
g++ -std=c++11 -O2 -Wall -Wextra -Werror   -I"$runtime_root/src/gpgpu-sim/src/gpgpu-sim"   "$tool_root/awma_s1_directed_test.cc"   -o "$runtime_root/tests/awma_s1_directed_test"
"$runtime_root/tests/awma_s1_directed_test"
python3 "$tool_root/verify_s1_integration_hooks.py"
