#include <assert.h>
#include <stdint.h>
#include <stdio.h>

#include "awma_r101r2_o2_service.h"
#include "awma_transient_l2_policy.h"

using namespace awma_transient_l2;

static region_policy policy_with_adjacent_regions() {
  region_policy policy;
  policy.reset(MODE_NONE);
  policy.configure_region(0, 0x1000, 0x2000, 1, true);
  policy.configure_region(1, 0x2000, 0x3000, 1, false);
  return policy;
}

int main() {
  unsigned tests = 0;
  region_policy policy = policy_with_adjacent_regions();

  // 1: disjoint traffic remains ordinary.
  service_access access = policy.classify_access(0x4000, 32);
  assert(access.kind == SERVICE_ACCESS_NON_TRANSIENT);
  ++tests;

  // 2: a fully-contained access in a live generation is eligible.
  access = policy.classify_access(0x1080, 128);
  assert(access.kind == SERVICE_ACCESS_LIVE_TRANSIENT);
  assert(access.oracle_eligible() && access.metadata.region_id() == 0);
  ++tests;

  // 3: a fully-contained access in a dead region fails closed.
  access = policy.classify_access(0x2080, 128);
  assert(access.kind == SERVICE_ACCESS_DEAD_TRANSIENT);
  assert(!access.oracle_eligible());
  ++tests;

  // 4: a transaction entering a region from below is not partially serviced.
  access = policy.classify_access(0x0fc0, 128);
  assert(access.kind == SERVICE_ACCESS_PARTIAL_TRANSIENT);
  ++tests;

  // 5: a transaction leaving a region is not partially serviced.
  access = policy.classify_access(0x1fc0, 128);
  assert(access.kind == SERVICE_ACCESS_MULTIPLE_REGIONS);
  ++tests;

  // 6: one transaction intersecting two adjacent regions fails closed.
  access = policy.classify_access(0x1fe0, 64);
  assert(access.kind == SERVICE_ACCESS_MULTIPLE_REGIONS);
  assert(access.intersection_count == 2);
  ++tests;

  // 7: zero-sized service requests are invalid.
  access = policy.classify_access(0x1000, 0);
  assert(access.kind == SERVICE_ACCESS_INVALID_RANGE);
  ++tests;

  // 8: wrapping address ranges are invalid.
  access = policy.classify_access(UINT64_MAX - 15, 32);
  assert(access.kind == SERVICE_ACCESS_INVALID_RANGE);
  ++tests;

  // 9: PRE-like activation makes the configured generation eligible.
  policy.transition(1, 1, true);
  access = policy.classify_access(0x2080, 32);
  assert(access.oracle_eligible());
  ++tests;

  // 10: POST-like death removes eligibility.
  line_metadata generation_one = access.metadata;
  policy.transition(1, 1, false);
  assert(policy.is_dead(generation_one));
  assert(!policy.classify_access(0x2080, 32).oracle_eligible());
  ++tests;

  // 11: generation advance rejects an old token and admits the new token.
  policy.transition(1, 2, true);
  assert(policy.is_dead(generation_one));
  access = policy.classify_access(0x2080, 32);
  assert(access.metadata.generation == 2 && policy.is_live(access.metadata));
  ++tests;

  // 12: service readiness is exactly one modeled cycle after admission.
  assert(awma_r101r2_o2::one_cycle_ready(41) == 42);
  assert(awma_r101r2_o2::is_exact_one_cycle(41, 42, 42));
  assert(!awma_r101r2_o2::is_exact_one_cycle(41, 42, 43));
  ++tests;

  // 13: bypass and non-sector stores use one normal ACK token.
  assert(awma_r101r2_o2::store_ack_tokens(true, true, 128) == 1);
  assert(awma_r101r2_o2::store_ack_tokens(false, false, 128) == 1);
  ++tests;

  // 14: sector-associative stores preserve the original per-sector ACK count.
  assert(awma_r101r2_o2::store_ack_tokens(false, true, 32) == 1);
  assert(awma_r101r2_o2::store_ack_tokens(false, true, 128) == 4);
  ++tests;

  // 15: the exactly-once accounting state machine reaches quiescence.
  awma_r101r2_o2::accounting accounting;
  awma_r101r2_o2::service_state state =
      awma_r101r2_o2::SERVICE_SCHEDULED;
  accounting.admit();
  accounting.make_ready(state);
  accounting.retire(state);
  assert(accounting.quiescent());
  ++tests;

  // 16: a duplicate completion is detected and prevents quiescence.
  accounting.make_ready(state);
  assert(accounting.duplicate == 1 && !accounting.quiescent());
  ++tests;

  // 17: lifecycle hashing changes on a semantic region transition.
  region_policy hash_policy = policy_with_adjacent_regions();
  const uint64_t before = hash_policy.lifecycle_hash();
  hash_policy.transition(1, 1, true);
  assert(before != hash_policy.lifecycle_hash());
  ++tests;

  // 18: ordinary LDG and LDGSTS retain distinct dependency paths.
  assert(awma_r101r2_o2::read_dependency(false) ==
         awma_r101r2_o2::READ_REGISTER_SCOREBOARD);
  assert(awma_r101r2_o2::read_dependency(true) ==
         awma_r101r2_o2::READ_LDGSTS_DEPBAR);
  ++tests;

  printf("AWMA_R101R2_O2_DIRECTED_TESTS PASS tests=%u\n", tests);
  return 0;
}
