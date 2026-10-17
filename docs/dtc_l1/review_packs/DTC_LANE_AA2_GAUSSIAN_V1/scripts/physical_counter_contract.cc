// Standalone CPU counter oracle against a byte-bound production header.
// No trace, GPU model cycle loop, new Core runtime, or performance observation.
#include "dtc-l1-common.h"
#include <cstdio>

using namespace dtc_l1;

static config frozen_config() {
  config c;
  c.selected_mode=mode::PAPER_OO;
  c.logical_sets=32; c.logical_ways=4;
  c.physical_lines=640; c.oo_pib_entries=128;
  c.finite_service=true;
  return c;
}

static bool balanced(const oo_frontend &f, uint64_t source_reclaims) {
  return f.new_misses()==f.allocated_lines()+f.immediate_reclaims()+
      f.final_ref_reclaims()+source_reclaims;
}

int main() {
  oo_frontend ready(frozen_config());
  ready.advance_service(1);
  assert(ready.admit(1));
  auto id=ready.access(1,1,0).physical;
  ready.complete(id);
  ready.advance_service(2);
  assert(ready.retire_ready_uid(2,1));
  assert(balanced(ready,0));
  assert(ready.allocated_lines()==1 && ready.active_refs()==0);
  auto event=ready.invalidate_lookup(5);
  assert(event.changed==1 && event.reclaimed==1 && event.retained==0);
  assert(!balanced(ready,0)); // Negative witness: old equation omits new release.
  assert(balanced(ready,event.reclaimed));
  assert(ready.map_loss_to_free_count()==ready.immediate_reclaims()+
      ready.final_ref_reclaims()+event.reclaimed);
  assert(ready.invalidate_lookup(6).changed==0);
  assert(ready.map_loss_to_free_count()==1);

  oo_frontend live(frozen_config());
  live.advance_service(1);
  assert(live.admit(1));
  auto old=live.access(1,1,0).physical;
  auto retained=live.invalidate_lookup(1);
  assert(retained.changed==1 && retained.retained==1 && retained.reclaimed==0);
  assert(live.is_allocated(old) && live.ref_count(old)==1);
  assert(balanced(live,retained.reclaimed));
  live.complete(old);
  live.advance_service(2);
  assert(live.retire_ready_uid(2,1));
  assert(live.final_ref_reclaims()==1 && live.allocated_lines()==0);
  assert(balanced(live,retained.reclaimed));
  assert(live.map_loss_to_free_count()==live.immediate_reclaims()+
      live.final_ref_reclaims()+retained.reclaimed);
  std::puts("{\"status\":\"PASS_CPU_COUNTER_CONTRACT_ONLY\","
    "\"ready_ref0_source_reclaims\":1,\"retained_then_final_ref_reclaims\":1,"
    "\"old_equation_negative_witness\":true,\"simulator_starts\":0}");
}
