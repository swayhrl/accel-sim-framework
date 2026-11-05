// Fixture reuse only. Old main/selectors are never called.
#define main frozen_old_test_main_not_executed
#include "test_tvd_production.cc"
#undef main
int main(int argc,char**argv){
  assert(argc==4);bool real=std::string(argv[3])=="real";
  scenario f(argv[1],argv[2],true,true,false,1,2,1,16);
  auto step=[&](){
    f.part->cache_cycle(f.gpu->gpu_sim_cycle);
    if(real){f.part->dram_cycle();f.part->dram_cycle();f.part->dram_cycle();}
    else {f.part->simple_dram_model_cycle();f.part->simple_dram_model_cycle();f.part->simple_dram_model_cycle();}
    ++f.gpu->gpu_sim_cycle;f.collect();
  };
  auto wait=[&](unsigned uid){for(unsigned n=0;n<200000&&!f.responses.count(uid);++n)step();assert(f.responses.count(uid));};
  for(unsigned i=0;i<12;++i){unsigned uid=f.push(i*128,true);wait(uid);}
  for(unsigned n=0;n<400000&&f.part->busy();++n)step();
  assert(!f.part->busy());assert(!f.sp->ep_l2_wad_occupancy());
  assert(f.sp->l2_char_no_resource_leak());assert(f.cache()->ft_drained());
  const auto&q=f.cache()->quota_row_port_for_test();
  assert(q.pending()==0);assert(q.stats().acks>=20);
  assert(q.stats().read_beats&&q.stats().commit_beats&&q.stats().holds);
  printf("PASS PRODUCTION_HANDSHAKE path=%s K=%u rows=%llu READ=%llu COMMIT=%llu holds=%llu L2ticks=%llu cycles=%llu\n",
    real?"bounded_real_DRAM_returnq":"bounded_simple_latency_queue",q.lanes(),
    (unsigned long long)q.stats().acks,(unsigned long long)q.stats().read_beats,
    (unsigned long long)q.stats().commit_beats,(unsigned long long)q.stats().holds,
    f.cache()->quota_l2_tick_for_test(),(unsigned long long)f.gpu->gpu_sim_cycle);
  puts("PASS actual_credit_tracker_packet_drained no_hidden_completion_ingress");
}
