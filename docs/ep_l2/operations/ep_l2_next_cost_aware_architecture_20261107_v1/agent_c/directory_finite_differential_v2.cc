#include "ep-l2-tvd-directory.h"
#include <array>
#include <memory>
#include <random>
#include <cstdio>
#include <cstdlib>
using D=ep_l2_tvd_directory<>;using P=ep_l2_quota_row_port;
#define CHECK(x) do{if(!(x)){fprintf(stderr,"DIFF_FAIL line%u step%u\n",__LINE__,step);return 1;}}while(0)
struct R {D::state state=D::EMPTY;unsigned long long line=0;ep_l2::PayloadHandle h;unsigned readers=0,uid=0;bool bound=false;};
int main(int argc,char**argv) {
 unsigned lanes=argc>1?unsigned(std::atoi(argv[1])):1,seed=argc>2?unsigned(std::atoi(argv[2])):641;
 std::mt19937 rng(seed);D d(8,true,true,4);d.enable_timed_service(true);P port(lanes);
 std::array<R,8> ref;std::array<D::ticket,8> tickets;
 std::array<std::unique_ptr<D::read_lease>,8>leases;std::array<unsigned,8>generation{};
 unsigned tick=0,uid=100,step=0,executed=0;unsigned long long next_line=0x10000;
 auto count=[&](){unsigned n=0;for(auto&r:ref)n+=r.state==D::CLEAN;return n;};
 auto service=[&](unsigned producer,unsigned owner,unsigned row) {
  const auto&e=d.at(row);P::key k(producer,owner,row,e.incarnation,e.payload.payload_id,e.payload.generation,unsigned(e.status));
  for(unsigned tries=0;tries<20;++tries) {
   d.service_tick(tick);
   if(port.ready(k,tick))return k;
   ++tick;port.tick(tick);
  }throw std::logic_error("bounded service did not progress");
 };
 auto check=[&](){
  if(d.clean_occupancy()!=count()||count()>4)return false;
  for(unsigned i=0;i<8;++i) {
   const auto&a=d.at(i);const auto&r=ref[i];
   if(a.status!=r.state||a.readers!=r.readers)return false;
   if(r.state!=D::EMPTY&&(a.line!=r.line||a.payload!=r.h||a.wb_uid_bound!=r.bound||(r.bound&&a.wb_request_uid!=r.uid)))return false;
   for(unsigned j=0;j<i;++j)if(r.state!=D::EMPTY&&ref[j].state!=D::EMPTY&&r.h==ref[j].h)return false;
  }return true;
 };
 for(step=0;step<128;++step) {
  unsigned i=rng()%8,op=rng()%8;auto&r=ref[i];unsigned owner=++uid;D::result status=D::INVALID_INPUT;
  const bool reclaimable=(r.state==D::CLEAN||r.state==D::WB_COMPLETE)&&!r.readers;
  if((op==0||op==1)&&(r.state==D::EMPTY||reclaimable)) {
   bool wb=op==1;if(!wb&&r.state!=D::CLEAN&&count()>=4)continue;
   auto key=service(wb?5:4,owner,i);auto token=port.token(key,tick);
   auto plan=d.selected_install(next_line,wb,i,true);
   CHECK(plan.status==D::OK);
   ep_l2::PayloadHandle h(i*4,++generation[i]);D::ticket t;
   status=d.commit_install(plan,next_line,h,1,wb?1:0,0,wb,tick,t,&token,owner,wb);
   CHECK(status==D::OK);port.commit(key,tick);
   r.state=wb?D::WB_STAGED:D::CLEAN;r.line=next_line;next_line+=128;r.h=h;r.readers=0;r.uid=wb?owner:0;r.bound=wb;tickets[i]=t;
  } else if(op==2&&r.state==D::WB_STAGED) {
   auto k=service(1,r.uid,i);auto token=port.token(k,tick);
   status=d.lower_accept(tickets[i],true,tick,&token);CHECK(status==D::OK);port.commit(k,tick);r.state=D::WB_INFLIGHT;
  } else if(op==3&&r.state==D::WB_INFLIGHT) {
   auto k=service(2,r.uid,i);auto token=port.token(k,tick);
   status=d.set_done(tickets[i],tick,&token);CHECK(status==D::OK);port.commit(k,tick);r.state=D::WB_COMPLETE;
  } else if(op==4&&r.state!=D::EMPTY&&!r.readers) {
   auto k=service(8,owner,i);auto token=port.token(k,tick);
   auto observed=d.preview_ticket(tickets[i],1,D::READ_OP);CHECK(observed.status==D::READ_READY);
   leases[i].reset(new D::read_lease());status=d.begin_read(observed,1,*leases[i],&token);
   CHECK(status==D::OK);port.commit(k,tick);r.readers=1;
  } else if(op==5&&r.readers) {
   auto k=service(9,owner,i);auto token=port.token(k,tick);
   status=d.response_commit(*leases[i],tick,&token);CHECK(status==D::OK);port.commit(k,tick);leases[i].reset();r.readers=0;
  } else if((op==6||op==7)&&reclaimable) {
   auto k=service(op==6?3:6,owner,i);auto token=port.token(k,tick);ep_l2::PayloadHandle h;
   status=op==6?d.reclaim(tickets[i],h,tick,&token):d.promote(tickets[i],h,tick,&token);
   CHECK(status==D::OK&&h==r.h);port.commit(k,tick);r=R();
  } else continue;
  ++executed;CHECK(check());++tick;port.tick(tick);d.service_tick(tick);
 }
 // Bounded closure of exactly the generated rows, with paid mutation service.
 for(unsigned i=0;i<8;++i) {
  auto&r=ref[i];
  if(r.readers){auto k=service(14,++uid,i);auto tok=port.token(k,tick);CHECK(d.cancel_read(*leases[i],&tok)==D::OK);port.commit(k,tick);leases[i].reset();r.readers=0;++tick;}
  if(r.state==D::WB_STAGED){auto k=service(1,r.uid,i);auto tok=port.token(k,tick);CHECK(d.lower_accept(tickets[i],true,tick,&tok)==D::OK);port.commit(k,tick);r.state=D::WB_INFLIGHT;++tick;}
  if(r.state==D::WB_INFLIGHT){auto k=service(2,r.uid,i);auto tok=port.token(k,tick);CHECK(d.set_done(tickets[i],tick,&tok)==D::OK);port.commit(k,tick);r.state=D::WB_COMPLETE;++tick;}
  if(r.state!=D::EMPTY){auto k=service(11,++uid,i);auto tok=port.token(k,tick);ep_l2::PayloadHandle h;CHECK(d.reclaim(tickets[i],h,tick,&tok)==D::OK);port.commit(k,tick);r=R();++tick;}
  CHECK(check());
 }
 CHECK(d.occupied()==0&&d.clean_occupancy()==0&&port.queued()==0);
 printf("PASS PRODUCTION_DIRECTORY_FINITE_DIFF lanes=%u seed=%u attempted=128 executed=%u ticks=%u counter_writes=%llu\n",lanes,seed,executed,tick,(unsigned long long)d.counter_writes());
}
