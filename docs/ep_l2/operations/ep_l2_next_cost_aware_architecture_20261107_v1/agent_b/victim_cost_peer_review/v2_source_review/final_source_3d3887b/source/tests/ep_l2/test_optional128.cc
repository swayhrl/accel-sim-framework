// Actual memory_sub_partition/cache/memport/response producers. Version labels
// are symbolic complete-sector labels; dataless SASS is not full-byte evidence.
#include <cassert>
#include <cstdio>
#include <map>
#include <set>
#include "../../libcuda/gpgpu_context.h"
#include "../../src/gpgpu-sim/gpu-sim.h"
#include "../../src/gpgpu-sim/icnt_wrapper.h"
#include "../../src/gpgpu-sim/l2cache.h"
#include "../../src/gpgpu-sim/mem_latency_stat.h"
#include "../../src/option_parser.h"

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
  explicit scenario(const char *base, const char *overlay, bool dirty=false, bool tvd=true, bool hold=false, unsigned sets=1, unsigned ft_mode=2, unsigned ways=1, unsigned wbuf=16, bool texture_only=false, unsigned extension=0)
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
    const std::string ext=std::to_string(extension);
    const char *ea[]={"optional-test","-gpgpu_ep_l2_victim_extension",ext.c_str()};
    option_parser_cmdline(p,3,ea);
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


