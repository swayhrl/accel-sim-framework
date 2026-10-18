#include "dtc-l1-common.h"
#include <cstdio>
#include <deque>
#include <vector>
using namespace dtc_l1;
int main() {
  for(bool finite:{false,true}) for(bool k1:{false,true}) {
    config c;c.selected_mode=mode::PAPER_OO;c.finite_service=finite;
    c.logical_sets=2;c.logical_ways=2;c.physical_lines=5;c.oo_pib_entries=16;
    oo_frontend f(c); // exactly the omitted/default OFF contract in both headers
    std::deque<std::pair<physical_identity,unsigned>> returns;
    std::vector<uint64_t> accepted;
    uint64_t uid=1;
    for(unsigned cycle=1;cycle<=500;++cycle) {
      f.advance_service(cycle);
      if(k1 && cycle%11==0) f.invalidate_lookup(cycle);
      while(!returns.empty() && returns.front().second<=cycle) {
        f.complete(returns.front().first);returns.pop_front();
      }
      if(uid<=80 && f.admit(uid)) {
        const uint64_t address=((uid*7)%9)*128;
        if(f.try_serve_tag(cycle,address)) {
          const auto r=f.access(cycle,uid,address);
          std::printf("%d %d %u %llu %u %u %llu\n",finite,k1,cycle,
            (unsigned long long)uid,(unsigned)r.kind,r.physical.id,
            (unsigned long long)r.physical.generation);
          if(r.kind!=io_access_kind::NO_FREE_LINE) {
            if(r.kind==io_access_kind::NEW_MISS) returns.push_back({r.physical,cycle+5});
            accepted.push_back(uid++);
          }
        }
      }
      for(auto it=accepted.begin();it!=accepted.end();++it) {
        if(f.retire_ready_uid(cycle,*it)) {accepted.erase(it);break;}
      }
      f.assert_shadow_refs();
      if(uid>80 && accepted.empty() && returns.empty()) break;
    }
    assert(uid==81 && !f.occupancy() && !f.active_refs() && returns.empty());
    std::printf("FINAL %d %d %llu %llu %llu %llu %llu %llu %zu\n",finite,k1,
      (unsigned long long)f.new_misses(),(unsigned long long)f.tag_evictions(),
      (unsigned long long)f.no_free_physical_events(),(unsigned long long)f.retires(),
      (unsigned long long)f.map_loss_to_free_count(),
      (unsigned long long)f.map_loss_to_free_sum(),f.allocated_lines());
  }
}
