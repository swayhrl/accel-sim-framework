
#include <array>
#include <cassert>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <utility>
#define private public
#include "/root/data/ep_l2_full_workload_performance_20261027_v1/research/next_cost_aware_architecture_20261107_v1/agent_a/core/src/gpgpu-sim/ep-l2-tvd-directory.h"
#undef private
#include <cstdio>
int main() {
 typedef ep_l2_tvd_directory<> D;const auto max=std::numeric_limits<std::uint64_t>::max();
 D b(128,true,true);auto p=b.preview_install(128,false,true);D::ticket t;
 b.m_creation_epoch=max;
 assert(b.commit_install(p,128,ep_l2::PayloadHandle(1,1),1,0,0,false,0,t)==D::INVALID_INPUT);
 assert(b.occupied()==0 && b.creation_epoch()==max);
 b.m_creation_epoch=0;
 assert(b.commit_install(p,128,ep_l2::PayloadHandle(1,1),1,0,0,false,0,t)==D::OK);
 auto promotion=b.preview_dirty_promotion(t,256,ep_l2::PayloadHandle(2,1),1,1,0,true,true);
 b.m_creation_epoch=max;ep_l2::PayloadHandle out;D::ticket wb;
 assert(b.commit_dirty_promotion(promotion,0,out,wb)==D::INVALID_INPUT);
 assert(b.at(t.index).line==128 && b.live(t) && !b.mandatory());
 D full(128,true,true),ext(128,true,false);
 for(unsigned i=0;i<128;++i){auto q=full.preview_install(i*128,false,true);D::ticket v;
  assert(full.commit_install(q,i*128,ep_l2::PayloadHandle(i,1),1,0,0,false,0,v)==D::OK);}
 auto bp=full.preview_install(128*128,false,true);
 auto xp=ext.preview_clean_slot(0,full.at(bp.index).line,true);ext.m_creation_epoch=max;
 const auto epoch=full.creation_epoch();
 assert(full.commit_clean_spill(bp,ext,xp,128*128,ep_l2::PayloadHandle(128,1),1,1,t,out)!=D::OK);
 assert(full.creation_epoch()==epoch && full.occupied()==128 && ext.occupied()==0);
 puts("PASS optional_creation_epoch_overflow_before_Base_install_dirty_rebind_dualrow_publication");
}
