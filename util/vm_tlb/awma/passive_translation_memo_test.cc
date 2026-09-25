#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "gpgpu-sim/passive_translation_memo.h"

int main() {
  const uint64_t page = 64ULL * 1024ULL;
  setenv("GPGPUSIM_AWMA_PASSIVE_MEMO_OBSERVER", "1", 1);
  awma_passive_memo::observer &observer =
      awma_passive_memo::observer::instance();
  assert(observer.enabled());

  const uint64_t inst1 = 0x100000001ULL;
  observer.note_decision(inst1, 1, 0, page + 8, page, 0,
                         vm_translation::TRANSLATION_ACCESS_READ);
  observer.note_natural_completion(
      inst1, 1, 0, page + 8, page, 0,
      vm_translation::TRANSLATION_ACCESS_READ, 1);
  observer.note_decision(inst1, 2, 0, page + 16, page, 0,
                         vm_translation::TRANSLATION_ACCESS_READ);
  observer.note_natural_completion(
      inst1, 2, 0, page + 16, page, 0,
      vm_translation::TRANSLATION_ACCESS_READ, 1);
  observer.note_decision(inst1, 3, 0, 2 * page + 8, page, 0,
                         vm_translation::TRANSLATION_ACCESS_READ);
  observer.note_natural_completion(
      inst1, 3, 0, 2 * page + 8, page, 0,
      vm_translation::TRANSLATION_ACCESS_READ, 2);
  observer.note_decision(inst1, 4, 0, page + 24, page, 0,
                         vm_translation::TRANSLATION_ACCESS_READ);
  observer.note_natural_completion(
      inst1, 4, 0, page + 24, page, 0,
      vm_translation::TRANSLATION_ACCESS_READ, 1);
  observer.retire_instruction(inst1);

  const awma_passive_memo::observer_counters &stats = observer.counters();
  assert(stats.natural_translation_completions == 4);
  assert(stats.decision_lookups == 4);
  assert(stats.capacity[0].hits == 1);
  assert(stats.capacity[1].hits == 2);
  assert(stats.capacity[2].hits == 2);
  assert(stats.capacity[0].replacements == 2);
  assert(stats.capacity[1].replacements == 0);
  assert(stats.capacity[2].replacements == 0);
  assert(stats.capacity[0].reuse_distance[0] == 1);
  assert(stats.capacity[1].reuse_distance[0] == 1);
  assert(stats.capacity[1].reuse_distance[1] == 1);
  assert(stats.instructions_retired == 1);
  assert(stats.unique_pages_total == 2);
  assert(stats.unique_pages_max == 2);
  assert(observer.live_instruction_states() == 0);

  // Source-supported legality dimensions are all checked. A permission-like
  // access mismatch and a generation mismatch are misses, never hits.
  const uint64_t inst2 = 0x100000002ULL;
  observer.note_decision(inst2, 5, 7, 3 * page + 8, page, 4,
                         vm_translation::TRANSLATION_ACCESS_READ);
  observer.note_natural_completion(
      inst2, 5, 7, 3 * page + 8, page, 4,
      vm_translation::TRANSLATION_ACCESS_READ, 30);
  observer.note_decision(inst2, 6, 7, 3 * page + 16, page, 4,
                         vm_translation::TRANSLATION_ACCESS_WRITE);
  observer.note_natural_completion(
      inst2, 6, 7, 3 * page + 16, page, 4,
      vm_translation::TRANSLATION_ACCESS_WRITE, 30);
  observer.note_decision(inst2, 7, 7, 3 * page + 24, page, 5,
                         vm_translation::TRANSLATION_ACCESS_WRITE);
  observer.note_natural_completion(
      inst2, 7, 7, 3 * page + 24, page, 5,
      vm_translation::TRANSLATION_ACCESS_WRITE, 30);
  observer.retire_instruction(inst2);
  assert(observer.counters().capacity[2]
             .access_compatibility_mismatches == 1);
  assert(observer.counters().capacity[2]
             .stale_generation_mismatches == 1);
  assert(observer.live_instruction_states() == 0);

  printf("passive_translation_memo_test PASS\n");
  return 0;
}
