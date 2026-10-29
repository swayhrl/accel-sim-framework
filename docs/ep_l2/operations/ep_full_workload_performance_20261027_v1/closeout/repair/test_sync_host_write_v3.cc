// Must be compiled under NEWCORE/tests/ep_l2 with the full NEW eight archives.
// Never link this new API to old Source78 archives. No full Trace/kernel input.
#include <cassert>
#include <cstdio>
#include <set>
#include <vector>
#include "../../libcuda/gpgpu_context.h"
#include "../../src/gpgpu-sim/gpu-sim.h"
#include "../../src/gpgpu-sim/l2cache.h"
#include "../../src/gpgpu-sim/icnt_wrapper.h"
#include "../../src/option_parser.h"
using Code=ep_sync_host_v2::Code;
struct test_gpu:exec_gpgpu_sim{
 test_gpu(const gpgpu_sim_config&c,gpgpu_context*x):exec_gpgpu_sim(c,x){}
 memory_sub_partition*sp(unsigned n){return m_memory_sub_partition[n];}
 memory_partition_unit*part(unsigned n){return m_memory_partition_unit[n];}
};
struct World{
 gpgpu_context ctx;gpgpu_sim_config cfg;test_gpu*gpu;partition_mf_allocator*allocator;unsigned ticks=0,requests=0;
 World(char**argv):cfg(&ctx){auto p=option_parser_create();ctx.ptx_reg_options(p);ctx.func_sim->ptx_opcocde_latency_options(p);icnt_reg_options(p);cfg.reg_options(p);
  option_parser_cfgfile(p,argv[1]);option_parser_cfgfile(p,argv[2]);
  const char*enabled=std::string(argv[4])=="default_off"?"0":"1";
  const char*args[]={"sync-host-cpu","-gpgpu_n_clusters","1","-gpgpu_n_cores_per_cluster","1",
   "-gpgpu_n_mem","32","-gpgpu_n_sub_partition_per_mchannel","2","-gpgpu_ep_l2_ft_mode",argv[3],
   "-gpgpu_cache:dl2","S:32:128:8,L:B:m:L:P,A:128:1,128:0,32",
   "-gpgpu_ep_l2_sync_host_write",enabled,"-gpgpu_ep_l2_ms_observer","0",
   "-gpgpu_ep_l2_b0_stats","0","-gpgpu_ep_l2_m0a_stats","0",
   "-gpgpu_flush_l1_cache",std::string(argv[4])=="l1_unflushed"?"0":"1",
   "-gpgpu_ep_l2_tvd_clean",std::string(argv[3])=="1"?"0":"1",
   "-gpgpu_ep_l2_tvd_dirty",std::string(argv[3])=="1"?"0":"1"};
  option_parser_cmdline(p,sizeof(args)/sizeof(args[0]),args);cfg.init();option_parser_destroy(p);
  gpu=new test_gpu(cfg,&ctx);gpu->init();allocator=new partition_mf_allocator(gpu->getMemoryConfig());
  assert(gpu->getMemoryConfig()->m_n_mem_sub_partition==64);
 }
 ~World(){delete allocator;delete gpu;}
 unsigned slice(uint64_t a){addrdec_t d;gpu->getMemoryConfig()->m_address_mapping.addrdec_tlx(a,&d);assert(d.sub_partition<64);return d.sub_partition;}
 mem_fetch*make(uint64_t a,bool write){active_mask_t act;act.set(0);mem_access_byte_mask_t b;const unsigned s=(a>>5)&3;for(unsigned n=32*s;n<32*(s+1);++n)b.set(n);mem_access_sector_mask_t mask;mask.set(s);
  return allocator->alloc(a,write?GLOBAL_ACC_W:GLOBAL_ACC_R,act,b,mask,32,write,gpu->gpu_sim_cycle+gpu->gpu_tot_sim_cycle,0,0,0,nullptr,0);}
 void step(){for(unsigned p=0;p<32;++p){gpu->part(p)->cache_cycle(gpu->gpu_sim_cycle+gpu->gpu_tot_sim_cycle);gpu->part(p)->simple_dram_model_cycle();}++gpu->gpu_sim_cycle;++ticks;assert(ticks<500000);}
 void drain(){for(unsigned n=0;n<10000&&gpu->active();++n)step();assert(!gpu->active());for(unsigned s=0;s<64;++s)assert(gpu->sp(s)->l2_char_no_resource_leak());}
 uint64_t request(uint64_t a,bool write,uint64_t expected=0){auto mf=make(a,write);++requests;auto sp=gpu->sp(slice(a));const uint64_t label=uint64_t(mf->get_request_uid())+1;assert(!sp->full());sp->push(mf,gpu->gpu_sim_cycle+gpu->gpu_tot_sim_cycle);
  for(unsigned n=0;n<10000&&!sp->ep_l2_l2icnt_occupancy();++n)step();assert(sp->top()==mf);
  if(!write){assert(mf->has_ft_wb_data());assert(mf->get_ft_wb_data()[(a>>5)&3]==expected);}
  assert(sp->pop()==mf);delete mf;drain();return label;}
 void evict(uint64_t owner){const auto mc=gpu->getMemoryConfig();const auto target=slice(owner);const auto set=mc->m_L2_config.set_index(owner);std::vector<uint64_t>a;
  for(unsigned n=0;n<1048576&&a.size()<8;++n){uint64_t x=owner+0x1000000ULL+uint64_t(n)*128;if(slice(x)==target&&mc->m_L2_config.set_index(x)==set)a.push_back(x);}
  assert(a.size()==8);for(auto x:a)request(x,false,0);}
};
int main(int argc,char**argv){assert(argc==5);World w(argv);const uint64_t base=0x7ff9f3504000ULL;
 w.gpu->perf_memcpy_to_gpu(base,8192);const auto first=w.request(base,true);const auto outside=w.request(base+8000,true);(void)first;
 // No real kernel is launched: this marks a finite cache fixture's postkernel phase.
 w.gpu->sync_host_note_kernel_launch();
 if(std::string(argv[4])=="l1_unflushed"){
  assert(w.gpu->sync_host_write_step(7,base,8000)==Code::HOLD_DOMAIN);
  assert(w.gpu->sync_host_committed_bytes_for_test()==0);
  w.request(base,false,first);w.request(base+8000,false,outside);w.drain();
  puts("SYNC_HOST_V3_L1_FLUSH_DOMAIN_HOLD PASS committed=0");return 0;
 }
 if(std::string(argv[4])=="default_off"){
  assert(w.gpu->sync_host_write_step(7,base,8000)==Code::DISABLED);
  mem_access_sector_mask_t mask;mask.set(0);assert(!w.gpu->sp(w.slice(base))->ft_try_force_l2_tag_update(base,0,mask));
  puts("SYNC_HOST_V2_DEFAULT_OFF_OLD_REFUSAL PASS real_kernel_launches=0");return 0;
 }
 if(std::string(argv[4])=="pending"){
  auto mf=w.make(base+0x2000000ULL,false);auto sp=w.gpu->sp(w.slice(mf->get_addr()));sp->push(mf,w.gpu->gpu_sim_cycle);
  assert(w.gpu->sync_host_write_step(7,base,8000)==Code::WAIT_DRAIN);
  assert(w.gpu->sync_host_committed_bytes_for_test()==0);
  for(unsigned n=0;n<10000&&!sp->ep_l2_l2icnt_occupancy();++n)w.step();assert(sp->top()==mf);assert(sp->pop()==mf);delete mf;w.drain();
 }
 const auto cycle=w.gpu->gpu_sim_cycle+w.gpu->gpu_tot_sim_cycle;unsigned steps=0;Code c;
 do{c=w.gpu->sync_host_write_step(7,base,8000,32);assert(c==Code::MORE||c==Code::DONE);++steps;assert(steps<=8);
   if(steps==1){auto sp=w.gpu->sp(w.slice(base));auto before=sp->ft_memcpy_offset_for_test();
     assert(sp->sync_host_commit(base,0)==Code::ALREADY);assert(sp->ft_memcpy_offset_for_test()==before);}}while(c!=Code::DONE);
 assert(steps==8&&w.gpu->sync_host_committed_bytes_for_test()==8000);
 assert(w.gpu->gpu_sim_cycle+w.gpu->gpu_tot_sim_cycle==cycle);
 assert(w.gpu->sync_host_write_step(7,base,8000)==Code::DONE);
 bool rejected=false;try{w.gpu->perf_memcpy_to_gpu(base,32);}catch(const std::logic_error&){rejected=true;}assert(rejected);
 w.request(base,false,ep_sync_host::host_namespace|7);w.request(base+8000,false,outside);
 if(std::string(argv[3])=="1"){
  // S has no TVD retention: exercise true lower refill, then real dirtyWB/set_done.
  w.evict(base);w.request(base,false,ep_sync_host::host_namespace|7);
  const auto written=w.request(base,true);w.evict(base);
  auto cache=w.gpu->sp(w.slice(base))->ft_cache_for_test();assert(cache->sync_host_backing_for_test(base).epoch==7);
  assert(cache->sync_host_backing_for_test(base).value==written);w.request(base,false,written);
 }else{
  // Conservatively unsupportedTVDalias remains a real negative, not free reclaim.
  w.evict(base);const auto old=w.gpu->sp(w.slice(base))->ft_cache_for_test()->sync_host_backing_for_test(base);
  assert(w.gpu->sync_host_write_step(8,base,32)==Code::HOLD_ALIAS_RO);
  const auto after=w.gpu->sp(w.slice(base))->ft_cache_for_test()->sync_host_backing_for_test(base);
  assert(old.value==after.value&&old.epoch==after.epoch&&w.gpu->sync_host_committed_bytes_for_test()==0);
  puts("SYNC_HOST_V2_EXPECTED_UNSAFE_TVD_HOLD committed=0 PASS");
 }
 w.drain();std::printf("SYNC_HOST_V2_ACTUAL_CACHE_COMPONENT_PASS mode=%s slices=64 committed=8000 sectors=250 rounds=8 ticks=%u requests=%u exec_gpgpu_sim_objects=1 real_kernel_launches=0 DRAMmodel=manual_simple_not_latency_proof\n",argv[3],w.ticks,w.requests);
}
