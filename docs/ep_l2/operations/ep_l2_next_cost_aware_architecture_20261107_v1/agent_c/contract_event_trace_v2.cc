#include "ep-l2-tvd-directory.h"
#include <cstdio>
#include <stdexcept>
using P=ep_l2_quota_row_port;using D=ep_l2_tvd_directory<>;
static void emit(const char*n,unsigned tick,P&p,D&d){
 printf("%s,%u,%u,%u,%llu,%llu,%llu,%u,%llu\n",n,tick,p.queued(),p.pending(),
 (unsigned long long)p.stats().read_beats,(unsigned long long)p.stats().commit_beats,
 (unsigned long long)p.stats().cancellations,d.clean_occupancy(),(unsigned long long)d.counter_writes());
}
int main(){
 puts("event,tick,queued,pending,reads,commits,cancels,count,count_writes");
 P p(1);D d(128,true,true,2);d.enable_timed_service(true);
 auto clk=[&](unsigned t){p.tick(t);d.service_tick(t);};
 auto install=[&](P::key k,unsigned t,unsigned long long line){auto a=d.selected_install(line,false,k.row);
  auto token=p.token(k,t);D::ticket out;
  if(d.commit_install(a,line,ep_l2::PayloadHandle(k.row*4+4,k.uid),1,0,0,false,t,out,&token)!=D::OK)throw std::logic_error("install failed");
  p.commit(k,t);};
 P::key a(4,1,0,0);p.ready(a,0);emit("enqueue_plus1",0,p,d);
 clk(1);emit("read_plus1",1,p,d);clk(2);install(a,2,0);emit("commit_plus1",2,p,d);
 auto row=d.at(0);P::key b(4,2,0,row.incarnation);p.ready(b,3);emit("enqueue_net0",3,p,d);
 clk(4);emit("read_net0",4,p,d);clk(5);install(b,5,128);emit("commit_net0",5,p,d);
 P::key c(4,3,1,0);p.ready(c,6);clk(7);emit("read_cancel",7,p,d);
 p.cancel_owner(4,3);emit("cancel",7,p,d);P::key e(4,4,1,0);p.ready(e,7);emit("enqueue_after_cancel",7,p,d);
 clk(8);emit("new_read_no_refund",8,p,d);clk(9);install(e,9,256);emit("commit_plus1_after_cancel",9,p,d);
 // Terminal visits every row, including empty, on the same production fabric.
 unsigned t=10;
 for(unsigned i=0;i<128;++i){
  auto r=d.at(i);P::key k(11,100+i,i,r.incarnation);
  p.ready(k,t);clk(t+1);clk(t+2);auto token=p.token(k,t+2);
  ep_l2::PayloadHandle released;
  if(r.status!=D::EMPTY&&d.reclaim(D::ticket(i,r.incarnation),released,t+2,&token)!=D::OK)throw std::logic_error("cleanup failed");
  p.commit(k,t+2);t+=3;
 }
 emit("cleanup128",t-1,p,d);
 P k2(2);D e2(2,true,true,2);e2.enable_timed_service(true);
 P::key ka(4,900,0,0),kb(11,901,1,0);
 k2.ready(ka,0);k2.ready(kb,0);k2.tick(1);e2.service_tick(1);emit("k2_shared_old_read",1,k2,e2);
 k2.tick(2);e2.service_tick(2);
 auto pa=e2.selected_install(0,false,0),pb=e2.selected_install(128,false,1);
 auto ta=k2.token(ka,2),tb=k2.token(kb,2);D::ticket ra,rb;
 if(e2.commit_install(pa,0,ep_l2::PayloadHandle(4,1),1,0,0,false,2,ra,&ta)!=D::OK)throw std::logic_error("k2a");
 k2.commit(ka,2);emit("k2_first_count_write",2,k2,e2);
 if(e2.commit_install(pb,128,ep_l2::PayloadHandle(8,1),1,0,0,false,2,rb,&tb)!=D::STALE)throw std::logic_error("stale missed");
 pb=e2.selected_install(128,false,1);
 if(e2.commit_install(pb,128,ep_l2::PayloadHandle(8,1),1,0,0,false,2,rb,&tb)!=D::COUNTER_BUSY)throw std::logic_error("single lane missed");
 emit("k2_counter_busy_no_refund",2,k2,e2);
 k2.tick(3);e2.service_tick(3);tb=k2.token(kb,3);pb=e2.selected_install(128,false,1);
 if(e2.commit_install(pb,128,ep_l2::PayloadHandle(8,1),1,0,0,false,3,rb,&tb)!=D::OK)throw std::logic_error("k2b");
 k2.commit(kb,3);emit("k2_second_serial_count_write",3,k2,e2);
 fprintf(stderr,"HOST_BYTES key=%zu port=%zu directory=%zu\\n",sizeof(P::key),sizeof(P),sizeof(D));
}
