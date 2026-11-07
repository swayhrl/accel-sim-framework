// Actual memory_sub_partition/cache/memport/response producers. Version labels
// are symbolic complete-sector labels; dataless SASS is not full-byte evidence.
#include <cassert>
#include <cstdio>
#include <map>
#include <set>
#include "/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/core/libcuda/gpgpu_context.h"
#include "/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/core/src/gpgpu-sim/gpu-sim.h"
#include "/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/core/src/gpgpu-sim/icnt_wrapper.h"
#include "/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/core/src/gpgpu-sim/l2cache.h"
#include "/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/core/src/gpgpu-sim/mem_latency_stat.h"
#include "/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/core/src/option_parser.h"

struct scenario {
  gpgpu_context context; gpgpu_sim_config cfg;
  exec_gpgpu_sim *gpu; memory_stats_t *stats; memory_partition_unit *part;
  memory_sub_partition *sp; partition_mf_allocator *alloc;
  std::map<unsigned, unsigned long long> responses;
  std::set<unsigned> bypass_responses;
  // Observe actual lower FIFO removals without replacing the DRAM producer.
  std::map<unsigned, unsigned> issued_lower_reads;
  unsigned long long audited_cycles = 0;
  unsigned max_physical_bank_grants = 0;
  explicit scenario(const char *base, const char *overlay, bool dirty=false, bool tvd=true, bool hold=false, unsigned sets=1, unsigned ft_mode=2, unsigned ways=1, unsigned wbuf=16, bool texture_only=false)
      : cfg(&context) {
    option_parser_t p=option_parser_create(); context.ptx_reg_options(p);
    context.func_sim->ptx_opcocde_latency_options(p); icnt_reg_options(p); cfg.reg_options(p);
    option_parser_cfgfile(p,base); option_parser_cfgfile(p,overlay);
    const std::string mode=std::to_string(ft_mode);
    const std::string entries=std::to_string(wbuf);
    const char *args[]={"tvd-test", "-gpgpu_ep_l2_ft_mode",mode.c_str(), "-gpgpu_ep_l2_wbuf_entries",entries.c_str(),
      "-gpgpu_dram_partition_queues","64:128:64:1", "-gpgpu_ep_l2_tvd_clean",tvd?"1":"0",
      "-gpgpu_ep_l2_tvd_dirty",dirty?"1":"0"};
    option_parser_cmdline(p,11,args);
    if(texture_only) {
      const char *routing[]={"tvd-test","-gpgpu_cache:dl2_texture_only","1"};
      option_parser_cmdline(p,3,routing);
    }
    std::string geometry="S:"+std::to_string(sets)+":128:"+std::to_string(ways)+",L:B:m:L:L,A:128:1,256:0,32";
    const char *geo[]={"tvd-test","-gpgpu_cache:dl2",geometry.c_str()}; option_parser_cmdline(p,3,geo);
    if (hold) {
      const char *block[]={"tvd-test","-gpgpu_dram_partition_queues","2048:2:64:1",
        "-gpgpu_l2_char_dram_issue_hold_after_issues","0", "-gpgpu_l2_char_dram_issue_hold_cycles","1000000"};
      option_parser_cmdline(p,7,block);
    }
    cfg.init(); option_parser_destroy(p);
    gpu=new exec_gpgpu_sim(cfg,&context); const memory_config *mc=gpu->getMemoryConfig();
    stats=new memory_stats_t(cfg.num_shader(),gpu->getShaderCoreConfig(),mc,gpu);
    part=new memory_partition_unit(0,mc,stats,gpu); sp=part->get_sub_partition(0);
    alloc=new partition_mf_allocator(mc);
  }
  // Real host prefill hook, with actual memcpy offset accumulation. It may
  // initialize one declared sector only and must not perform a GPU bank op.
  void warm(new_addr_type address, unsigned repeats=1) {
    mem_access_sector_mask_t mask; mask.set((address>>5)&3);
    const auto physical_cycle=gpu->gpu_tot_sim_cycle+gpu->gpu_sim_cycle;
    unsigned long long before[4];
    for(unsigned b=0;b<4;++b) before[b]=sp->ft_bank_grants_for_test(b);
    for(unsigned i=0;i<repeats;++i) sp->force_l2_tag_update(address,physical_cycle,mask);
    assert(gpu->gpu_tot_sim_cycle+gpu->gpu_sim_cycle==physical_cycle);
    for(unsigned b=0;b<4;++b) assert(sp->ft_bank_grants_for_test(b)==before[b]);
  }
  bool try_warm(new_addr_type address) {
    mem_access_sector_mask_t mask;mask.set((address>>5)&3);
    const auto offset=sp->ft_memcpy_offset_for_test();
    unsigned long long before[4];
    for(unsigned b=0;b<4;++b)before[b]=sp->ft_bank_grants_for_test(b);
    const bool accepted=sp->ft_try_force_l2_tag_update(address,
        gpu->gpu_tot_sim_cycle+gpu->gpu_sim_cycle,mask);
    assert(sp->ft_memcpy_offset_for_test()==offset+(accepted?1:0));
    for(unsigned b=0;b<4;++b)assert(sp->ft_bank_grants_for_test(b)==before[b]);
    return accepted;
  }
  ~scenario() { delete alloc; delete part; delete stats; delete gpu; }
  l2_cache *cache() { return sp->ft_cache_for_test(); }
  mem_fetch *make(new_addr_type address, bool write=false, bool texture=false) {
    active_mask_t active; active.set(0); mem_access_byte_mask_t bytes;
    const unsigned sector=(address>>5)&3;
    for(unsigned i=sector*32;i<sector*32+32;++i) bytes.set(i);
    mem_access_sector_mask_t sectors; sectors.set(sector);
    assert(!texture || !write);
    if(texture) {
      // istexture() reads the instruction's space, not the access-type enum.
      warp_inst_t instruction(gpu->getShaderCoreConfig());instruction.initiation_interval=1;
      instruction.space=memory_space_t(tex_space);
      instruction.issue(active,0,gpu->gpu_sim_cycle,0,0,0);
      mem_access_t access(TEXTURE_ACC_R,address,32,false,active,bytes,sectors,&context);
      auto mf=new mem_fetch(access,&instruction,0,8,0,0,0,gpu->getMemoryConfig(),gpu->gpu_sim_cycle);
      assert(mf->istexture());return mf;
    }
    return alloc->alloc(address,write?GLOBAL_ACC_W:GLOBAL_ACC_R,active,bytes,sectors,32,write,
        gpu->gpu_sim_cycle,0,0,0,NULL,0);
  }
  unsigned push_partial_write(new_addr_type address) {
    active_mask_t active; active.set(0); mem_access_byte_mask_t bytes;
    unsigned sector=(address>>5)&3;
    for(unsigned b=sector*32;b<sector*32+4;++b) bytes.set(b);
    mem_access_sector_mask_t mask; mask.set(sector);
    auto mf=alloc->alloc(address,GLOBAL_ACC_W,active,bytes,mask,32,true,gpu->gpu_sim_cycle,0,0,0,NULL,0);
    unsigned uid=mf->get_request_uid();sp->push(mf,gpu->gpu_sim_cycle);return uid;
  }
  unsigned push_atomic(new_addr_type address) {
    active_mask_t active; active.set(0); mem_access_byte_mask_t bytes;
    unsigned sector=(address>>5)&3;
    for(unsigned b=sector*32;b<sector*32+32;++b) bytes.set(b);
    mem_access_sector_mask_t mask; mask.set(sector);
    warp_inst_t instruction(gpu->getShaderCoreConfig()); instruction.initiation_interval=1;
    instruction.space = memory_space_t(global_space);
    instruction.issue(active,0,gpu->gpu_sim_cycle,0,0,0);
    instruction.add_callback(0,NULL,NULL,NULL,true);
    mem_access_t access(GLOBAL_ACC_R,address,32,false,active,bytes,mask,&context);
    auto mf=new mem_fetch(access,&instruction,0,8,0,0,0,gpu->getMemoryConfig(),gpu->gpu_sim_cycle);
    assert(mf->isatomic()); unsigned uid=mf->get_request_uid();
    sp->push(mf,gpu->gpu_sim_cycle); return uid;
  }
  unsigned push(new_addr_type address, bool write=false) {
    auto mf=make(address,write); unsigned uid=mf->get_request_uid();
    sp->push(mf,gpu->gpu_sim_cycle); return uid;
  }
  void collect() {
    while(auto mf=sp->pop()) {
      assert(!responses.count(mf->get_request_uid()));
      assert(!bypass_responses.count(mf->get_request_uid()));
      // Zero is an explicit sector-version label. A missing read payload must
      // not silently become zero and make warmed/clean read assertions pass.
      assert((mf->get_is_write() || mf->has_ft_wb_data()) &&
             "FT/TVD read response requires explicit sector-version backing");
      unsigned sector=(mf->get_addr()>>5)&3;
      responses[mf->get_request_uid()]=mf->has_ft_wb_data()?mf->get_ft_wb_data()[sector]:0;
      delete mf;
    }
  }
  void step(bool drain=true) {
    unsigned long long before[4];
    for(unsigned b=0;b<4;++b) before[b]=sp->ft_bank_grants_for_test(b);
    part->cache_cycle(gpu->gpu_sim_cycle);
    const auto lower=sp->L2_dram_queue_empty()?nullptr:sp->L2_dram_queue_top();
    const bool pending_read=lower && !lower->get_is_write();
    const auto lower_uid=lower?lower->get_request_uid():0;
    part->simple_dram_model_cycle();
    // A real accepted DRAM issue removes this exact FIFO head. The cache
    // memport counter intentionally excludes the direct texture-only bypass.
    const auto next=sp->L2_dram_queue_empty()?nullptr:sp->L2_dram_queue_top();
    if(pending_read && next!=lower)
      ++issued_lower_reads[lower_uid];
    for(unsigned b=0;b<4;++b) {
      const auto grants=sp->ft_bank_grants_for_test(b)-before[b];
      assert(grants<=1 && "at most one grant per bank per physical GPU cycle");
      max_physical_bank_grants=std::max(max_physical_bank_grants,(unsigned)grants);
    }
    ++audited_cycles;
    ++gpu->gpu_sim_cycle; if(drain) collect();
  }
  void await(unsigned uid) {
    for(unsigned n=0;n<10000&&!responses.count(uid);++n) step();
    assert(responses.count(uid));
  }
  void drain() {
    for(unsigned n=0;n<200000 && part->busy();++n) step();
    assert(!part->busy() && !sp->ep_l2_wad_occupancy());
    assert(sp->l2_char_no_resource_leak());
  }
  void clock_report() {
    assert(audited_cycles && max_physical_bank_grants==1);
    printf("TVD_REPAIR_CLOCK|cycles=%llu|max_grants_per_physical_bank_cycle=%u\n",
        audited_cycles,max_physical_bank_grants);
  }
};


