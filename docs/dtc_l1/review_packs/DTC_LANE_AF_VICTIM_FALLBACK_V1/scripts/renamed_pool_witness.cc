#include "dtc-l1-common.h"
#include <cstdio>
using namespace dtc_l1;
// Natural renamed hidden owner makes a full pool possible even when physical
// entries exceed the total number of directory positions. No real-input claim.
int main() {
#ifdef AF_BASELINE_SIZES
  std::printf("{\"config_bytes\":%zu,\"oo_frontend_bytes\":%zu}\n",sizeof(config),sizeof(oo_frontend));
#else
  std::printf("{\"config_bytes\":%zu,\"oo_frontend_bytes\":%zu}\n",sizeof(config),sizeof(oo_frontend));
  for(bool on:{false,true}) {
    config c;c.selected_mode=mode::PAPER_OO;c.finite_service=true;
    c.logical_sets=1;c.logical_ways=2;c.physical_lines=3;c.oo_pib_entries=8;
    c.reclaimable_victim_fallback=on;
    oo_frontend f(c);
    f.advance_service(1);assert(f.admit(1));auto hidden=f.access(1,1,0).physical;
    f.advance_service(2);assert(f.admit(2));auto a=f.access(2,2,128).physical;f.complete(a);
    f.advance_service(3);assert(f.admit(3));auto b=f.access(3,3,256).physical;f.complete(b);
    f.advance_service(4);assert(f.retire_ready_uid(4,3));
    assert(f.is_allocated(hidden) && !f.tag_visible(hidden) && f.ref_count(hidden)==1);
    assert(f.tag_visible(a) && f.ref_count(a)==1 && f.entry_ready_for(2));
    assert(f.tag_visible(b) && !f.ref_count(b));
    f.advance_service(5);assert(f.admit(4));const auto result=f.access(5,4,384);
    if(on) {
      assert(result.kind==io_access_kind::NEW_MISS && result.physical.id==b.id);
      assert(result.physical.generation==b.generation+1 && f.reclaimable_victim_fallbacks()==1);
    } else assert(result.kind==io_access_kind::NO_FREE_LINE && !f.reclaimable_victim_fallbacks());
    assert(f.is_allocated(hidden) && f.is_allocated(a) && f.ref_count(a)==1);
    f.assert_shadow_refs();
    std::printf("{\"case\":\"AF09_physical_gt_tags_natural_renaming_%s\",\"status\":\"PASS\","
                "\"physical\":3,\"tag_slots\":2,\"fallbacks\":%llu,\"allocated\":%zu}\n",
                on?"ON":"OFF",(unsigned long long)f.reclaimable_victim_fallbacks(),f.allocated_lines());
  }
#endif
}
