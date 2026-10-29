#define main original_capacity_control_main
#include "/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/core/tests/ep_l2/test_tag_capacity_geometry.cc"
#undef main
int main(int argc,char**argv){
 assert(argc==14);const std::string mode=argv[13];bool direct=mode=="DIRECT",write=mode=="WRITE"||mode=="PATCH_WRITE";
 capacity_fixture f(argv,geometry(32,8));auto a=f.addresses(9);f.fill_pending(a);
 if(mode=="REUSE_GUARD"){for(unsigned n=0;n<8;++n){f.send(f.make(a[n],false));f.await_frontend();}assert(f.pending_reads.size()==8);}

 if(mode=="MSHR_FULL") {
  unsigned made=0;for(unsigned set=1;set<32 && made<128;++set){auto others=f.addresses(5,false,set);for(auto x:others){if(made==128)break;f.send(f.make(x,false));f.await_lower(9+made);++made;}}
  assert(made==128 && f.cache->mshr_entries_used()==128);
 }
 auto native=f.addresses(1,false)[0];auto incoming=f.make(native,write);unsigned uid=incoming->get_request_uid(),idx=~0u;
 assert(f.cache->ft_raw_probe_for_test(incoming,idx)==RESERVATION_FAIL);
 if(write)f.memory[native][0]=f.expected.at(uid)[0];
 if(mode=="MSHR_FULL") {
  l2_access_plan p;f.cache->preview_access(native,incoming,p);assert(p.probe_status==MISS && p.needs_new_mshr && !p.mshr_entry_available);
  f.send(incoming);f.ticks(64);assert(f.sp->ep_l2_icntl2_occupancy()==1 && f.pending_reads.size()==136);
  auto*d=ep_l2_detach_diag::get(f.cache);assert(d && d->total[ep_l2_detach_diag::detach_success]==0);
  printf("FIDELITY_REPRO|mode=MSHR_FULL|line128=1|frontend_denied=1|detach=0|normal_capacity_guard_preserved=1\n");
 } else if(mode=="PATCH_READ" || mode=="PATCH_WRITE") {
  // Repeated preview must be state-free; only real admission calls relieve.
  auto old=f.tag_for(a[0]);unsigned before_bank=f.cache->ep_l2_payload_bank_grants();
  for(unsigned n=0;n<32;++n){l2_access_plan p;f.cache->preview_access(native,incoming,p);assert(p.probe_status==MISS && f.tag_for(a[0])==old);}
  assert(f.cache->ep_l2_payload_bank_grants()==before_bank);
  f.send(incoming);f.ticks(64);assert(f.sp->ep_l2_icntl2_occupancy()==0);
  assert(f.tag_for(native).valid());auto*d=ep_l2_detach_diag::get(f.cache);assert(d && d->total[ep_l2_detach_diag::detach_success]==1);
  assert(f.pending_reads.size()==(write?8:9));
  printf("FIDELITY_REPRO|mode=%s|repeated_preview_no_mutation=1|frontend_accepted=1|detach=1|late_returns_drain_checked=1\n",mode.c_str());
 } else if(!direct){
  f.send(incoming);f.ticks(64);assert(f.pending_reads.size()==8 && f.sp->ep_l2_icntl2_occupancy()==1);
  ep_l2_detach_diag::preview s;f.cache->detach_diag_snapshot(incoming,s);l2_access_plan p;f.cache->preview_access(native,incoming,p,&s);
  assert(p.exact && p.probe_status==RESERVATION_FAIL && ((mode=="REUSE_GUARD"||mode=="T_OFF")?s.eligible==0:s.eligible>=1));
  printf("FIDELITY_REPRO|mode=%s|eligible=%u|frontend_denied=1|new_lower=0|raw_tag_fail=1|descriptor=%u|missq_room=%u\n",mode.c_str(),s.eligible,f.cache->ep_l2_descriptor_count_used(),f.cache->miss_queue_has_slots(2));
 } else {
  auto result=f.cache->tvd_frontend(incoming,f.gpu->gpu_sim_cycle,true);assert(result==l2_cache::TVD_WAIT);f.step();
  result=f.cache->tvd_frontend(incoming,f.gpu->gpu_sim_cycle,true);assert(result==l2_cache::TVD_NORMAL);
  l2_access_plan p;f.cache->preview_access(native,incoming,p);assert(p.probe_status==RESERVATION_FAIL);
  std::list<cache_event> events;auto accepted=f.cache->access(native,incoming,f.gpu->gpu_sim_cycle,events);assert(accepted!=RESERVATION_FAIL);
  f.await_lower(9);unsigned live_attached=0;for(auto x:a)if(f.tag_for(x).valid())++live_attached;
  assert(live_attached==7 && f.tag_for(native).valid());
  printf("FIDELITY_REPRO|mode=DIRECT|same_state_preview_denied=1|backend_accepted=1|new_lower=1|old_ro_still_live=1|drain_not_applicable_bypassed_subpartition_admission=1\n");fflush(stdout);std::_Exit(0);
 }
 // Return old pending packets through real ReturnQ; blocked head eventually proceeds.
 f.finish_named(mode.c_str());
}
