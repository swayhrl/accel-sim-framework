// New lifecycle-V2 production CPU cases. Frozen old selectors are not run.
#define main frozen_old_test_main_not_executed
#include "/root/data/ep_l2_full_workload_performance_20261027_v1/research/next_cost_aware_architecture_20261107_v1/agent_c/core_candidate/tests/ep_l2/test_tvd_production.cc"
#undef main
using D=l2_cache::tvd_directory;
static void terminal(scenario&f) {
 auto before=f.gpu->gpu_sim_cycle;
 auto reads=f.cache()->quota_row_port_for_test().stats().read_beats;
 auto commits=f.cache()->quota_row_port_for_test().stats().commit_beats;
 f.sp->quota_request_cleanup();assert(f.part->busy());
 for(unsigned i=0;i<200000&&f.part->busy();++i)f.step();
 assert(!f.part->busy()&&f.sp->quota_cleanup_done());
 assert(f.cache()->quota_cleanup_cursor_for_test()==128);
 assert(f.cache()->tvd_for_test()->occupied()==0);
 assert(f.cache()->ep_l2_payload_for_test().tvd_used()==0);
 assert(f.cache()->quota_row_port_for_test().queued()==0);
 assert(f.cache()->quota_row_port_for_test().pending()==0);
 const auto ticks=f.gpu->gpu_sim_cycle-before;
 assert(f.cache()->quota_row_port_for_test().stats().read_beats-reads==128);
 assert(f.cache()->quota_row_port_for_test().stats().commit_beats-commits==128);
 assert(ticks==384); // registered ingress1 + READ1 + COMMIT1 for every indexed row
 f.cache()->quota_print_terminal(stdout,0,f.gpu->gpu_sim_cycle);
 printf("PASS CLOCKED_EPOCH128 ticks=%llu includes_empty_rows_no_free_scan\n",(unsigned long long)ticks);
}
static void clean(const char*b,const char*o) {
 scenario f(b,o,true,true,false,1,2,1,16);
 for(unsigned i=0;i<6;++i){auto uid=f.push(i*128);f.await(uid);}
 f.drain();auto*d=f.cache()->tvd_for_test();
 assert(d->clean_occupancy()>0);
 auto uid=f.push(0);f.await(uid);f.drain();
 terminal(f);puts("PASS CLEAN_INSTALL_NET0_READ_LEASE_RETIRED_REAL_QUEUE");
}
static void dirty(const char*b,const char*o,bool real) {
 scenario f(b,o,true,true,false,1,2,1,16);
 auto step=[&](){
  f.part->cache_cycle(f.gpu->gpu_sim_cycle);
  if(real){f.part->dram_cycle();f.part->dram_cycle();f.part->dram_cycle();}
  else{f.part->simple_dram_model_cycle();f.part->simple_dram_model_cycle();f.part->simple_dram_model_cycle();}
  ++f.gpu->gpu_sim_cycle;f.collect();
 };
 auto wait=[&](unsigned uid){for(unsigned i=0;i<300000&&!f.responses.count(uid);++i)step();assert(f.responses.count(uid));};
 auto a=f.push(0,true);wait(a);
 auto z=f.push(128,true);wait(z);
 auto r=f.push(0);wait(r);
 assert(f.responses.at(r)==(unsigned long long)a+1);
 for(unsigned i=0;i<300000&&f.part->busy();++i)step();
 assert(!f.part->busy()&&f.cache()->ft_drained()&&f.sp->l2_char_no_resource_leak());
 assert(f.cache()->tvd_for_test()->stats().lower_accepts>0&&f.cache()->tvd_for_test()->stats().wb_completions>0);
 f.sp->quota_request_cleanup();unsigned n=0;
 for(;n<300000&&f.part->busy();++n)step();
 assert(!f.part->busy()&&f.sp->quota_cleanup_done()&&f.cache()->tvd_for_test()->occupied()==0);
 printf("PASS DIRTY_ATOMIC_WAD_UID_LOWER_COMPLETION_READER path=%s terminal_ticks=%u\n",real?"real_DRAM3_per_L2":"simple3_per_L2",n);
}
static void promotion(const char*b,const char*o,bool dirty_victim) {
 scenario f(b,o,true,true,false,1,2,1,16);
 auto a=f.push(0);f.await(a);
 auto z=f.push(128,dirty_victim);f.await(z);for(unsigned i=0;i<200000&&f.part->busy();++i)f.step();
 fprintf(stderr,"DIAG busy=%u drained=%u wad=%u queued=%u pending=%u clean=%u mandatory=%u\n",f.part->busy(),f.cache()->ft_drained(),f.sp->ep_l2_wad_occupancy(),f.cache()->quota_row_port_for_test().queued(),f.cache()->quota_row_port_for_test().pending(),f.cache()->tvd_for_test()->clean_occupancy(),f.cache()->tvd_for_test()->mandatory());
 for(unsigned ri=0;ri<128;++ri){auto&e=f.cache()->tvd_for_test()->at(ri);if(e.status!=D::EMPTY)fprintf(stderr,"ROW %u state%u line%llu uid%u bound%u readers%u\n",ri,e.status,(unsigned long long)e.line,e.wb_request_uid,e.wb_uid_bound,e.readers);}
 for(unsigned pr=1;pr<=14;++pr)if(f.cache()->quota_row_port_for_test().producer_active(pr))fprintf(stderr,"PRODUCER %u selected%u\n",pr,f.cache()->quota_row_port_for_test().producer_selected(pr));
 assert(!f.part->busy());

 assert(f.cache()->tvd_for_test()->live(f.cache()->tvd_for_test()->find(0)));
 auto w=f.push(0,true);f.await(w);auto r=f.push(0);f.await(r);for(unsigned i=0;i<200000&&f.part->busy();++i)f.step();
 fprintf(stderr,"DIAG busy=%u drained=%u wad=%u queued=%u pending=%u clean=%u mandatory=%u\n",f.part->busy(),f.cache()->ft_drained(),f.sp->ep_l2_wad_occupancy(),f.cache()->quota_row_port_for_test().queued(),f.cache()->quota_row_port_for_test().pending(),f.cache()->tvd_for_test()->clean_occupancy(),f.cache()->tvd_for_test()->mandatory());
 for(unsigned ri=0;ri<128;++ri){auto&e=f.cache()->tvd_for_test()->at(ri);if(e.status!=D::EMPTY)fprintf(stderr,"ROW %u state%u line%llu uid%u bound%u readers%u\n",ri,e.status,(unsigned long long)e.line,e.wb_request_uid,e.wb_uid_bound,e.readers);}
 for(unsigned pr=1;pr<=14;++pr)if(f.cache()->quota_row_port_for_test().producer_active(pr))fprintf(stderr,"PRODUCER %u selected%u\n",pr,f.cache()->quota_row_port_for_test().producer_selected(pr));
 assert(!f.part->busy());

 assert(f.responses.at(r)==(unsigned long long)w+1);
 assert(f.cache()->tvd_for_test()->stats().promotions>0);
 terminal(f);printf("PASS PAID_PROMOTION dirty_native_victim=%u data_identity_preserved\n",dirty_victim?1:0);
}
static void rollback(const char*b,const char*o,bool dirty_victim) {
 scenario f(b,o,true,true,false,1,2,1,16);
 auto a=f.push(0,dirty_victim);f.await(a);f.drain();
 auto h=f.cache()->ep_l2_tag_payload_handle_for_test(0);
 auto mf=f.make(128);auto uid=mf->get_request_uid();f.sp->push(mf,f.gpu->gpu_sim_cycle);
 const unsigned producer=dirty_victim?5:4;
 for(unsigned i=0;i<100000&&!f.cache()->quota_row_port_for_test().producer_selected(producer);++i)f.step();
 assert(f.cache()->quota_row_port_for_test().producer_selected(producer));
 assert(f.cache()->ft_reservation_active());
 assert(f.cache()->tvd_for_test()->mandatory()==0);
 auto counter=f.cache()->tvd_for_test()->clean_occupancy();
 auto reads=f.cache()->quota_row_port_for_test().stats().read_beats;
 f.cache()->quota_cancel_pending_clean_for_test();
 assert(!f.cache()->ft_reservation_active());
 assert(f.cache()->tvd_for_test()->mandatory()==0&&f.cache()->tvd_for_test()->clean_occupancy()==counter);
 assert(f.cache()->ep_l2_tag_payload_handle_for_test(0)==h&&f.cache()->ep_l2_payload_for_test().handle_live(h));
 assert(f.cache()->quota_row_port_for_test().stats().read_beats==reads);
 f.await(uid);f.drain();terminal(f);
 printf("PASS PRE_NATIVE_ROLLBACK dirty=%u no_visible_WAD_no_credit_or_payload_loss\n",dirty_victim?1:0);
}
static void reader_hold(const char*b,const char*o,bool cancel) {
 scenario f(b,o,true,true,false,1,2,1,16);
 auto a=f.push(0);f.await(a);auto z=f.push(128);f.await(z);f.drain();
 auto*d=f.cache()->tvd_for_test();auto ticket=d->find(0);auto h=d->at(ticket.index).payload;
 auto mf=f.make(0);auto uid=mf->get_request_uid();
 auto front=[&](bool space){return f.cache()->tvd_frontend(mf,f.gpu->gpu_sim_cycle,true&&space);};
 for(unsigned i=0;i<100000&&!f.cache()->quota_reader_active_for_test();++i){front(true);f.step();}
 assert(f.cache()->quota_reader_active_for_test());
 assert(d->at(ticket.index).readers==1&&f.cache()->ep_l2_payload_for_test().inspect(h).pins==1);
 auto retired=d->stats().read_responses;
 for(unsigned i=0;i<5;++i){assert(front(false)==l2_cache::TVD_WAIT);f.step();}
 assert(d->at(ticket.index).readers==1&&f.cache()->ep_l2_payload_for_test().inspect(h).pins==1&&d->stats().read_responses==retired);
 if(cancel) {
  bool done=false;
  for(unsigned i=0;i<100000&&!done;++i){done=f.cache()->tvd_cancel_frontend_read(mf,f.gpu->gpu_sim_cycle);if(!done)f.step();}
  assert(done&&!f.cache()->quota_reader_active_for_test());
  assert(d->at(ticket.index).readers==0&&f.cache()->ep_l2_payload_for_test().inspect(h).pins==0);
  delete mf;f.drain();terminal(f);puts("PASS OWNED_READER_CANCEL_PAYS_RETIRE_LIFETIME_RELEASE_ONCE");return;
 }
 bool ready=false;
 for(unsigned i=0;i<100000&&!ready;++i){ready=front(true)==l2_cache::TVD_RESPONSE;if(!ready)f.step();}
 assert(ready&&d->at(ticket.index).readers==1&&f.cache()->ep_l2_payload_for_test().inspect(h).pins==1);
 // Model the caller declining enqueue after readiness: no callback is made.
 assert(front(false)==l2_cache::TVD_WAIT);
 assert(d->at(ticket.index).readers==1&&f.cache()->ep_l2_payload_for_test().inspect(h).pins==1&&d->stats().read_responses==retired);
 f.sp->push(mf,f.gpu->gpu_sim_cycle);f.await(uid);f.drain();
 assert(d->at(ticket.index).readers==0&&f.cache()->ep_l2_payload_for_test().inspect(h).pins==0&&d->stats().read_responses==retired+1);
 terminal(f);puts("PASS ICNT_REJECTION_NEVER_RELEASES_PAYLOAD_OR_LIFETIME_BEFORE_ENQUEUE");
}
static void early_flush(const char*b,const char*o) {
 scenario f(b,o,true,true,false,1,2,1,16);
 auto a=f.push(0);f.await(a);auto z=f.push(128);f.await(z);f.drain();
 auto count=f.cache()->tvd_for_test()->clean_occupancy();
 bool rejected=false;try{f.sp->flushL2();}catch(const std::logic_error&){rejected=true;}
 assert(rejected&&f.cache()->tvd_for_test()->clean_occupancy()==count);
 terminal(f);f.sp->flushL2();puts("PASS UNTICKED_FLUSH_REJECTED_WITHOUT_ROW_LOSS");
}
static void general_pressure(const char*b,const char*o) {
 scenario f(b,o,true,true,false,64,2,16,16);
 std::array<std::vector<new_addr_type>,64>addresses;
 const auto&cfg=f.gpu->getMemoryConfig()->m_L2_config;
 unsigned complete=0;
 for(new_addr_type a=0x400000;complete<64*16;a+=128) {
  const auto set=cfg.set_index(a);assert(set<64);
  if(addresses[set].size()<16){addresses[set].push_back(a);++complete;}
 }
 for(unsigned set=0;set<64;++set)for(auto a:addresses[set])f.warm(a);
 assert(f.cache()->ep_l2_payload_for_test().resident_used()==1024);
 new_addr_type next=0x10000000,current=addresses[0][0];
 auto cold=[&](){while(cfg.set_index(next)!=0)next+=128;auto x=next;next+=128;return x;};
 for(unsigned i=0;i<38;++i) {
  current=cold();auto uid=f.push(current);f.await(uid);
  for(unsigned way=1;way<16;++way){auto hit=f.push(addresses[0][way]);f.await(hit);}
 }
 f.drain();auto clean=f.cache()->tvd_for_test()->clean_occupancy();assert(clean>0);
 auto w=f.push(current,true);f.await(w);f.drain();
 auto before=f.cache()->quota_scan_probes_for_test();
 auto uid=f.push(cold());f.await(uid);f.drain();
 auto probes=f.cache()->quota_scan_probes_for_test()-before;
 fprintf(stderr,"PRESSURE probes=%llu clean_before=%u clean_after=%u resident=%u tvd=%u\n",(unsigned long long)probes,clean,f.cache()->tvd_for_test()->clean_occupancy(),f.cache()->ep_l2_payload_for_test().resident_used(),f.cache()->ep_l2_payload_for_test().tvd_used());
 assert(f.cache()->tvd_for_test()->clean_occupancy()<clean);
 assert(f.cache()->ft_drained()&&f.sp->l2_char_no_resource_leak());
 terminal(f);
 printf("PASS GENERAL_RECLAIM_BANK0_PRESSURE paid_probes=%llu clean_before=%u cost_reference_not_performance_optimization\n",
   (unsigned long long)probes,clean);
}
int main(int argc,char**argv) {
 assert(argc==4);std::string k=argv[3];
 if(k=="clean")clean(argv[1],argv[2]);
 else if(k=="dirty")dirty(argv[1],argv[2],false);
 else if(k=="real_dirty")dirty(argv[1],argv[2],true);
 else if(k=="promote")promotion(argv[1],argv[2],false);
 else if(k=="dirty_promote")promotion(argv[1],argv[2],true);
 else if(k=="rollback")rollback(argv[1],argv[2],false);
 else if(k=="dirty_rollback")rollback(argv[1],argv[2],true);
 else if(k=="reader_hold")reader_hold(argv[1],argv[2],false);
 else if(k=="reader_cancel")reader_hold(argv[1],argv[2],true);
 else if(k=="early_flush")early_flush(argv[1],argv[2]);
 else if(k=="general_pressure")general_pressure(argv[1],argv[2]);
 else return 77;
}
