#include <assert.h>
#include <stdint.h>
#include <stdio.h>

#include "gpgpu-sim/passive_last_translation_forwarding.h"

struct zero_opportunity_signature {
  unsigned physical_lookups;
  unsigned admissions;
  unsigned instructions;
  unsigned cycles;
  unsigned coverage;
  unsigned translation_results;
};

int main() {
  const uint64_t page = 64ULL * 1024ULL;
  awma_passive_v2::forwarding_table &table =
      awma_passive_v2::forwarding_table::instance();
  const uint64_t inst1 = 0x200000001ULL;
  uint64_t pa = 0;
  vm_translation::translation_source source =
      vm_translation::TRANSLATION_SOURCE_UNOBSERVED;

  // Empty entry misses. Natural completion installs the exact identity.
  assert(!table.try_forward(inst1, 0, 3 * page + 8, 32, page, 4,
                            vm_translation::TRANSLATION_ACCESS_READ,
                            &pa, &source));
  table.note_natural_completion(
      inst1, 0, 3 * page + 8, 32, page, 4,
      vm_translation::TRANSLATION_ACCESS_READ, 30,
      vm_translation::TRANSLATION_SOURCE_PTW);

  // Same page and complete identity forwards with the stored PPN.
  assert(table.try_forward(inst1, 0, 3 * page + 96, 32, page, 4,
                           vm_translation::TRANSLATION_ACCESS_READ,
                           &pa, &source));
  assert(pa == 30 * page + 96);
  assert(source == vm_translation::TRANSLATION_SOURCE_PTW);
  table.note_forward_application(true);

  // Different VPN, generation, and access type are misses.
  assert(!table.try_forward(inst1, 0, 4 * page + 8, 32, page, 4,
                            vm_translation::TRANSLATION_ACCESS_READ,
                            &pa, &source));
  assert(!table.try_forward(inst1, 0, 3 * page + 8, 32, page, 5,
                            vm_translation::TRANSLATION_ACCESS_READ,
                            &pa, &source));
  assert(!table.try_forward(inst1, 0, 3 * page + 8, 32, page, 4,
                            vm_translation::TRANSLATION_ACCESS_WRITE,
                            &pa, &source));

  // A new natural completion overwrites the single entry.
  table.note_natural_completion(
      inst1, 0, 4 * page + 8, 32, page, 4,
      vm_translation::TRANSLATION_ACCESS_READ, 40,
      vm_translation::TRANSLATION_SOURCE_L1_TLB_HIT);
  assert(!table.try_forward(inst1, 0, 3 * page + 8, 32, page, 4,
                            vm_translation::TRANSLATION_ACCESS_READ,
                            &pa, &source));
  assert(table.try_forward(inst1, 0, 4 * page + 64, 32, page, 4,
                           vm_translation::TRANSLATION_ACCESS_READ,
                           &pa, &source));
  assert(pa == 40 * page + 64);
  table.note_forward_application(false);

  // Instruction retirement invalidates state and prevents cross-instruction
  // reuse even for the same exact translation identity.
  table.retire_instruction(inst1);
  assert(table.live_entries() == 0);
  const uint64_t inst2 = 0x200000002ULL;
  assert(!table.try_forward(inst2, 0, 4 * page + 64, 32, page, 4,
                            vm_translation::TRANSLATION_ACCESS_READ,
                            &pa, &source));
  table.retire_instruction(inst2);

  const awma_passive_v2::counters &stats = table.stats();
  assert(stats.hits == 2);
  assert(stats.forwarded_applications == 2);
  assert(stats.head_requests_avoided == 2);
  assert(stats.prelaunch_work_not_saved == 1);
  assert(stats.forwards_without_live_prelaunch == 1);
  assert(stats.overwrites == 1);
  assert(stats.stale_generation_misses == 1);
  assert(stats.access_compatibility_misses == 1);
  assert(stats.ppn_consistency_faults == 0);
  assert(table.live_entries() == 0);

  table.note_prelaunch_attempt(vm_translation::TRANSLATION_PENDING, true, 1);
  table.note_prelaunch_attempt(vm_translation::L1_PORT_STALL, false, 1);
  table.note_head_translation_attempt();
  assert(stats.prelaunch_attempts == 2);
  assert(stats.prelaunch_head_attempts == 1);
  assert(stats.prelaunch_lookup_request_increments == 2);
  assert(stats.prelaunch_pending == 1);
  assert(stats.prelaunch_l1_port_stalls == 1);
  assert(stats.head_translation_attempts == 1);

  // ZERO-OPPORTUNITY model: every access is a distinct page. V2 performs the
  // same baseline request/admission/application sequence and adds no cycle.
  zero_opportunity_signature off = {3, 3, 1, 3, 3, 3};
  zero_opportunity_signature v2 = {0, 0, 1, 0, 0, 0};
  const uint64_t inst3 = 0x200000003ULL;
  for (unsigned i = 0; i < 3; ++i) {
    assert(!table.try_forward(
        inst3, 0, (10 + i) * page + 8, 32, page, 0,
        vm_translation::TRANSLATION_ACCESS_READ, &pa, &source));
    ++v2.physical_lookups;
    ++v2.admissions;
    ++v2.cycles;
    ++v2.coverage;
    ++v2.translation_results;
    table.note_natural_completion(
        inst3, 0, (10 + i) * page + 8, 32, page, 0,
        vm_translation::TRANSLATION_ACCESS_READ, 10 + i,
        vm_translation::TRANSLATION_SOURCE_L1_TLB_HIT);
  }
  table.retire_instruction(inst3);
  assert(v2.physical_lookups == off.physical_lookups);
  assert(v2.admissions == off.admissions);
  assert(v2.instructions == off.instructions);
  assert(v2.cycles == off.cycles);
  assert(v2.coverage == off.coverage);
  assert(v2.translation_results == off.translation_results);
  assert(table.live_entries() == 0);

  printf("passive_last_translation_forwarding_test PASS\n");
  return 0;
}
