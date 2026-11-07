#include "ep-l2-tvd-directory.h"
#include <cstdio>
#include <cstdlib>
using P=ep_l2_quota_row_port;using D=ep_l2_tvd_directory<>;
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL line%u\n",__LINE__);return 1;}}while(0)
static int cap_test(unsigned cap) {
 P p(2);D d(2,true,true,cap);d.enable_timed_service(true);
 P::key a(4,1,0,0),b(11,2,1,0);p.ready(a,0);p.ready(b,0);
 p.tick(1);d.service_tick(1);CHECK(!p.ready(a,1)&&!p.ready(b,1));
 p.tick(2);d.service_tick(2);CHECK(p.ready(a,2)&&p.ready(b,2));
 auto pa=d.selected_install(0,false,0),pb=d.selected_install(128,false,1);
 auto ta=p.token(a,2),tb=p.token(b,2);D::ticket ra,rb;
 CHECK(d.commit_install(pa,0,ep_l2::PayloadHandle(4,1),1,0,0,false,2,ra,&ta)==D::OK);
 p.commit(a,2);CHECK(d.clean_occupancy()==1&&d.counter_writes()==1);
 CHECK(d.commit_install(pb,128,ep_l2::PayloadHandle(8,1),1,0,0,false,2,rb,&tb)==D::STALE);
 pb=d.selected_install(128,false,1);
 if(cap==2) {
  CHECK(pb.status==D::OK);
  CHECK(d.commit_install(pb,128,ep_l2::PayloadHandle(8,1),1,0,0,false,2,rb,&tb)==D::COUNTER_BUSY);
  CHECK(d.clean_occupancy()==1&&p.pending()==1&&p.stats().read_beats==1);
  p.tick(3);d.service_tick(3);tb=p.token(b,3);pb=d.selected_install(128,false,1);
  CHECK(d.commit_install(pb,128,ep_l2::PayloadHandle(8,1),1,0,0,false,3,rb,&tb)==D::OK);
  p.commit(b,3);CHECK(d.clean_occupancy()==2&&d.counter_writes()==2&&p.stats().read_beats==1);
 } else {
  CHECK(pb.status==D::DIRECTORY_FULL);CHECK(d.clean_occupancy()==1&&d.counter_writes()==1);
  CHECK(p.cancel_owner(11,2)==1);CHECK(p.pending()==0&&p.stats().read_beats==1);
 }
 printf("PASS K2_TWO_PLUS1_OLD_COUNT cap=%u count=%u writes=%llu no_lost_update_no_cap_overrun\n",
 cap,d.clean_occupancy(),(unsigned long long)d.counter_writes());return 0;
}
int main() {
 if(cap_test(1)||cap_test(2))return 1;
 P p(1);P::key keys[6]={P::key(2,1,0,1),P::key(1,2,1,1),P::key(4,3,2,1),
  P::key(8,4,3,1),P::key(9,5,4,1),P::key(11,6,5,1)};
 for(auto&k:keys)p.ready(k,0);CHECK(p.queued()==6&&p.pending()==0);
 unsigned done=0;unsigned mask=0;
 for(unsigned tick=1;tick<20&&done<6;++tick) {
  p.tick(tick);
  for(unsigned i=0;i<6;++i)if(!(mask&(1u<<i))&&p.ready(keys[i],tick)) {
   p.commit(keys[i],tick);mask|=1u<<i;++done;
  }
 }
 CHECK(done==6&&p.queued()==0);CHECK(p.stats().read_beats==6&&p.stats().commit_beats==6);
 puts("PASS SIX_BOUNDED_HEADS_RR_ATTEMPT_SERVICE_READ_COMMIT");
 P q(2);P::key a(4,10,0,1),b(11,11,1,1),c(8,12,2,1);
 q.ready(a,0);q.ready(b,0);q.tick(1);CHECK(q.pending()==2);CHECK(q.cancel_owner(4,10)==1);
 q.ready(c,1);CHECK(q.pending()==1&&q.stats().read_beats==1);q.tick(2);CHECK(q.ready(b,2));
 q.commit(b,2);CHECK(q.stats().read_beats==1);q.tick(3);CHECK(q.pending()==1&&q.stats().read_beats==2);
 CHECK(!q.ready(c,3));q.tick(4);CHECK(q.ready(c,4));q.commit(c,4);
 puts("PASS CANCEL_AND_BUSY_NEVER_REFUND_READ");
 D d(2,true,true,2);d.enable_timed_service(true);d.service_tick(1);
 auto plan=d.selected_install(0,false,0);D::ticket t;
 CHECK(d.commit_install(plan,0,ep_l2::PayloadHandle(4,1),1,0,0,false,1,t)==D::ROW_PORT_BUSY);
 CHECK(d.clean_occupancy()==0);puts("PASS UNPAID_ROW_MUTATION_FAILS_CLOSED");
}
