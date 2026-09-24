#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "gpgpu-sim/vm_translation.h"

static vm_translation::translation_key key(uint64_t vpn) {
  return vm_translation::translation_key(0, vpn, 64ULL * 1024ULL);
}

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

  unsetenv("GPGPUSIM_AWMA_SHARE_DELIVERY_SLOTS");
  assert(vm_translation::awma_share_delivery_slots() == 1);
  setenv("GPGPUSIM_AWMA_SHARE_DELIVERY_SLOTS", "2", 1);
  assert(vm_translation::awma_share_delivery_slots() == 2);
  setenv("GPGPUSIM_AWMA_SHARE_DELIVERY_SLOTS", "1", 1);
  assert(vm_translation::awma_share_delivery_slots() == 1);
  unsetenv("GPGPUSIM_AWMA_SHARE_DELIVERY_SLOTS");

  // C1 legality: same page/key/generation/permission is shareable.  Every
  // incompatible identity component and a cross-page transaction rejects.
  assert(vm_translation::same_page_share_compatible(
      7, 3 * page + 32, 32, vm_translation::TRANSLATION_ACCESS_READ, 9,
      7, 3 * page + 96, 32, vm_translation::TRANSLATION_ACCESS_READ, 9,
      page));
  assert(!vm_translation::same_page_share_compatible(
      7, 3 * page, 32, vm_translation::TRANSLATION_ACCESS_READ, 9,
      8, 3 * page + 64, 32, vm_translation::TRANSLATION_ACCESS_READ, 9,
      page));
  assert(!vm_translation::same_page_share_compatible(
      7, 3 * page, 32, vm_translation::TRANSLATION_ACCESS_READ, 9,
      7, 3 * page + 64, 32, vm_translation::TRANSLATION_ACCESS_WRITE, 9,
      page));
  assert(!vm_translation::same_page_share_compatible(
      7, 3 * page, 32, vm_translation::TRANSLATION_ACCESS_READ, 9,
      7, 3 * page + 64, 32, vm_translation::TRANSLATION_ACCESS_READ, 10,
      page));
  assert(!vm_translation::same_page_share_compatible(
      7, 3 * page, 32, vm_translation::TRANSLATION_ACCESS_READ, 9,
      7, 4 * page, 32, vm_translation::TRANSLATION_ACCESS_READ, 9,
      page));
  assert(!vm_translation::same_page_share_compatible(
      7, 4 * page - 16, 32, vm_translation::TRANSLATION_ACCESS_READ, 9,
      7, 3 * page, 32, vm_translation::TRANSLATION_ACCESS_READ, 9,
      page));

  // Requester-path telemetry distinguishes a walk owner, an outstanding-MSHR
  // merger, and a later ordinary L1 hit without changing translation output.
  unsetenv("GPGPUSIM_AWMA_TRANSLATION_CANDIDATE");
  vm_translation::translation_controller service_vm(service_config());
  uint64_t first_pa = 0;
  uint64_t merged_pa = 0;
  vm_translation::translation_source first_source =
      vm_translation::TRANSLATION_SOURCE_UNOBSERVED;
  vm_translation::translation_source merged_source =
      vm_translation::TRANSLATION_SOURCE_UNOBSERVED;
  vm_translation::request_service_class first_service =
      vm_translation::REQUEST_SERVICE_UNOBSERVED;
  vm_translation::request_service_class merged_service =
      vm_translation::REQUEST_SERVICE_UNOBSERVED;
  bool first_ready = false;
  bool merged_ready = false;
  for (uint64_t cycle = 0; cycle < 50 && (!first_ready || !merged_ready);
       ++cycle) {
    if (!first_ready)
      first_ready = service_vm.translate(
          0, 0, 40 * page + 1, 32, cycle, 1001, &first_pa, &first_source,
          vm_translation::TRANSLATION_ACCESS_READ, true, &first_service) ==
                    vm_translation::READY;
    if (!merged_ready)
      merged_ready = service_vm.translate(
          0, 0, 40 * page + 2, 32, cycle, 1002, &merged_pa,
          &merged_source, vm_translation::TRANSLATION_ACCESS_READ, true,
          &merged_service) == vm_translation::READY;
    service_vm.cycle(cycle);
  }
  assert(first_ready && merged_ready);
  assert(first_pa == 40 * page + 1 && merged_pa == 40 * page + 2);
  assert(first_service == vm_translation::REQUEST_SERVICE_PTW);
  assert(merged_service == vm_translation::REQUEST_SERVICE_MSHR_MERGE);
  uint64_t hit_pa = 0;
  vm_translation::translation_source hit_source =
      vm_translation::TRANSLATION_SOURCE_UNOBSERVED;
  vm_translation::request_service_class hit_service =
      vm_translation::REQUEST_SERVICE_UNOBSERVED;
  bool hit_ready = false;
  for (uint64_t cycle = 50; cycle < 60 && !hit_ready; ++cycle) {
    hit_ready = service_vm.translate(
        0, 0, 40 * page + 3, 32, cycle, 1003, &hit_pa, &hit_source,
        vm_translation::TRANSLATION_ACCESS_READ, true, &hit_service) ==
                vm_translation::READY;
    service_vm.cycle(cycle);
  }
  assert(hit_ready && hit_pa == 40 * page + 3);
  assert(hit_service == vm_translation::REQUEST_SERVICE_L1_HIT);
  assert(service_vm.quiescent_invariants_hold());

  // OFF is exact ordinary LRU and allocates no candidate state.
  unsetenv("GPGPUSIM_AWMA_TRANSLATION_CANDIDATE");
  vm_translation::set_associative_tlb off(
      vm_translation::tlb_config(2, 2, 1), true);
  uint64_t ppn = 0;
  off.fill(key(1), 1, 0);
  off.fill(key(2), 2, 1);
  off.fill(key(3), 3, 2);
  assert(!off.refill_protection_enabled());
  assert(!off.probe(key(1), 3, &ppn));
  assert(off.candidate_pending() == 0);
  assert(off.refill_stats().history_inserts == 0);

  // C2: an evicted key that misses again enters the bounded pending set; its
  // refill is protected, a later hit is useful, and replacement skips it.
  setenv("GPGPUSIM_AWMA_TRANSLATION_CANDIDATE", "refill_protect", 1);
  vm_translation::set_associative_tlb protected_tlb(
      vm_translation::tlb_config(2, 2, 1), true);
  protected_tlb.fill(key(10), 10, 0);
  protected_tlb.fill(key(11), 11, 1);
  protected_tlb.fill(key(12), 12, 2);  // Evicts 10 and records history.
  assert(!protected_tlb.probe(key(10), 3, &ppn));
  assert(protected_tlb.candidate_pending() == 1);
  protected_tlb.fill(key(10), 10, 4);
  assert(protected_tlb.candidate_pending() == 0);
  assert(protected_tlb.refill_stats().protected_refills == 1);
  assert(protected_tlb.probe(key(10), 5, &ppn) && ppn == 10);
  protected_tlb.fill(key(13), 13, 6);
  assert(protected_tlb.probe(key(10), 7, &ppn));
  assert(protected_tlb.refill_stats().protected_hits >= 2);
  assert(protected_tlb.refill_stats().protected_victim_skips >= 1);

  // A one-way set proves the all-protected fallback always makes progress.
  vm_translation::set_associative_tlb fallback(
      vm_translation::tlb_config(1, 1, 1), true);
  fallback.fill(key(20), 20, 0);
  fallback.fill(key(21), 21, 1);  // history contains 20
  assert(!fallback.probe(key(20), 2, &ppn));
  fallback.fill(key(20), 20, 3);  // protected refill
  fallback.fill(key(22), 22, 4);  // must fall back to LRU, never pin/deadlock
  assert(fallback.refill_stats().all_protected_lru_fallbacks == 1);
  assert(fallback.candidate_pending() == 0);
  assert(!fallback.probe(key(20), 5, &ppn));
  assert(fallback.candidate_pending() == 1);
  fallback.fill(key(20), 20, 6);
  assert(fallback.candidate_pending() == 0);

  // The 20-bit protection clock has an explicit wrap reset; no stale timer
  // can become protected again after the counter wraps.
  vm_translation::set_associative_tlb wrap(
      vm_translation::tlb_config(1, 1, 1), true);
  wrap.fill(key(30), 30, 0);
  wrap.fill(key(31), 31, 1);
  assert(!wrap.probe(key(30), 2, &ppn));
  wrap.fill(key(30), 30, 3);
  assert(wrap.probe(key(30), (1ULL << 20) + 3, &ppn));
  assert(wrap.refill_stats().timer_wrap_resets == 1);

  printf("awma_literature_mechanism_test PASS\n");
  return 0;
}
