#include <assert.h>
#include <stdint.h>
#include <stdio.h>

#include "gpgpu-sim/prel1_exact_coalescer.h"
#include "gpgpu-sim/vm_translation.h"

static vm_translation::translation_config make_config() {
  const uint64_t page = 65536;
  return vm_translation::translation_config(
      1, page, vm_translation::tlb_config(1, 1, 1),
      vm_translation::tlb_config(8, 8, 1), 8, 8, 1, 1,
      vm_translation::page_table_config(), 0,
      vm_translation::pwc_config(vm_translation::PWC_OFF, 0, 1), 2, 3);
}

static uint64_t drain_one(vm_translation::translation_controller *vm,
                          uint64_t va, uint64_t uid, uint64_t begin,
                          vm_translation::translation_source *source_out) {
  uint64_t pa = 0;
  vm_translation::translation_source source =
      vm_translation::TRANSLATION_SOURCE_UNOBSERVED;
  assert(vm->translate(0, 0, va, 32, begin, uid, &pa, &source) ==
         vm_translation::TRANSLATION_PENDING);
  for (uint64_t cycle = begin; cycle < begin + 80; ++cycle) {
    vm->cycle(cycle);
    const vm_translation::lookup_result result = vm->translate(
        0, 0, va, 32, cycle, uid, &pa, &source);
    if (result == vm_translation::READY) {
      assert(pa == va);
      *source_out = source;
      return cycle + 1;
    }
  }
  assert(false && "translation failed to drain");
  return begin + 80;
}

static uint64_t run_pair(vm_translation::translation_controller *vm,
                         uint64_t va, uint64_t leader_uid,
                         uint64_t follower_uid, uint64_t begin,
                         vm_translation::translation_source expected) {
  uint64_t pa = 0;
  vm_translation::translation_source source =
      vm_translation::TRANSLATION_SOURCE_UNOBSERVED;
  const uint64_t launches_before = vm->stats().l1_lookup_launches;
  assert(vm->translate(0, 0, va, 32, begin, leader_uid, &pa, &source) ==
         vm_translation::TRANSLATION_PENDING);
  assert(vm->stats().l1_lookup_launches == launches_before + 1);
  vm->cycle(begin);
  // Next-cycle per-SID port is available, so this is exactly a physical
  // launch that frozen V1 would admit. The candidate registers a follower
  // instead and launches no second L1 request.
  assert(vm->translate(0, 0, va + 64, 32, begin + 1, follower_uid,
                       &pa, &source) ==
         vm_translation::TRANSLATION_PENDING);
  assert(vm->stats().l1_lookup_launches == launches_before + 1);

  bool follower_done = false;
  bool leader_done = false;
  uint64_t end = begin + 1;
  for (uint64_t cycle = begin + 1; cycle < begin + 100; ++cycle) {
    vm->cycle(cycle);
    if (!follower_done) {
      const vm_translation::lookup_result result = vm->translate(
          0, 0, va + 64, 32, cycle, follower_uid, &pa, &source);
      if (result == vm_translation::READY) {
        assert(pa == va + 64 && source == expected);
        follower_done = true;
      }
    }
    if (!leader_done) {
      const vm_translation::lookup_result result = vm->translate(
          0, 0, va, 32, cycle, leader_uid, &pa, &source);
      if (result == vm_translation::READY) {
        assert(pa == va && source == expected);
        leader_done = true;
      }
    }
    if (follower_done && leader_done) {
      end = cycle + 1;
      break;
    }
  }
  assert(follower_done && leader_done);
  return end;
}

int main() {
  const uint64_t page = 65536;
  vm_translation::translation_controller vm(make_config());
  vm_translation::translation_source source =
      vm_translation::TRANSLATION_SOURCE_UNOBSERVED;

  // Cold page: real L1/L2 miss and PTW leader, with one exact follower.
  uint64_t cycle = run_pair(&vm, 10 * page, 1, 2, 0,
                            vm_translation::TRANSLATION_SOURCE_PTW);

  // The completed cold translation is resident in L1. This pair therefore
  // exercises an actual L1-hit leader.
  cycle = run_pair(&vm, 10 * page + 128, 3, 4, cycle + 2,
                   vm_translation::TRANSLATION_SOURCE_L1_TLB_HIT);

  // Fill another page to evict page 10 from the one-entry L1 while retaining
  // page 10 in the eight-entry L2.
  cycle = drain_one(&vm, 11 * page, 5, cycle + 2, &source);
  assert(source == vm_translation::TRANSLATION_SOURCE_PTW);
  cycle = run_pair(&vm, 10 * page + 256, 6, 7, cycle + 2,
                   vm_translation::TRANSLATION_SOURCE_L2_TLB_HIT);

  assert(vm.stats().l1_lookup_launches < 7);
  assert(vm.stats().completed == 7);
  assert(awma_prel1::exact_coalescer::instance().quiescent());
  assert(vm.quiescent_invariants_hold());
  awma_prel1::exact_coalescer::instance().print(stdout);
  printf("prel1_exact_coalescer_integration_test PASS cycle=%llu\n",
         (unsigned long long)cycle);
  return 0;
}