#include "../../src/gpgpu-sim/ep-l2-optional-segment-port.h"
static unsigned owners(scenario &f,new_addr_type line) {
  unsigned n=0;
  for(auto dir:{f.cache()->tvd_for_test(),f.cache()->optional_for_test()})
    if(dir)for(unsigned i=0;i<dir->capacity();++i)
      if(dir->at(i).status!=l2_cache::tvd_directory::EMPTY && dir->at(i).line==line)++n;
  for(unsigned i=0;i<f.cache()->get_num_lines_for_optional_test();++i) {
    const auto h=f.cache()->ep_l2_tag_payload_handle_for_test(i);
    if(f.cache()->ep_l2_payload_for_test().handle_live(h) &&
       f.cache()->ep_l2_payload_for_test().inspect(h).owner==line)++n;
  }
  return n;
}
static void capacity_and_alias(const char *base,const char *overlay,unsigned mode) {
  scenario f(base,overlay,true,true,false,1,2,1,16,false,mode);
  auto b=f.cache()->tvd_for_test();auto x=f.cache()->optional_for_test();
  for(unsigned i=0;i<257;++i){
    auto u=f.push(new_addr_type(i)*128);f.await(u);
    // Inject distinct symbolic clean sector labels only in this CPU fixture.
    // This tests preserving an existing clean handle, not an application oracle.
    auto h=f.cache()->ep_l2_tag_payload_handle_for_test(0);
    const_cast<ep_l2_payload_store&>(f.cache()->ep_l2_payload_for_test()).inspect_mutable(h).versions[0]=i+1000;
  }
  f.drain();assert(b->occupied()==128 && !b->mandatory());
  if(mode==2) {
    assert(x && x->occupied()==128 && !x->mandatory());
    for(unsigned i=0;i<257;++i)assert(owners(f,new_addr_type(i)*128)==1);
    for(auto d:{b,x})for(unsigned i=0;i<128;++i) {
      const auto &e=d->at(i);
      assert(f.cache()->ep_l2_payload_for_test().inspect(e.payload).versions[0]==e.line/128+1000);
    }
    const auto q0=f.cache()->tvd_lookup_queries_for_test(),q1=f.cache()->optional_queries_for_test();
    auto u=f.push(128*200);f.await(u);assert(f.responses.at(u)==1200);
    assert(f.cache()->tvd_lookup_queries_for_test()==q0+1 &&
           f.cache()->optional_queries_for_test()==q1);
    const auto extline=x->at(0).line;auto q2=f.cache()->optional_queries_for_test();
    u=f.push(extline);f.await(u);assert(f.responses.at(u)==extline/128+1000);
    assert(f.cache()->optional_queries_for_test()==q2+1);
    u=f.push(extline+32);f.await(u);assert(f.responses.at(u)==0);
    assert(owners(f,extline)==1 && !x->live(x->find(extline)));
    auto w=f.push(extline+32,true);f.await(w);
    u=f.push(extline+32);f.await(u);assert(f.responses.at(u)==(unsigned long long)w+1);
    assert(owners(f,extline)==1);
    const auto extwrite=x->at(1).line;w=f.push(extwrite,true);f.await(w);
    u=f.push(extwrite);f.await(u);assert(f.responses.at(u)==(unsigned long long)w+1);
    assert(owners(f,extwrite)==1 && !f.try_warm(999999*128ULL));
    for(unsigned i=257;i<270;++i){u=f.push(new_addr_type(i)*128);f.await(u);}
    f.drain();assert(b->occupied()+x->occupied()<=256 && b->mandatory()<=128);
    assert(f.cache()->ep_l2_payload_for_test().physical_slots()==1168);
    assert(f.cache()->ep_l2_payload_for_test().ownership_consistent());
    assert(f.cache()->optional_spills_for_test()>=128);
  } else {
    assert(!x || !x->occupied());assert(f.cache()->optional_spills_for_test()==0);
    if(mode==1)assert(f.cache()->optional_queries_for_test()>=257);
  }
  f.cache()->tvd_print(stdout,0);
  printf("PASS optional_capacity_alias_mode_%u|base=%u|extra=%u\n",mode,b->occupied(),x?x->occupied():0);
}
static void epoch_interleaving(const char *base,const char *overlay) {
  scenario f(base,overlay,true,true,false,1,2,1,16,false,2);
  auto mf=f.make(4096);auto cache=f.cache();auto now=f.gpu->gpu_sim_cycle;
  assert(cache->optional_read_row_for_test(0,now));
  assert(cache->optional_read_row_for_test(0,now));
  assert(!cache->optional_read_row_for_test(1,now));
  assert(!cache->optional_read_row_for_test(0,now)); // bounded same-row fanout

  assert(cache->tvd_frontend(mf,now,true)==l2_cache::TVD_WAIT);++f.gpu->gpu_sim_cycle;
  assert(cache->tvd_frontend(mf,++now,true)==l2_cache::TVD_WAIT);
  auto b=const_cast<l2_cache::tvd_directory*>(cache->tvd_for_test());
  auto &store=const_cast<ep_l2_payload_store&>(cache->ep_l2_payload_for_test());
  auto free=store.preview_free(ep_l2_payload_store::TVD);
  auto h=store.reserve(free.payload_id,ep_l2_payload_store::TVD,8192,ep_l2_payload_store::TVD_VALID);
  auto plan=b->preview_install(8192,false,true);l2_cache::tvd_directory::ticket t;
  assert(b->commit_install(plan,8192,h,1,0,0,false,now,t)==l2_cache::tvd_directory::OK);
  ++f.gpu->gpu_sim_cycle;
  assert(cache->tvd_frontend(mf,++now,true)==l2_cache::TVD_WAIT);
  assert(cache->optional_replays_for_test()==1 && cache->optional_queries_for_test()==0);
  ++f.gpu->gpu_sim_cycle;assert(cache->tvd_frontend(mf,++now,true)==l2_cache::TVD_WAIT);
  ++f.gpu->gpu_sim_cycle;assert(cache->tvd_frontend(mf,++now,true)==l2_cache::TVD_NORMAL);
  assert(cache->optional_queries_for_test()==1);
  ep_l2::PayloadHandle out;assert(b->reclaim(t,out,now)==l2_cache::tvd_directory::OK);
  store.release(out);delete mf;
  puts("PASS optional_interstage_base_creation_replays_paid_base_not_dual_cam");
}
static void mandatory_bank_progress(const char *base,const char *overlay) {
  scenario f(base,overlay,true,true,false,256,2,1,16,false,2);
  // 64 prefilled bank0 resident tags, then concentrate optional clean in bank0.
  for(unsigned i=0;i<256;i+=4)f.warm(new_addr_type(i)*128);
  for(unsigned i=1;i<250;++i) {auto u=f.push(new_addr_type(i)*256*128);f.await(u);}
  auto &store=f.cache()->ep_l2_payload_for_test();
  assert(!store.preview_free(ep_l2_payload_store::RESIDENT,0).valid());
  auto w=f.push(new_addr_type(249)*256*128,true);f.await(w);
  const auto before=f.cache()->optional_reclaims_for_test();
  auto u=f.push(new_addr_type(250)*256*128);f.await(u);f.drain();
  assert(f.cache()->optional_reclaims_for_test()>before);
  assert(!f.sp->ep_l2_wad_occupancy() && store.ownership_consistent());
  assert(store.physical_slots()==1168);
  puts("PASS optional_full_bank_paid_reclaim_then_mandatory_WB_complete");
}
static void ports_and_atomic_directory() {
  ep_l2_optional_segment_port p;ep_l2::PayloadHandle h(7,2);
  assert(p.reserve(1,3,4,h,p.BEGIN_READ,9));assert(!p.reserve(2,3,4,h,p.INSTALL,9));
  assert(p.reserve(1,3,4,h,p.END_READ,9));assert(!p.reserve(1,3,4,h,p.CANCEL_READ,9));
  assert(p.reserve(2,3,4,h,p.INSTALL,10));assert(!p.reserve(2,3,4,h,p.DROP,10));
  typedef ep_l2_tvd_directory<> D;D b(128,true,true),x(128,true,false);
  for(unsigned i=0;i<128;++i){auto plan=b.preview_install(i*128,false,true);D::ticket t;
    assert(b.commit_install(plan,i*128,ep_l2::PayloadHandle(i,1),1,0,0,false,0,t)==D::OK);}
  auto plan=b.preview_install(128*128,false,true);auto q=x.preview_clean_slot(0,b.at(plan.index).line,true);
  auto obs=b.preview_ticket(D::ticket(plan.index,b.at(plan.index).incarnation),1,D::READ_OP);
  D::read_lease lease;assert(b.begin_read(obs,1,lease)==D::OK);
  const auto epoch=b.creation_epoch();const auto occ=b.occupied();D::ticket t;ep_l2::PayloadHandle out;
  assert(b.commit_clean_spill(plan,x,q,128*128,ep_l2::PayloadHandle(128,1),1,1,t,out)!=D::OK);
  assert(b.creation_epoch()==epoch && b.occupied()==occ && !x.occupied());
  assert(b.cancel_read(lease)==D::OK);
  plan=b.preview_install(128*128,false,true);q=x.preview_clean_slot(0,b.at(plan.index).line,true);
  assert(b.commit_clean_spill(plan,x,q,128*128,ep_l2::PayloadHandle(128,1),1,1,t,out)==D::OK);
  assert(b.occupied()==128 && x.occupied()==1 && !out.valid());
  printf("PASS optional_bounded_port_atomic_transfer|entry_size=%zu|plan_size=%zu|port_size=%zu\n",
      sizeof(D::entry),sizeof(D::install_plan),sizeof(p));
}
int main(int argc,char **argv) {
  assert(argc==4);const unsigned mode=std::stoul(argv[3]);ports_and_atomic_directory();
  capacity_and_alias(argv[1],argv[2],mode);
  if(mode==2){epoch_interleaving(argv[1],argv[2]);mandatory_bank_progress(argv[1],argv[2]);}
  puts("PASS OPTIONAL128_PRODUCTION_CPU_BOUNDED_NO_APPLICATION");
}
