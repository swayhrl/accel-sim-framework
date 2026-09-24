#include <assert.h>
#include <stdint.h>
#include <stdio.h>

#include "gpgpu-sim/vm_translation.h"

int main() {
  const uint64_t page = 64ULL * 1024ULL;

  // Frozen candidate consumes an already-ready legal owner result.
  assert(vm_translation::decide_nonblocking_share(true, true, false) ==
         vm_translation::NONBLOCKING_SHARE_READY_OWNER);

  // The sole control intervention masks READY consumption. The exact same
  // legal member therefore takes the non-ready baseline fallback action.
  const bool owner_ready = true;
  const bool owner_only_no_share_control = true;
  assert(vm_translation::decide_nonblocking_share(
             true, owner_ready && !owner_only_no_share_control, false) ==
         vm_translation::NONBLOCKING_SHARE_BASELINE_FALLBACK);

  // A late owner result remains unable to apply after the control fallback.
  assert(vm_translation::decide_nonblocking_share(
             true, owner_ready && !owner_only_no_share_control, true) ==
         vm_translation::NONBLOCKING_SHARE_FALLBACK_LOCKED);

  // Non-ready behavior is matched between candidate and control.
  assert(vm_translation::decide_nonblocking_share(true, false, false) ==
         vm_translation::NONBLOCKING_SHARE_BASELINE_FALLBACK);

  // The control does not widen grouping legality.
  assert(vm_translation::same_page_share_compatible(
      5, 6 * page + 8, 32, vm_translation::TRANSLATION_ACCESS_READ, 11,
      5, 6 * page + 72, 32, vm_translation::TRANSLATION_ACCESS_READ, 11,
      page));
  assert(!vm_translation::same_page_share_compatible(
      5, 6 * page + 8, 32, vm_translation::TRANSLATION_ACCESS_READ, 11,
      6, 6 * page + 72, 32, vm_translation::TRANSLATION_ACCESS_READ, 11,
      page));
  assert(!vm_translation::same_page_share_compatible(
      5, 6 * page + 8, 32, vm_translation::TRANSLATION_ACCESS_READ, 11,
      5, 6 * page + 72, 32, vm_translation::TRANSLATION_ACCESS_WRITE, 11,
      page));

  printf("awma_c1_nonblocking_causal_ablation_test PASS\n");
  return 0;
}
