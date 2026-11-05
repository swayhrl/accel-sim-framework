// New bounded production frontend-reclaim delta only. No old selectors run.
#define main frozen_old_production_test_main_not_executed
#include "test_tvd_production.cc"
#undef main
using D=l2_cache::tvd_directory;
static void prepare(scenario&f) {
  auto a=f.push(0);f.await(a);f.drain();
  auto b=f.push(128,true);f.await(b);f.drain();
  assert(f.cache()->tvd_for_test()->clean_occupancy()==1);
}
static void positive(const char*base,const char*overlay) {
 scenario f(base,overlay,true,true,false,1,2,1,16);prepare(f);
 auto d=f.cache()->tvd_for_test();auto t=d->find(0);assert(d->live(t));
 auto h=d->at(t.index).payload;auto mf=f.make(32);auto uid=mf->get_request_uid();
 auto lower=f.cache()->tvd_actual_lower_read_packets();
 f.sp->push(mf,f.gpu->gpu_sim_cycle);
 for(unsigned n=0;n<100&&!f.cache()->quota_row_port_for_test().pending();++n)f.step();
 assert(f.cache()->quota_row_port_for_test().pending()==1);
 assert(d->live(t)&&d->clean_occupancy()==1);
 assert(f.cache()->ep_l2_payload_for_test().handle_live(h));
 assert(f.cache()->tvd_actual_lower_read_packets()==lower);
 auto ack=f.cache()->quota_row_port_for_test().stats().acks;
 auto tick=f.cache()->quota_l2_tick_for_test();
 for(unsigned i=0;i<4;++i)f.part->simple_dram_model_cycle();
 assert(f.cache()->quota_l2_tick_for_test()==tick);
 assert(f.cache()->quota_row_port_for_test().stats().acks==ack);
 assert(d->live(t)&&d->clean_occupancy()==1);
 f.step();
 assert(f.cache()->quota_row_port_for_test().stats().acks==ack+1);
 assert(!d->live(t)&&d->clean_occupancy()==0);
 assert(!f.cache()->ep_l2_payload_for_test().handle_live(h));
 f.await(uid);f.drain();
 puts("PASS REAL_FRONTEND_CLEAN_MINUS1 READ_preserves_row_count_payload_lower COMMIT_releases_generation_once");
}
static void pin_cancel(const char*base,const char*overlay,bool corrupt_payload) {
 scenario f(base,overlay,true,true,false,1,2,1,16);prepare(f);
 auto d=const_cast<D*>(f.cache()->tvd_for_test());auto t=d->find(0);auto h=d->at(t.index).payload;
 auto mf=f.make(32);auto uid=mf->get_request_uid();
 auto front=[&](){return f.cache()->tvd_frontend(mf,f.gpu->gpu_sim_cycle,true);};
 for(unsigned n=0;n<100&&!f.cache()->quota_row_port_for_test().pending();++n){front();f.step();}
 assert(f.cache()->quota_row_port_for_test().pending()==1);
 auto before=f.cache()->quota_row_port_for_test().stats().acks;
 if(corrupt_payload) {
  // Deliberate invalid external generation change: handler must fail before
  // directory/count erase or stale-handle release; not a legal workload.
  f.cache()->ep_l2_payload_for_test().release(h);
  bool failed=false;try{front();}catch(const std::logic_error&){failed=true;}
  assert(failed&&d->live(t)&&d->clean_occupancy()==1);
  assert(f.cache()->quota_row_port_for_test().pending()==0);
  assert(f.cache()->quota_row_port_for_test().stats().acks==before);
  ep_l2::PayloadHandle unused;auto result=d->reclaim(t,unused,f.gpu->gpu_sim_cycle);assert(result==D::OK);
  delete mf;f.drain();
  puts("PASS STALE_PAYLOAD_GENERATION_FAILS_BEFORE_ROW_COUNT_MUTATION_OR_ACK");return;
 }
 auto o=d->preview_ticket(t,1,D::READ_OP);D::read_lease lease;
 auto started=d->begin_read(o,1,lease);assert(started==D::OK);
 f.cache()->ep_l2_payload_for_test().pin(h);
 assert(front()==l2_cache::TVD_WAIT);
 assert(d->live(t)&&d->clean_occupancy()==1&&f.cache()->quota_row_port_for_test().pending()==0);
 assert(f.cache()->quota_row_port_for_test().stats().acks==before);
 auto retired=d->cancel_read(lease);assert(retired==D::OK);f.cache()->ep_l2_payload_for_test().unpin(h);
 bool committed=false;
 for(unsigned n=0;n<100&&!committed;++n){f.step();committed=front()==l2_cache::TVD_NORMAL;}
 assert(committed&&!d->live(t)&&d->clean_occupancy()==0);
 assert(!f.cache()->ep_l2_payload_for_test().handle_live(h));
 f.sp->push(mf,f.gpu->gpu_sim_cycle);f.await(uid);f.drain();
 puts("PASS READER_PIN_CANCELS_OWN_READ_RESERVATION_NO_MUTATION_NO_REFUND_RETRY_COMMITS_ONCE");
}
static void directory_conflict() {
 D d(2,true,true,2);D::ticket t;
 auto ip=d.preview_install(0,false);
 auto r=d.commit_install(ip,0,ep_l2::PayloadHandle(4,7),1,0,0,false,0,t);assert(r==D::OK);
 auto p=d.preview_reserved_reclaim(t);assert(p.status==D::OK);
 auto replacement=d.preview_install(256,false);D::ticket nt;
 r=d.commit_install(replacement,256,ep_l2::PayloadHandle(8,11),1,0,0,false,1,nt);assert(r==D::OK);
 // Replacement may choose empty row. Remove/reinstall original row explicitly
 // through actual public production methods to change its incarnation.
 ep_l2::PayloadHandle gone;r=d.reclaim(t,gone,2);assert(r==D::OK);
 auto count=d.clean_occupancy();ep_l2::PayloadHandle released;
 r=d.commit_reserved_reclaim(p,released,3);
 assert(r==D::STALE&&d.clean_occupancy()==count&&!released.valid());
 puts("PASS RESERVED_RECLAIM_STALE_INCARNATION_NO_SECOND_COUNT_DECREMENT");
}
int main(int argc,char**argv) {
 assert(argc==4);
 if(std::string(argv[3])=="positive")positive(argv[1],argv[2]);
 else if(std::string(argv[3])=="pin")pin_cancel(argv[1],argv[2],false);
 else if(std::string(argv[3])=="stale_payload")pin_cancel(argv[1],argv[2],true);
 else if(std::string(argv[3])=="directory")directory_conflict();
 else return 77;
}
