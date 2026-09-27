#!/usr/bin/env bash
set -euo pipefail

runtime=/root/awma_r101_transient_l2_arch_174_v1_runtime
core="$runtime/src/gpgpu-sim"
repo=/root/workspace/accel-sim-framework-awma-r101-transient-l2-arch-174-v1
output=/root/share/mnt164/huangrulin/awma_r101_transient_l2_arch_174_v1/raw/postimplementation_regressions
mkdir -p "$runtime/tests" "$output"

for name in vm_m3_g3_4b_tlb_timing_test vm_m2_rf_pending_retry_test vm_c10b_runtime_validation_test; do
  g++ -std=c++17 -O2 -I"$core/src" \
    "$core/tests/$name.cc" "$core/src/gpgpu-sim/vm_translation.cc" \
    -o "$runtime/tests/$name"
  "$runtime/tests/$name" >"$output/$name.log" 2>&1
  grep -q 'PASS' "$output/$name.log"
done

g++ -std=c++11 -O2 -Wall -Wextra -Werror \
  -I"$core/src/gpgpu-sim" \
  "$repo/util/vm_tlb/awma/r101_transient_l2_arch_v1/awma_transient_l2_policy_test.cc" \
  -o "$runtime/tests/awma_transient_l2_policy_test"
"$runtime/tests/awma_transient_l2_policy_test" \
  >"$output/awma_transient_l2_policy_test.log" 2>&1
grep -q '^AWMA_TRANSIENT_L2_POLICY_TEST_PASS$' \
  "$output/awma_transient_l2_policy_test.log"

sha256sum "$output"/*.log >"$output/SHA256SUMS"
echo DIRECTED_TESTS_PASS
