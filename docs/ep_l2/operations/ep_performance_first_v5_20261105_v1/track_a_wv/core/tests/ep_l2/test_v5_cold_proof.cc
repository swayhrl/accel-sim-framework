#include "../../src/gpgpu-sim/ep-l2-tvd-directory.h"
#include <cstdio>
using D=ep_l2_tvd_directory<>;
int main(){
  for(bool dirty:{false,true}) {
    D d(1,true,true);D::ticket t;ep_l2::PayloadHandle h(0,1);
    assert(d.never_installed());
    auto p=d.preview_install(0,dirty);
    assert(d.commit_install(p,0,h,1,dirty?1:0,1,dirty,1,t)==D::INVALID_INPUT);
    assert(d.never_installed()); // unsuccessful producer never sets false-positive
    assert(d.commit_install(p,0,h,1,dirty?1:0,0,dirty,1,t)==D::OK);
    assert(!d.never_installed() && d.occupied()==1); // SET precedes visibility
    const auto o=d.preview_ticket(t,1,D::READ_OP);D::read_lease l;
    assert(o.status==D::READ_READY && d.begin_read(o,1,l)==D::OK);
    ep_l2::PayloadHandle released;
    assert(d.reclaim(t,released,1)==(dirty?D::WAIT_WRITEBACK:D::PINNED));
    assert(!d.never_installed());
    assert(d.cancel_read(l)==D::OK);
    if(dirty) {
      assert(d.bind_writeback(t,23)==D::OK);
      assert(d.lower_accept(t,false,2)==D::DATA_TRANSFER_UNPROVEN);
      assert(d.lower_accept(t,true,2)==D::OK);
      assert(!d.epoch_ready() && !d.never_installed());
      assert(d.set_done(t,3)==D::OK);
    }
    assert(d.reclaim(t,released,4)==D::OK);
    assert(!d.occupied() && !d.never_installed()); // sticky; no unsafe empty reset
    assert(d.reclaim(t,released,4)==D::STALE);
    auto q=d.preview_install(128,true);
    assert(d.commit_install(q,128,h,1,1,0,true,5,t)==D::OK);
    assert(d.rollback_staged(t,6)==D::OK);
    assert(!d.occupied() && !d.never_installed());
  }
  printf("V5_COLD_PROOF_PASS|profiles=2|checks=failed_commit,set_before_visible,reader_pin,mandatory_WB,lower_data,stale_ticket,rollback,sticky_empty\n");
}
