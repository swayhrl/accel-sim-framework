#include <assert.h>

#include <iostream>

#include "awma_r101r3_s1_service.h"
#include "awma_transient_l2_policy.h"

using awma_r101r3_s1::accounting;
using awma_r101r3_s1::bounded_path_state;
using awma_r101r3_s1::request_semantics;
using awma_transient_l2::MODE_NONE;
using awma_transient_l2::SERVICE_ACCESS_DEAD_TRANSIENT;
using awma_transient_l2::SERVICE_ACCESS_LIVE_TRANSIENT;
using awma_transient_l2::SERVICE_ACCESS_MULTIPLE_REGIONS;
using awma_transient_l2::SERVICE_ACCESS_PARTIAL_TRANSIENT;
using awma_transient_l2::region_policy;

int main() {
  region_policy policy;
  policy.reset(MODE_NONE);
  policy.configure_region(0, 0x1000, 0x1100, 1, true);
  policy.configure_region(1, 0x1100, 0x1200, 1, true);
  policy.configure_region(2, 0x2000, 0x2100, 1, false);
  policy.configure_region(3, 0x3000, 0x3100, 1, false);

  const awma_transient_l2::service_access live =
      policy.classify_access(0x1040, 32);
  assert(live.kind == SERVICE_ACCESS_LIVE_TRANSIENT);
  assert(live.oracle_eligible());

  request_semantics read;
  read.ordinary_read = true;
  read.request_bytes = 32;
  assert(awma_r101r3_s1::supported(live, read));

  request_semantics write;
  write.ordinary_write = true;
  write.request_bytes = 32;
  assert(awma_r101r3_s1::supported(live, write));

  request_semantics atomic = read;
  atomic.atomic = true;
  assert(!awma_r101r3_s1::supported(live, atomic));

  request_semantics wrong_width = read;
  wrong_width.request_bytes = 64;
  assert(!awma_r101r3_s1::supported(live, wrong_width));

  request_semantics unsupported;
  unsupported.request_bytes = 32;
  assert(!awma_r101r3_s1::supported(live, unsupported));

  const awma_transient_l2::service_access partial =
      policy.classify_access(0x0ff0, 32);
  assert(partial.kind == SERVICE_ACCESS_PARTIAL_TRANSIENT);
  assert(!awma_r101r3_s1::supported(partial, read));

  const awma_transient_l2::service_access multiple =
      policy.classify_access(0x10f0, 32);
  assert(multiple.kind == SERVICE_ACCESS_MULTIPLE_REGIONS);
  assert(!awma_r101r3_s1::supported(multiple, read));

  const awma_transient_l2::line_metadata generation_one = live.metadata;
  assert(policy.is_live(generation_one));
  policy.transition(0, 1, false);
  assert(!policy.is_live(generation_one));
  const awma_transient_l2::service_access dead =
      policy.classify_access(0x1040, 32);
  assert(dead.kind == SERVICE_ACCESS_DEAD_TRANSIENT);
  policy.transition(0, 2, true);
  const awma_transient_l2::service_access generation_two =
      policy.classify_access(0x1040, 32);
  assert(generation_two.kind == SERVICE_ACCESS_LIVE_TRANSIENT);
  assert(generation_two.metadata.generation == 2);
  assert(!policy.is_live(generation_one));

  bounded_path_state path;
  assert(path.can_accept());
  path.data_port_busy = true;
  assert(!path.can_accept());
  path.data_port_busy = false;
  path.return_queue_full = true;
  assert(!path.can_accept());
  path.return_queue_full = false;
  path.dram_queue_full = true;
  assert(!path.can_accept());

  accounting counters;
  counters.serve(false, false, 32, 16);
  counters.serve(false, true, 32, 32);
  counters.serve(true, false, 32, 8);
  assert(counters.reads == 2);
  assert(counters.ldgsts_reads == 1);
  assert(counters.writes == 1);
  assert(counters.request_bytes == 96);
  assert(counters.active_bytes == 56);
  assert(counters.exact());
  counters.duplicates = 1;
  assert(!counters.exact());

  std::cout << "AWMA_R101R3_S1_DIRECTED PASS checks=24\n";
  return 0;
}
