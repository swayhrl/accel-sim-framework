#include "gpgpu-sim/shader.h"
#include <cassert>
#include <cstdio>
int main(){
 shd_warp_t w(nullptr,32);warp_inst_t sync, following;
 sync.m_is_warp_sync=true;following.m_is_warp_sync=false;
 w.ibuffer_fill(0,&sync);w.ibuffer_fill(1,&following);
 w.inc_inst_in_pipeline();w.inc_inst_in_pipeline();
 assert(w.num_issued_inst_in_pipeline()==0 && w.stores_done());
 w.inc_inst_in_pipeline();
 assert(w.num_issued_inst_in_pipeline()==1);
 w.dec_inst_in_pipeline();w.inc_store_req();
 assert(w.num_issued_inst_in_pipeline()==0 && !w.stores_done());
 w.dec_store_req();assert(w.stores_done());
 // Removing the current ibuffer entry must happen AFTER the drain check.
 w.ibuffer_free();assert(w.num_issued_inst_in_pipeline()==1);
 assert(!following.m_is_warp_sync);
 puts("CPU_WARP_DRAIN_STATE_PASS buffered_excluded older_blocks stores_block before_ibuffer_free");
}
