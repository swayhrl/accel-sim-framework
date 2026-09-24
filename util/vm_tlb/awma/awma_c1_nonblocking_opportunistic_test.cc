#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gpgpu-sim/vm_translation.h"

static vm_translation::translation_config service_config() {
  const uint64_t page = 64ULL * 1024ULL;
  return vm_translation::translation_config(
      1, page, vm_translation::tlb_config(4, 4, 1),
      vm_translation::tlb_config(8, 8, 1), 8, 8, 1, 1,
      vm_translation::page_table_config(), 0,
      vm_translation::pwc_config(vm_translation::PWC_OFF, 0, 1), 1, 1);
}

int main() {
  const uint64_t page = 64ULL * 1024ULL;

  setenv("GPGPUSIM_AWMA_TRANSLATION_CANDIDATE",
         "nonblocking_opportunistic_share", 1);
  assert(vm_translation::awma_candidate_mode() ==
         vm_translation::
             AWMA_TRANSLATION_CANDIDATE_NONBLOCKING_OPPORTUNISTIC_SHARE);
  assert(strcmp(vm_translation::awma_candidate_mode_name(
                    vm_translation::
                        AWMA_TRANSLATION_CANDIDATE_NONBLOCKING_OPPORTUNISTIC_SHARE),
                "nonblocking_opportunistic_share") == 0);

  // READY at the member decision point shares; not-READY falls back.
  assert(vm_translation::decide_nonblocking_share(true, true, false) ==
         vm_translation::NONBLOCKING_SHARE_READY_OWNER);
  assert(vm_translation::decide_nonblocking_share(true, false, false) ==
         vm_translation::NONBLOCKING_SHARE_BASELINE_FALLBACK);
  assert(vm_translation::decide_nonblocking_share(false, true, false) ==
         vm_translation::NONBLOCKING_SHARE_NOT_A_MEMBER);

  // Once fallback is selected, a late READY owner cannot apply a result.
  bool fallback_locked = false;
  bool translation_applied = false;
  unsigned applications = 0;
  vm_translation::nonblocking_share_action action =
      vm_translation::decide_nonblocking_share(true, false, fallback_locked);
  assert(action == vm_translation::NONBLOCKING_SHARE_BASELINE_FALLBACK);
  fallback_locked = true;
  translation_applied = true;  // frozen baseline path completes exactly once
  ++applications;
  action = vm_translation::decide_nonblocking_share(
      true, true, fallback_locked);
  assert(action == vm_translation::NONBLOCKING_SHARE_FALLBACK_LOCKED);
  assert(translation_applied && applications == 1);

  // ASID/page/generation/permission mismatches are never legal members.
  assert(vm_translation::same_page_share_compatible(
      3, 8 * page + 32, 32, vm_translation::TRANSLATION_ACCESS_READ, 7,
      3, 8 * page + 96, 32, vm_translation::TRANSLATION_ACCESS_READ, 7,
      page));
  assert(!vm_translation::same_page_share_compatible(
      3, 8 * page + 32, 32, vm_translation::TRANSLATION_ACCESS_READ, 7,
      4, 8 * page + 96, 32, vm_translation::TRANSLATION_ACCESS_READ, 7,
      page));
  assert(!vm_translation::same_page_share_compatible(
      3, 8 * page + 32, 32, vm_translation::TRANSLATION_ACCESS_READ, 7,
      3, 9 * page + 96, 32, vm_translation::TRANSLATION_ACCESS_READ, 7,
      page));
  assert(!vm_translation::same_page_share_compatible(
      3, 8 * page + 32, 32, vm_translation::TRANSLATION_ACCESS_READ, 7,
      3, 8 * page + 96, 32, vm_translation::TRANSLATION_ACCESS_READ, 8,
      page));
  assert(!vm_translation::same_page_share_compatible(
      3, 8 * page + 32, 32, vm_translation::TRANSLATION_ACCESS_READ, 7,
      3, 8 * page + 96, 32, vm_translation::TRANSLATION_ACCESS_WRITE, 7,
      page));

  // A fallback request never cancels the owner. Both finish through bounded
  // controller state, the second requester is explicitly classified, and the
  // controller reaches full terminal quiescence.
  vm_translation::translation_controller controller(service_config());
  uint64_t owner_pa = 0, fallback_pa = 0;
  vm_translation::translation_source owner_source =
      vm_translation::TRANSLATION_SOURCE_UNOBSERVED;
  vm_translation::translation_source fallback_source =
      vm_translation::TRANSLATION_SOURCE_UNOBSERVED;
  vm_translation::request_service_class owner_service =
      vm_translation::REQUEST_SERVICE_UNOBSERVED;
  vm_translation::request_service_class fallback_service =
      vm_translation::REQUEST_SERVICE_UNOBSERVED;
  bool owner_done = false, fallback_done = false;
  for (uint64_t cycle = 0; cycle < 64 && (!owner_done || !fallback_done);
       ++cycle) {
    if (!owner_done)
      owner_done = controller.translate(
          0, 0, 20 * page + 8, 32, cycle, 101, &owner_pa, &owner_source,
          vm_translation::TRANSLATION_ACCESS_READ, true, &owner_service) ==
                   vm_translation::READY;
    if (!fallback_done)
      fallback_done = controller.translate(
          0, 0, 20 * page + 72, 32, cycle, 102, &fallback_pa,
          &fallback_source, vm_translation::TRANSLATION_ACCESS_READ, true,
          &fallback_service) == vm_translation::READY;
    controller.cycle(cycle);
  }
  assert(owner_done && fallback_done);
  assert(owner_pa == 20 * page + 8);
  assert(fallback_pa == 20 * page + 72);
  assert(owner_service == vm_translation::REQUEST_SERVICE_PTW);
  assert(fallback_service == vm_translation::REQUEST_SERVICE_MSHR_MERGE);
  assert(controller.stats().mshr_merges == 1);
  assert(controller.quiescent_invariants_hold());

  printf("awma_c1_nonblocking_opportunistic_test PASS\n");
  return 0;
}
