#!/usr/bin/env bash
set -euo pipefail

runtime=/root/awma_r101r4_p1_post_l1_local_service_174_v1_runtime
core="$runtime/src/gpgpu-sim"
repo=/root/workspace/accel-sim-framework-awma-r101r4-local-service-path-localization-174-v1
output=/root/share/mnt164/huangrulin/awma_r101r4_local_service_path_localization_174_v1/raw/regressions_p1
tools="$repo/util/vm_tlb/awma/r101r4_local_service_path_localization_v1"
mkdir -p "$runtime/tests" "$output"

for name in vm_m3_g3_4b_tlb_timing_test vm_m2_rf_pending_retry_test vm_c10b_runtime_validation_test
do
  g++ -std=c++17 -O2 -I"$core/src" \
    "$core/tests/$name.cc" "$core/src/gpgpu-sim/vm_translation.cc" \
    -o "$runtime/tests/$name"
  "$runtime/tests/$name" >"$output/$name.log" 2>&1
  grep -q PASS "$output/$name.log"
done

g++ -std=c++11 -O2 -Wall -Wextra -Werror \
  -I"$core/src/gpgpu-sim" \
  "$repo/util/vm_tlb/awma/r101_transient_l2_arch_v1/awma_transient_l2_policy_test.cc" \
  -o "$runtime/tests/awma_transient_l2_policy_test"
"$runtime/tests/awma_transient_l2_policy_test" \
  >"$output/awma_transient_l2_policy_test.log" 2>&1
grep -q '^AWMA_TRANSIENT_L2_POLICY_TEST_PASS$' \
  "$output/awma_transient_l2_policy_test.log"

g++ -std=c++11 -O2 -Wall -Wextra -Werror \
  -I"$core/src/gpgpu-sim" \
  "$repo/util/vm_tlb/awma/r101r2_context2_memory_service_v1/awma_o2_directed_test.cc" \
  -o "$runtime/tests/awma_o2_directed_test"
"$runtime/tests/awma_o2_directed_test" >"$output/o2_policy.log" 2>&1
grep -q 'AWMA_R101R2_O2_DIRECTED_TESTS PASS tests=18' \
  "$output/o2_policy.log"

"$tools/run_p1_directed_tests.sh" >"$output/p1_directed_and_hooks.log" 2>&1
grep -q 'AWMA_R101R4_P0_DIRECTED PASS checks=22' \
  "$output/p1_directed_and_hooks.log"
grep -q 'AWMA_R101R4_P1_HOOKS PASS checks=23' \
  "$output/p1_directed_and_hooks.log"

(
  cd "$output"
  sha256sum *.log > SHA256SUMS
  sha256sum -c SHA256SUMS
)
echo R101R4_P1_REGRESSIONS_AND_DIRECTED_PASS