int main(int argc,char **argv) {
 assert(argc==3);scenario f(argv[1],argv[2],true);
 unsigned long long hash=0;
 for(unsigned i=0;i<140;++i){auto u=f.push(i*128ULL);f.await(u);hash=hash*131+f.responses.at(u);}
 for(unsigned i=12;i<140;i+=9){auto u=f.push(i*128ULL);f.await(u);hash=hash*131+f.responses.at(u);}
 auto w=f.push(12*128ULL,true);f.await(w);
 auto r=f.push(12*128ULL);f.await(r);assert(f.responses.at(r)==(unsigned long long)w+1);
 hash=hash*131+f.responses.at(r);
 auto atomic=f.push_atomic(3*128ULL);f.await(atomic);
 r=f.push(3*128ULL);f.await(r);hash=hash*131+f.responses.at(r);
 f.drain();
 printf("DIFFERENTIAL|cycles=%llu|queries=%llu|clean=%llu|dirty=%llu|responses=%llu|promotions=%llu|signature=%llu|banks=%u\n",
  f.gpu->gpu_sim_cycle,f.cache()->tvd_lookup_queries_for_test(),
  f.cache()->tvd_for_test()->stats().clean_installs,f.cache()->tvd_for_test()->stats().dirty_installs,
  f.cache()->tvd_for_test()->stats().read_responses,f.cache()->tvd_for_test()->stats().promotions,
  hash,f.max_physical_bank_grants);
}
