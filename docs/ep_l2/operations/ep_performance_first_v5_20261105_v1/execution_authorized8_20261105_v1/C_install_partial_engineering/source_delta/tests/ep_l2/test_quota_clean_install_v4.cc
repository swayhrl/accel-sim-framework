// Only new paid CLEAN-install/replacement delta cases; old selectors not run.
#define main frozen_old_production_test_main_not_executed
#include "test_tvd_production.cc"
#undef main
using D=l2_cache::tvd_directory;
static void prepare(scenario&f,bool net0) {
 auto a=f.push(0);f.await(a);f.drain();
 if(net0){auto b=f.push(128);f.await(b);f.drain();assert(f.cache()->tvd_for_test()->clean_occupancy()==1);}
}
static void run(const char*base,const char*overlay,const std::string&kind) {
 const bool net0=kind!="plus1";
 scenario f(base,overlay,true,true,false,1,2,1,16);prepare(f,net0);
 auto*d=const_cast<D*>(f.cache()->tvd_for_test());
 auto old_row=d->find(0);auto old_count=d->clean_occupancy();
 ep_l2::PayloadHandle displaced=net0?d->at(old_row.index).payload:ep_l2::PayloadHandle();
 auto incoming=f.cache()->ep_l2_tag_payload_handle_for_test(0);
 auto lower=f.cache()->tvd_actual_lower_read_packets();
 auto mf=f.make(net0?256:128);auto uid=mf->get_request_uid();f.sp->push(mf,f.gpu->gpu_sim_cycle);
 for(unsigned n=0;n<100&&!f.cache()->quota_row_port_for_test().pending();++n)f.step();
 assert(f.cache()->quota_row_port_for_test().pending()==1&&f.cache()->ft_reservation_active());
 assert(d->clean_occupancy()==old_count);
 assert(f.cache()->ep_l2_tag_payload_handle_for_test(0)==incoming);
 assert(f.cache()->ep_l2_payload_for_test().handle_live(incoming));
 assert(f.cache()->tvd_actual_lower_read_packets()==lower);
 if(net0)assert(d->live(old_row)&&d->at(old_row.index).payload==displaced&&f.cache()->ep_l2_payload_for_test().handle_live(displaced));
 auto ack=f.cache()->quota_row_port_for_test().stats().acks;
 if(kind=="rollback") {
  f.cache()->quota_cancel_pending_clean_for_test();
  assert(!f.cache()->ft_reservation_active()&&f.cache()->quota_row_port_for_test().pending()==0);
  assert(d->clean_occupancy()==old_count&&d->live(old_row));
  assert(f.cache()->ep_l2_tag_payload_handle_for_test(0)==incoming&&f.cache()->ep_l2_payload_for_test().handle_live(incoming));
  assert(f.cache()->ep_l2_payload_for_test().handle_live(displaced));
  assert(f.cache()->tvd_actual_lower_read_packets()==lower);
  assert(f.cache()->quota_row_port_for_test().stats().acks==ack);
 } else if(kind=="pin") {
  auto o=d->preview_ticket(old_row,1,D::READ_OP);D::read_lease lease;
  auto v=d->begin_read(o,1,lease);assert(v==D::OK);f.cache()->ep_l2_payload_for_test().pin(displaced);
  f.step();
  assert(d->live(old_row)&&d->clean_occupancy()==old_count&&f.cache()->ft_reservation_active());
  assert(f.cache()->quota_row_port_for_test().stats().acks==ack);
  assert(f.cache()->quota_row_port_for_test().pending()==0);
  assert(f.cache()->ep_l2_tag_payload_handle_for_test(0)==incoming);
  assert(f.cache()->ep_l2_payload_for_test().handle_live(displaced));
  assert(f.cache()->tvd_actual_lower_read_packets()==lower);
  auto retired=d->cancel_read(lease);assert(retired==D::OK);f.cache()->ep_l2_payload_for_test().unpin(displaced);
 } else {
  f.step();
  assert(f.cache()->quota_row_port_for_test().stats().acks==ack+1);
  assert(d->clean_occupancy()==1);
  auto installed=d->find(net0?128:0);assert(d->live(installed)&&d->at(installed.index).payload==incoming);
  assert(f.cache()->ep_l2_payload_for_test().inspect(incoming).allocation_role==ep_l2_payload_store::TVD);
  if(net0){assert(!d->live(old_row));assert(!f.cache()->ep_l2_payload_for_test().handle_live(displaced));}
 }
 f.await(uid);f.drain();
 assert(d->clean_occupancy()==1);
 if(kind=="rollback"||kind=="pin"){
  assert(!d->live(old_row));assert(!f.cache()->ep_l2_payload_for_test().handle_live(displaced));
  auto installed=d->find(128);assert(d->live(installed)&&d->at(installed.index).payload==incoming);
 }
 printf("PASS REAL_CLEAN_INSTALL kind=%s old_count=%u final_count=%u READ_preserves_old_row_payload_native_tag COMMIT_once\n",kind.c_str(),old_count,d->clean_occupancy());
}
static void directory(const std::string&kind) {
 D d(2,true,true,1);D::ticket a;auto p=d.preview_install(0,false);
 auto q=d.commit_install(p,0,ep_l2::PayloadHandle(4,1),1,0,0,false,0,a);assert(q==D::OK&&d.clean_occupancy()==1);
 auto replace=d.preview_install(128,false);assert(replace.status==D::OK&&replace.index==a.index);
 if(kind=="overflow") {
  auto&e=const_cast<D::entry&>(d.at(a.index));e.incarnation=std::numeric_limits<unsigned long long>::max();
  bool failed=false;try{d.validate_install(replace,128,ep_l2::PayloadHandle(8,1),1,0,0,false);}catch(const std::overflow_error&){failed=true;}
  assert(failed&&d.clean_occupancy()==1&&d.at(a.index).line==0);
  puts("PASS INSTALL_INCARNATION_EXHAUSTION_FAILS_BEFORE_COUNT_ROW_PUBLICATION");return;
 }
 auto obs=d.preview_ticket(a,1,D::READ_OP);D::read_lease lease;
 q=d.begin_read(obs,1,lease);assert(q==D::OK);
 assert(d.validate_install(replace,128,ep_l2::PayloadHandle(8,1),1,0,0,false)==D::STALE);
 assert(d.clean_occupancy()==1&&d.live(a));q=d.cancel_read(lease);assert(q==D::OK);
 replace=d.preview_install(128,false);D::ticket b;
 q=d.commit_install(replace,128,ep_l2::PayloadHandle(8,1),1,0,0,false,1,b);
 assert(q==D::OK&&d.clean_occupancy()==1&&!d.live(a)&&d.live(b));
 puts("PASS FULL_CAP_CLEAN_REPLACEMENT_NET0_SINGLE_TARGET_STALE_REJECT_NO_MUTATION");
}
int main(int argc,char**argv) {
 assert(argc==4);std::string k=argv[3];
 if(k=="directory"||k=="overflow")directory(k);
 else if(k=="plus1"||k=="net0"||k=="pin"||k=="rollback")run(argv[1],argv[2],k);
 else return 77;
}
