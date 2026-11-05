#include "reclaim_scheduler.h"
#include "ep-l2-tvd-directory.h"
#include <cstdio>
using D=ep_l2_tvd_directory<>;using S=reclaim_scheduler<D>;
D::ticket install(D &d,unsigned line,unsigned id,bool dirty,unsigned now){
 auto p=d.preview_install(line,dirty);D::ticket t;
 assert(d.commit_install(p,line,ep_l2::PayloadHandle(id,1),1,dirty?1:0,0,dirty,now,t)==D::OK);return t;
}
void scan(S &s,D &d,unsigned start){for(unsigned i=0;i<d.capacity();++i)s.scan(d,start+i,true);}
int main(){
 {D d(4,true,true);auto c=install(d,0,0,false,1);auto w=install(d,128,4,true,2);
  assert(d.bind_writeback(w,1)==D::OK && d.lower_accept(w,true,3)==D::OK && d.set_done(w,4)==D::OK);
  auto o=d.preview_ticket(c,1,D::READ_OP);D::read_lease l;assert(d.begin_read(o,1,l)==D::OK);assert(d.response_commit(l,5)==D::OK);
  S old,now;assert(old.issue(d,0,6,false)==S::WAIT_SELECTION);assert(now.issue(d,0,6,true)==S::WAIT_SELECTION);
  ep_l2::PayloadHandle h;assert(now.commit_to(d,6,true,h)==S::WAIT_SELECTION);
  scan(old,d,7);scan(now,d,7);assert(old.selected.index==c.index && now.selected.index==w.index);
  assert(now.commit_to(d,10,true,h)==S::WAIT_PORT);assert(now.commit_to(d,11,false,h)==S::WAIT_PORT);
  assert(now.commit_to(d,12,true,h)==S::DONE && h.payload_id==4);
 }
 {D d(4,true,true);auto c=install(d,0,0,false,1);S s;ep_l2::PayloadHandle h;
  s.issue(d,1,2,true);scan(s,d,3);assert(!s.pending);
  s.issue(d,0,7,true);scan(s,d,8);
  auto o=d.preview_ticket(c,1,D::READ_OP);D::read_lease l;assert(d.begin_read(o,1,l)==D::OK);
  assert(s.commit_to(d,12,true,h)==S::PINNED);assert(d.cancel_read(l)==D::OK);
  s.issue(d,0,13,true);scan(s,d,14);assert(d.reclaim(c,h,18)==D::OK);
  auto n=install(d,128,4,false,19);assert(n.incarnation!=c.incarnation);
  assert(s.commit_to(d,20,true,h)==S::STALE);
 }
 {D d(4,true,true);auto w=install(d,0,0,true,1);S s;s.issue(d,0,2,true);scan(s,d,3);assert(!s.pending);
  assert(d.bind_writeback(w,2)==D::OK && d.lower_accept(w,true,7)==D::OK);s.issue(d,0,8,true);scan(s,d,9);assert(!s.pending);
 }
 puts("V5_RECLAIM_CYCLE_MODEL_PASS|cases=3|scan=one_row_per_cycle|update_lane=1|production_capacity_scan_cycles=128|checks=clean_vs_complete,bank,pin,stale,mandatory,port_backpressure");
}
