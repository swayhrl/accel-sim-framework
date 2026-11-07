#include "ep-l2-tvd-directory.h"
#include <cassert>
#include <limits>
#include <cstdio>
using P=ep_l2_quota_row_port;using D=ep_l2_tvd_directory<>;
int main(){
 P p(2);P::key a(4,1,0,1),b(11,2,0,1);
 p.ready(a,0);p.ready(b,0);p.tick(1);
 assert(p.pending()==1&&p.stats().row_conflicts==1);
 p.tick(2);assert(p.ready(a,2));p.commit(a,2);
 p.tick(3);assert(!p.ready(b,3));p.tick(4);assert(p.ready(b,4));p.commit(b,4);
 assert(p.stats().read_beats==2&&p.stats().commit_beats==2);
 puts("PASS SAME_ROW_K2_DEFERRED_SECOND_READ_NOT_FREE");
 D d(2,true,true,2);d.enable_timed_service(true);d.service_tick(1);
 D::ticket t;auto plan=d.selected_install(0,false,0);
 D::service_token tok;tok.valid=true;tok.index=0;tok.incarnation=0;tok.tick=1;
 assert(d.commit_install(plan,0,ep_l2::PayloadHandle(4,1),1,0,0,false,1,t,&tok)==D::OK);
 d.service_tick(2);auto observation=d.preview_access(0,1,D::READ_OP,0,2);
 D::read_lease lease;tok.incarnation=999;tok.tick=2;
 assert(d.begin_read(observation,1,lease,&tok)==D::ROW_PORT_BUSY&&d.at(0).readers==0);
 tok.incarnation=t.incarnation;
 assert(d.begin_read(observation,1,lease,&tok)==D::OK&&d.at(0).readers==1);
 ep_l2::PayloadHandle released;
 assert(d.reclaim(t,released,2,&tok)==D::PINNED&&d.clean_occupancy()==1);
 assert(d.cancel_read(lease,&tok)==D::OK);
 assert(d.response_commit(lease,2,&tok)==D::STALE&&d.at(0).readers==0);
 puts("PASS STALE_ROW_TOKEN_PINNED_RECLAIM_AND_DUPLICATE_RETIRE_FAIL_CLOSED");
 // Isolated CPU fault injection only: reach otherwise impractical generation boundary.
 auto&e=const_cast<D::entry&>(d.at(0));e.incarnation=std::numeric_limits<std::uint64_t>::max();
 tok.incarnation=e.incarnation;D::ticket max_ticket(0,e.incarnation);
 bool threw=false;try{d.reclaim(max_ticket,released,2,&tok);}catch(const std::overflow_error&){threw=true;}
 assert(threw&&d.clean_occupancy()==1&&d.at(0).status==D::CLEAN&&d.counter_writes()==1);
 puts("PASS INCARNATION_OVERFLOW_REJECTED_BEFORE_ROW_COUNT_PUBLICATION");
}
