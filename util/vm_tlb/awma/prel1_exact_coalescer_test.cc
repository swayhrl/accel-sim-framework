#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "gpgpu-sim/prel1_exact_coalescer.h"

using awma_prel1::exact_coalescer;
using awma_prel1::request_decision;

static const uint64_t kPage = 65536;

static request_decision decide(uint64_t uid, uint64_t vpn, uint64_t generation,
                               vm_translation::translation_access access,
                               uint64_t cycle, unsigned asid = 0) {
  return exact_coalescer::instance().decide_new_request(
      0, uid, asid, vpn, kPage, generation, access, cycle);
}

static void launch(uint64_t uid, uint64_t vpn, uint64_t generation,
                   vm_translation::translation_access access,
                   uint64_t cycle, unsigned asid = 0) {
  exact_coalescer::instance().note_leader_launch(
      0, uid, asid, vpn, kPage, generation, access, cycle);
}

static void complete(uint64_t uid, uint64_t ppn,
                     vm_translation::translation_source source,
                     uint64_t cycle) {
  exact_coalescer::instance().note_leader_completion(
      0, uid, ppn, source, cycle);
}

static awma_prel1::follower_poll_result poll(
    uint64_t uid, uint64_t vpn, uint64_t generation,
    vm_translation::translation_access access, uint64_t cycle,
    bool consume, uint64_t *pa, vm_translation::translation_source *source,
    unsigned asid = 0) {
  return exact_coalescer::instance().poll_follower(
      0, uid, asid, vpn, kPage, generation, access,
      vpn * kPage + 128, cycle, consume, pa, source);
}

static void run_main() {
  exact_coalescer &coal = exact_coalescer::instance();
  assert(coal.enabled() && !coal.grouping_only_control());
  assert(coal.compare_latency() == 0);

  // Unique request follows baseline and covers an L1-hit leader.
  assert(decide(1, 1, 1, vm_translation::TRANSLATION_ACCESS_READ, 1) ==
         awma_prel1::REQUEST_BASELINE_LEADER);
  launch(1, 1, 1, vm_translation::TRANSLATION_ACCESS_READ, 1);
  complete(1, 1, vm_translation::TRANSLATION_SOURCE_L1_TLB_HIT, 3);

  // Same-cycle follower, L2 leader, non-consuming READY observation, then
  // exactly one consuming application.
  assert(decide(10, 10, 1, vm_translation::TRANSLATION_ACCESS_READ, 10) ==
         awma_prel1::REQUEST_BASELINE_LEADER);
  launch(10, 10, 1, vm_translation::TRANSLATION_ACCESS_READ, 10);
  assert(decide(11, 10, 1, vm_translation::TRANSLATION_ACCESS_READ, 10) ==
         awma_prel1::REQUEST_REGISTERED_FOLLOWER);
  uint64_t pa = 0;
  vm_translation::translation_source source =
      vm_translation::TRANSLATION_SOURCE_UNOBSERVED;
  assert(poll(11, 10, 1, vm_translation::TRANSLATION_ACCESS_READ, 11,
              true, &pa, &source) == awma_prel1::FOLLOWER_WAITING);
  complete(10, 100, vm_translation::TRANSLATION_SOURCE_L2_TLB_HIT, 20);
  assert(poll(11, 10, 1, vm_translation::TRANSLATION_ACCESS_READ, 20,
              false, &pa, &source) == awma_prel1::FOLLOWER_READY);
  assert(pa == 100 * kPage + 128);
  assert(poll(11, 10, 1, vm_translation::TRANSLATION_ACCESS_READ, 20,
              true, &pa, &source) == awma_prel1::FOLLOWER_READY);
  assert(poll(11, 10, 1, vm_translation::TRANSLATION_ACCESS_READ, 21,
              true, &pa, &source) == awma_prel1::FOLLOWER_NOT_REGISTERED);

  // Cross-cycle follower and PTW leader.
  assert(decide(20, 20, 1, vm_translation::TRANSLATION_ACCESS_READ, 30) ==
         awma_prel1::REQUEST_BASELINE_LEADER);
  launch(20, 20, 1, vm_translation::TRANSLATION_ACCESS_READ, 30);
  assert(decide(21, 20, 1, vm_translation::TRANSLATION_ACCESS_READ, 31) ==
         awma_prel1::REQUEST_REGISTERED_FOLLOWER);
  complete(20, 200, vm_translation::TRANSLATION_SOURCE_PTW, 40);
  assert(poll(21, 20, 1, vm_translation::TRANSLATION_ACCESS_READ, 40,
              true, &pa, &source) == awma_prel1::FOLLOWER_READY);

  // VPN/ASID/generation/access mismatches never merge. Keep the exact leader
  // live and reuse the second entry serially for each mismatch.
  assert(decide(30, 30, 1, vm_translation::TRANSLATION_ACCESS_READ, 50) ==
         awma_prel1::REQUEST_BASELINE_LEADER);
  launch(30, 30, 1, vm_translation::TRANSLATION_ACCESS_READ, 50);
  assert(decide(31, 31, 1, vm_translation::TRANSLATION_ACCESS_READ, 50) ==
         awma_prel1::REQUEST_BASELINE_LEADER);
  launch(31, 31, 1, vm_translation::TRANSLATION_ACCESS_READ, 50);
  complete(31, 31, vm_translation::TRANSLATION_SOURCE_L1_TLB_HIT, 51);
  assert(decide(32, 30, 1, vm_translation::TRANSLATION_ACCESS_READ, 52, 1) ==
         awma_prel1::REQUEST_BASELINE_LEADER);
  launch(32, 30, 1, vm_translation::TRANSLATION_ACCESS_READ, 52, 1);
  complete(32, 30, vm_translation::TRANSLATION_SOURCE_L1_TLB_HIT, 53);
  assert(decide(33, 30, 2, vm_translation::TRANSLATION_ACCESS_READ, 54) ==
         awma_prel1::REQUEST_BASELINE_LEADER);
  launch(33, 30, 2, vm_translation::TRANSLATION_ACCESS_READ, 54);
  complete(33, 30, vm_translation::TRANSLATION_SOURCE_L1_TLB_HIT, 55);
  assert(decide(34, 30, 1, vm_translation::TRANSLATION_ACCESS_WRITE, 56) ==
         awma_prel1::REQUEST_BASELINE_LEADER);
  launch(34, 30, 1, vm_translation::TRANSLATION_ACCESS_WRITE, 56);
  complete(34, 30, vm_translation::TRANSLATION_SOURCE_L1_TLB_HIT, 57);

  // Two live entries make a third distinct request baseline fallback.
  assert(decide(35, 35, 1, vm_translation::TRANSLATION_ACCESS_READ, 58) ==
         awma_prel1::REQUEST_BASELINE_LEADER);
  launch(35, 35, 1, vm_translation::TRANSLATION_ACCESS_READ, 58);
  assert(decide(36, 36, 1, vm_translation::TRANSLATION_ACCESS_READ, 58) ==
         awma_prel1::REQUEST_ENTRY_FULL_PASSTHROUGH);
  complete(35, 35, vm_translation::TRANSLATION_SOURCE_L1_TLB_HIT, 59);
  complete(30, 30, vm_translation::TRANSLATION_SOURCE_L1_TLB_HIT, 59);

  // Fixed 32-waiter bound. The 33rd exact follower takes baseline fallback.
  assert(decide(100, 100, 1, vm_translation::TRANSLATION_ACCESS_READ, 100) ==
         awma_prel1::REQUEST_BASELINE_LEADER);
  launch(100, 100, 1, vm_translation::TRANSLATION_ACCESS_READ, 100);
  for (uint64_t i = 0; i < 32; ++i)
    assert(decide(101 + i, 100, 1,
                  vm_translation::TRANSLATION_ACCESS_READ, 101 + i) ==
           awma_prel1::REQUEST_REGISTERED_FOLLOWER);
  assert(decide(200, 100, 1, vm_translation::TRANSLATION_ACCESS_READ, 140) ==
         awma_prel1::REQUEST_WAITER_FULL_PASSTHROUGH);
  complete(100, 1000, vm_translation::TRANSLATION_SOURCE_PTW, 150);
  for (uint64_t i = 0; i < 32; ++i)
    assert(poll(101 + i, 100, 1, vm_translation::TRANSLATION_ACCESS_READ,
                151 + i, true, &pa, &source) ==
           awma_prel1::FOLLOWER_READY);
  assert(coal.quiescent());
  coal.print(stdout);
}

