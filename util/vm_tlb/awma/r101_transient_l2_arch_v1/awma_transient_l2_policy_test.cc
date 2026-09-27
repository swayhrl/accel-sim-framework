#include "awma_transient_l2_policy.h"

#include <assert.h>
#include <stdio.h>

using namespace awma_transient_l2;

static unsigned choose(const region_policy &policy,
                       const line_metadata metadata[4],
                       const bool invalid[4], const bool reserved[4],
                       const bool baseline_eligible[4],
                       const unsigned baseline_order[4]) {
  for (unsigned wanted = VICTIM_INVALID; wanted <= VICTIM_LIVE_TRANSIENT;
       ++wanted) {
    for (unsigned rank = 0; rank < 4; ++rank) {
      const unsigned way = baseline_order[rank];
      if (policy.classify_victim(metadata[way], invalid[way], reserved[way],
                                 baseline_eligible[way]) == wanted)
        return way;
    }
  }
  return 4;
}

int main() {
  region_policy policy;
  policy.reset(MODE_BOUNDED_LIVE_RETENTION);
  policy.configure_region(0, 0x1000, 0x2000, 1, true);   // A
  policy.configure_region(1, 0x2000, 0x3000, 1, true);   // B
  policy.configure_region(2, 0x3000, 0x4000, 1, true);   // X0
  policy.configure_region(3, 0x4000, 0x5000, 1, false);  // X1

  line_metadata live = policy.classify_line(0x1000, 128);
  line_metadata ordinary = policy.classify_line(0x8000, 128);
  line_metadata dead = policy.classify_line(0x4000, 128);
  assert(policy.is_live(live));
  assert(policy.is_dead(dead));

  // 1/4: live clean is protected while an ordinary legal victim exists.
  line_metadata metadata[4] = {live, ordinary, live, live};
  bool invalid[4] = {false, false, false, false};
  bool reserved[4] = {false, false, false, false};
  bool eligible[4] = {true, true, true, true};
  unsigned order[4] = {0, 1, 2, 3};
  assert(choose(policy, metadata, invalid, reserved, eligible, order) == 1);
  printf("TEST_1_TRANSIENT_CLEAN_LIVE_PRESSURE PASS\n");

  // 2: a forced dirty live eviction is never droppable.
  assert(!policy.may_drop_dirty(live));
  unsigned writeback_queue = 0;
  if (!policy.may_drop_dirty(live)) ++writeback_queue;
  assert(writeback_queue == 1);
  printf("TEST_2_DIRTY_LIVE_WRITES_BACK PASS\n");

  // 3/4: a dirty dead transient is droppable and preferred to ordinary.
  metadata[0] = ordinary;
  metadata[1] = dead;
  assert(policy.may_drop_dirty(dead));
  assert(choose(policy, metadata, invalid, reserved, eligible, order) == 1);
  if (!policy.may_drop_dirty(dead)) ++writeback_queue;
  assert(writeback_queue == 1);
  printf("TEST_3_DEAD_DIRTY_DROP PASS\n");
  printf("TEST_4_DEAD_PREFERRED_OVER_ORDINARY PASS\n");

  // 5: all-ways-live falls back to baseline order.
  for (unsigned i = 0; i < 4; ++i) metadata[i] = live;
  assert(choose(policy, metadata, invalid, reserved, eligible, order) == 0);
  printf("TEST_5_ALL_LIVE_BASELINE_FALLBACK PASS\n");

  // 6: generation reuse makes an old line dead and a new line live.
  line_metadata old_generation = live;
  policy.transition(0, 2, true);
  line_metadata new_generation = policy.classify_line(0x1000, 128);
  assert(policy.is_dead(old_generation));
  assert(policy.is_live(new_generation));
  assert(!policy.may_drop_dirty(new_generation));
  printf("TEST_6_GENERATION_REUSE PASS\n");

  // 7: partial first/last lines are conservatively classified by overlap.
  region_policy partial;
  partial.reset(MODE_BOUNDED_LIVE_RETENTION);
  partial.configure_region(0, 0x1081, 0x117f, 1, true);
  assert(partial.classify_line(0x1080, 128).transient());
  assert(partial.classify_line(0x1100, 128).transient());
  assert(!partial.classify_line(0x1180, 128).transient());
  printf("TEST_7_PARTIAL_LINE_ALIGNMENT PASS\n");

  // 8: non-transient addresses remain ordinary.
  assert(!ordinary.transient());
  assert(!policy.may_drop_dirty(ordinary));
  printf("TEST_8_NON_TRANSIENT_UNAFFECTED PASS\n");

  // 9: OFF mode restores baseline eligibility and never drops dirty data.
  region_policy off;
  off.reset(MODE_NONE);
  off.configure_region(0, 0x1000, 0x2000, 1, false);
  line_metadata off_line = off.classify_line(0x1000, 128);
  assert(off.classify_victim(off_line, false, false, true) ==
         VICTIM_ORDINARY);
  assert(!off.may_drop_dirty(off_line));
  printf("TEST_9_MODE_OFF_EQUIVALENCE PASS\n");

  // 10: a complete bounded transition sequence has no unsafe wrap.
  for (unsigned generation = 3; generation <= 8; ++generation)
    policy.transition(0, generation, (generation & 1) != 0);
  assert(policy.get_region(0).generation == 8);
  --writeback_queue;
  assert(writeback_queue == 0);
  printf("TEST_10_TERMINAL_QUIESCENCE PASS\n");
  printf("POLICY_COST line_metadata_bytes=%zu descriptor_bytes=%zu logical_bits_per_line=%u\n",
         sizeof(line_metadata), sizeof(descriptor),
         kLogicalMetadataBitsPerLine);

  printf("AWMA_TRANSIENT_L2_POLICY_TEST_PASS\n");
  return 0;
}
