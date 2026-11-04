#include <cassert>
#include <iostream>
#include <map>
#include <vector>
#include "/root/data/dtc_failure_repair_20261025_v1/core/src/gpgpu-sim/dtc-l1-common.h"
int main() {
 struct Case {const char* name;unsigned sets,ways,pool;bool expect_block;};
 for(const Case test:std::vector<Case>{{"tag64x16_pool640",64,16,640,true},{"tag128x8_pool640",128,8,640,true},{"baseline64x8_pool640",64,8,640,false},{"physical768_tag64x8",64,8,768,false},{"physical1024_tag64x8",64,8,1024,false}}) {
  dtc_l1::config cfg;cfg.finite_service=true;cfg.selected_mode=dtc_l1::mode::PAPER_OO;cfg.logical_sets=test.sets;cfg.logical_ways=test.ways;cfg.physical_lines=test.pool;cfg.tag_hash_bankrow=true;
  dtc_l1::oo_frontend f(cfg);std::map<unsigned,unsigned> occupancy;
  for(unsigned i=0;i<640;++i){const uint64_t cycle=3*i,address=128ULL*i,uid=i+1;f.advance_service(cycle);assert(f.admit(uid));assert(f.try_serve_tag(cycle,address));auto access=f.access(cycle,uid,address);assert(access.kind==dtc_l1::io_access_kind::NEW_MISS);f.complete(access.physical);f.advance_service(cycle+1);uint64_t retired=0;assert(f.retire_one_ready(cycle+1,&retired)&&retired==uid);++occupancy[dtc_l1::logical_tag_set(address,test.sets,true)];}
  assert(f.retires()==640 && f.active_refs()==0);const auto allocated=f.allocated_lines(), evictions=f.tag_evictions();assert(f.admit(10000));unsigned blocked=0;bool progressed=false;
  for(unsigned step=0;step<32;++step){const uint64_t cycle=2000+step*3,address=128ULL*640;f.advance_service(cycle);assert(f.try_serve_tag(cycle,address));auto access=f.access(cycle,10000,address);
   if(access.kind==dtc_l1::io_access_kind::NO_FREE_LINE){++blocked;assert(f.allocated_lines()==allocated&&f.active_refs()==0&&f.tag_evictions()==evictions);}
   else {assert(access.kind==dtc_l1::io_access_kind::NEW_MISS);progressed=true;f.complete(access.physical);f.advance_service(cycle+1);uint64_t retired=0;assert(f.retire_one_ready(cycle+1,&retired)&&retired==10000);break;}
  }
  assert(test.expect_block?(blocked==32&&!progressed&&allocated==640&&evictions==0):progressed);
  unsigned lo=640,hi=0;for(const auto& x:occupancy){lo=std::min(lo,x.second);hi=std::max(hi,x.second);}assert(occupancy.size()==test.sets);
  std::cout<<"{\"case\":\""<<test.name<<"\",\"sets\":"<<test.sets<<",\"ways\":"<<test.ways<<",\"physical_lines\":"<<test.pool<<",\"retired_before_probe\":640,\"allocated_before_probe\":"<<allocated<<",\"active_refs_before_probe\":0,\"tag_evictions_before_probe\":"<<evictions<<",\"set_observed_min\":"<<lo<<",\"set_observed_max\":"<<hi<<",\"blocked_retry_cycles\":"<<blocked<<",\"progressed\":"<<(progressed?"true":"false")<<"}\n";
 }
}