static void run_control() {
  exact_coalescer &coal = exact_coalescer::instance();
  assert(coal.enabled() && coal.grouping_only_control());
  assert(decide(1, 1, 1, vm_translation::TRANSLATION_ACCESS_READ, 1) ==
         awma_prel1::REQUEST_BASELINE_LEADER);
  launch(1, 1, 1, vm_translation::TRANSLATION_ACCESS_READ, 1);
  assert(decide(2, 1, 1, vm_translation::TRANSLATION_ACCESS_READ, 2) ==
         awma_prel1::REQUEST_CONTROL_GROUPED_PASSTHROUGH);
  complete(1, 1, vm_translation::TRANSLATION_SOURCE_L1_TLB_HIT, 3);
  assert(coal.quiescent());
  coal.print(stdout);
}

static void run_plus_one() {
  exact_coalescer &coal = exact_coalescer::instance();
  assert(coal.enabled() && coal.compare_latency() == 1);
  assert(decide(1, 1, 1, vm_translation::TRANSLATION_ACCESS_READ, 1) ==
         awma_prel1::REQUEST_COMPARE_DELAY);
  assert(decide(1, 1, 1, vm_translation::TRANSLATION_ACCESS_READ, 2) ==
         awma_prel1::REQUEST_BASELINE_LEADER);
  launch(1, 1, 1, vm_translation::TRANSLATION_ACCESS_READ, 2);
  assert(decide(2, 1, 1, vm_translation::TRANSLATION_ACCESS_READ, 2) ==
         awma_prel1::REQUEST_COMPARE_DELAY);
  assert(decide(2, 1, 1, vm_translation::TRANSLATION_ACCESS_READ, 3) ==
         awma_prel1::REQUEST_REGISTERED_FOLLOWER);
  complete(1, 1, vm_translation::TRANSLATION_SOURCE_L1_TLB_HIT, 4);
  uint64_t pa = 0;
  vm_translation::translation_source source =
      vm_translation::TRANSLATION_SOURCE_UNOBSERVED;
  assert(poll(2, 1, 1, vm_translation::TRANSLATION_ACCESS_READ, 4,
              true, &pa, &source) == awma_prel1::FOLLOWER_READY);
  assert(coal.quiescent());
  coal.print(stdout);
}

int main(int argc, char **argv) {
  assert(argc == 2);
  if (strcmp(argv[1], "main") == 0)
    run_main();
  else if (strcmp(argv[1], "control") == 0)
    run_control();
  else if (strcmp(argv[1], "plus_one") == 0)
    run_plus_one();
  else
    return 2;
  return 0;
}
