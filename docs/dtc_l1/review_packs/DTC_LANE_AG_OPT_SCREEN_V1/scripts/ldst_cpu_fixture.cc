// AG bounded CPU LDST fixture adapted from the fixed AA5 fixture, not an AA5 attempt.
// Main logical line changed to 0x2000 so AE ON exercises set0 -> set4.
// CPU-only synthetic coalesced instructions; actual ABI production objects.
// -fno-access-control is a test seam; no production source/header is changed.
#include "gpgpu-sim/gpu-sim.h"
#include "gpgpu-sim/shader.h"
#include "gpgpu_context.h"
#include "option_parser.h"
#include "gpgpu-sim/icnt_wrapper.h"
#include "gpgpu-sim/scoreboard.h"
#include <sys/resource.h>
#include <dlfcn.h>
#include <iostream>
#include <vector>
#include "abi_stats_dump.inc"

// Normal production entry only; no private observer printer is invoked.
static void normal_snapshot(gpgpu_sim*gpu,const char*label){
 dtc_l1::paper_frontend_stats before,after;
 for(unsigned c=0;c<64;++c)gpu->get_simt_core_clusters()[c]->get_dtc_l1_stats(before);
 std::cout<<"AA5_PUBLIC_BEFORE label="<<label<<"\n";dump_all_stats(before);
 const auto cycle=gpu->global_cycle();
 std::cout<<"AA5_EXPORT_SNAPSHOT_BEGIN label="<<label<<" expected_cycle="<<cycle<<"\n";std::cout.flush();
 Dl_info normal_binding{};auto*normal_symbol=dlsym(RTLD_DEFAULT,"_ZN9gpgpu_sim14gpu_print_statEy");assert(normal_symbol && dladdr(normal_symbol,&normal_binding));std::cout<<"AA5_NORMAL_ENTRY_LIBRARY "<<normal_binding.dli_fname<<"\n";std::cout.flush();
 gpu->gpu_print_stat(0); // genuine production gpu_print_stat -> normal aggregate path
 std::fflush(stdout);
 std::cout<<"AA5_EXPORT_SNAPSHOT_END label="<<label<<"\n";
 for(unsigned c=0;c<64;++c)gpu->get_simt_core_clusters()[c]->get_dtc_l1_stats(after);
 assert(gpu->global_cycle()==cycle);
 std::cout<<"AA5_PUBLIC_AFTER label="<<label<<"\n";dump_all_stats(after);
}

struct capture_transport:mem_fetch_interface {
  gpgpu_sim* gpu; std::vector<mem_fetch*> requests; unsigned bytes=0;
  explicit capture_transport(gpgpu_sim*g):gpu(g){}
  bool full(unsigned,bool)const override{return false;}
  void push(mem_fetch*m)override{requests.push_back(m);bytes+=m->get_data_size();std::cout<<"Y2_PACKET "<<gpu->global_cycle()<<" "<<m->get_addr()<<" "<<m->get_data_size()<<"\n";}
};
static warp_inst_t* instruction(shader_core_ctx*core,unsigned wid,unsigned reg,uint64_t addr){
 auto*p=new warp_inst_t(core->get_config());p->op=LOAD_OP;p->memory_op=memory_load;p->space=memory_space_t(global_space);p->cache_op=CACHE_L1;p->data_size=4;p->pc=0x100+wid*16;p->op_pipe=MEM__OP;p->num_regs=1;p->outcount=1;p->incount=0;p->isize=16;p->pred=-1;p->ar1=-1;p->ar2=-1;
 for(auto&v:p->out)v=0;for(auto&v:p->in)v=0;p->out[0]=reg;p->arch_reg.dst[0]=reg;
 active_mask_t mask;mask.set(0);p->issue(mask,wid,core->get_gpu()->global_cycle(),wid,0,0);
 mem_access_byte_mask_t bytes;for(unsigned i=0;i<32;i++)bytes.set(i);mem_access_sector_mask_t sectors;sectors.set(0);
 p->m_accessq.emplace_back(GLOBAL_ACC_R,addr,32,false,mask,bytes,sectors,core->get_config()->gpgpu_ctx);return p;
}
int main(int argc,const char**argv){
 rlimit limit{0,0};setrlimit(RLIMIT_CORE,&limit);if(argc<2)return 64;
 Dl_info binding{};auto*symbol=dlsym(RTLD_DEFAULT,"_ZN9ldst_unit5cycleEv");if(!symbol||!dladdr(symbol,&binding))return 65;std::cout<<"Y2_LIBRARY "<<binding.dli_fname<<"\n";
 gpgpu_context ctx;gpgpu_sim_config cfg(&ctx);auto parser=option_parser_create();cfg.reg_options(parser);icnt_reg_options(parser);ctx.ptx_reg_options(parser);ctx.func_sim->ptx_opcocde_latency_options(parser);option_parser_cfgfile(parser,argv[1]);
 const char*defaults[]={"Y2_ABI","-gpgpu_n_clusters","64","-gpgpu_n_cores_per_cluster","1","-gpgpu_n_mem","1","-gpgpu_n_sub_partition_per_mchannel","1","-gpgpu_shader_core_pipeline","64:32","-gpgpu_shader_cta","2","-gpgpu_smem_latency","2","-network_mode","2","-gpgpu_cache:dl1","N:8:128:1,L:T:m:L:L,A:4:4,4:0,32","-gpgpu_dtc_l1_mode","3","-gpgpu_dtc_l1_finite_service","1","-gpgpu_l1_cache_write_ratio","0","-gpgpu_gmem_skip_L1D","0","-enable_ptx_file_line_stats","0","-gpgpu_flush_l1_cache","1","-gpgpu_cache:dl1PrefL1","N:8:128:1,L:T:m:L:L,A:4:4,4:0,32","-gpgpu_shmem_size_PrefL1","65536","-gpgpu_dtc_l1_debug_event_limit","0","-gpgpu_runtime_stat","500000"};
 option_parser_cmdline(parser,sizeof(defaults)/sizeof(defaults[0]),defaults);option_parser_cmdline(parser,argc-1,argv+1);option_parser_print(parser,stdout);cfg.init();auto*gpu=new exec_gpgpu_sim(cfg,&ctx);gpu->init();normal_snapshot(gpu,"initial0");
 auto*core=gpu->get_simt_core_clusters()[0]->get_shader_cores()[0];auto*ld=core->m_ldst_unit;capture_transport transport(gpu);ld->m_icnt=&transport;capture_transport ordinary_transport(gpu);ld->m_L1D->m_memport=&ordinary_transport;mem_fetch*ordinary_root=nullptr;
 auto*collector=dynamic_cast<opndcoll_rfu_t*>(core->m_operand_collector);if(!collector)return 66;
 std::vector<std::vector<mem_fetch*>> batches;std::vector<unsigned> returned;unsigned built=0,issued=0;
 bool multi=true;unsigned expected_loads=multi?3:1;
 for(unsigned cycle=1;cycle<=40;++cycle){
  gpu->gpu_sim_cycle=cycle;collector->process_banks();
  if(cycle==1||(multi&&(cycle==5||cycle==11))){unsigned wid=cycle==5?1:0;unsigned reg=cycle==11?2:1;auto*p=instruction(core,wid,reg,0x2000);assert(ld->m_dispatch_reg->empty());core->m_warp[wid]->inc_inst_in_pipeline();core->m_scoreboard->reserveRegisters(p);register_set regs(1,"Y2");regs.move_in(p);ld->issue(regs);++issued;}
  if(cycle==8){auto*p=instruction(core,0,3,0x3000);ordinary_root=ld->m_mf_allocator->alloc(*p,p->m_accessq.back(),cycle);delete p;std::list<cache_event> events;assert(ld->m_L1D->access(0x3000,ordinary_root,cycle,events)==MISS);}
  if(cycle==23){assert(ordinary_transport.requests.size()==1);ordinary_root->set_reply();ld->m_L1D->fill(ordinary_root,cycle);assert(ld->m_L1D->access_ready());assert(ld->m_L1D->next_access()==ordinary_root);delete ordinary_root;ordinary_root=nullptr;}
  if(cycle==9){core->m_warp[0]->set_membar();assert(core->warp_waiting_at_mem_barrier(0));assert(!ld->m_dtc_l1_oo_frontend->will_new_miss(0x2000));
#ifdef Y2_HAS_K1
assert(ld->m_dtc_invalidation.requests==0);
#endif
std::cout<<"Y2_CONTROL {\"cycle\":9,\"queryable\":true,\"selected_event\":false}\n";}
  if(cycle==10){
#ifdef Y2_HAS_K1
   auto before=ld->m_dtc_service_sample_cycle;core->cache_invalidate(dtc_l1::invalidation_source::IDLE_CLUSTER);core->cache_invalidate(dtc_l1::invalidation_source::IDLE_CLUSTER);assert(before==ld->m_dtc_service_sample_cycle);if(cfg.m_shader_config.dtc_l1_invalidate_on_source_event){assert(ld->m_dtc_l1_oo_frontend->will_new_miss(0x2000));assert(ld->m_dtc_invalidation.changed==1&&ld->m_dtc_invalidation.ordinary_commits==0&&ld->m_L1D->m_invalidate_pending);}
#else
   core->cache_invalidate();core->cache_invalidate();
#endif
  }
  while(built<transport.requests.size()){
   auto*root=transport.requests[built++];std::vector<mem_fetch*> children;for(unsigned sector:{3U,1U,0U,2U}){if(std::getenv("Y2_DUPLICATE")&&sector==1)sector=3;active_mask_t mask;mask.set(0);mem_access_byte_mask_t bm;mem_access_sector_mask_t sm;sm.set(sector);mem_access_t access(GLOBAL_ACC_R,root->get_addr()+sector*32,32,false,mask,bm,sm,&ctx);auto*child=new mem_fetch(access,static_cast<const warp_inst_t*>(nullptr),0,8,0,0,0,&cfg.m_memory_config,cycle,root);child->set_reply();children.push_back(child);}batches.push_back(children);returned.push_back(0);
  }
  for(unsigned i=0;i<batches.size();++i)if(cycle>=12+i*12&&returned[i]<4)ld->fill(batches[i][returned[i]++]);
  if(cycle==36){assert(!core->warp_waiting_at_mem_barrier(0));assert(!core->warp_waiting_at_mem_barrier(0));}
  if(cycle==32){cfg.gpgpu_flush_l1_cache=false;gpu->change_cache_config(FuncCachePreferNone);gpu->change_cache_config(FuncCachePreferL1);gpu->change_cache_config(FuncCachePreferL1);
#ifdef Y2_HAS_K1
   if(cfg.m_shader_config.dtc_l1_invalidate_on_source_event){assert(ld->m_dtc_invalidation.source_counts[3]==1);auto*other=gpu->get_simt_core_clusters()[1]->get_shader_cores()[0]->m_ldst_unit;assert(other->m_dtc_invalidation.source_counts[3]==1);}
#endif
   cfg.gpgpu_flush_l1_cache=true;
  }
  // Genuine operand-collector bank conflict, not a mocked writeback predicate.
  if(cycle>=15&&cycle<=20){auto*block=instruction(core,0,1,0x2000);assert(collector->writeback(*block));delete block;}
  if(cycle<=30||cycle>=35)ld->cycle();
  ld->m_dtc_l1_oo_frontend->assert_shadow_refs();
  unsigned lower_live=ld->m_dtc_l1_oo_inflight.size()+(ordinary_root?1:0);assert(gpu->dtc_l1_lower_requests_acquired()-gpu->dtc_l1_lower_requests_released()==lower_live);
  std::cout<<"Y2_PHYSICAL [";bool comma=false;unsigned physical_id=0;for(const auto&physical:ld->m_dtc_l1_oo_frontend->m_phys){if(physical.allocated){if(comma)std::cout<<",";std::cout<<"["<<physical_id<<","<<physical.generation<<","<<physical.ref_count<<","<<physical.tag_valid<<","<<physical.ready<<","<<physical.waiters.size()<<"]";comma=true;}++physical_id;}std::cout<<"]\n";
  std::cout<<"Y2_TICK ["<<cycle<<","<<ld->m_dtc_l1_oo_pib.size()<<","<<ld->m_dtc_l1_oo_frontend->allocated_lines()<<","<<ld->m_dtc_l1_oo_frontend->active_refs()<<","<<ld->m_dtc_l1_oo_inflight.size()<<","<<gpu->dtc_l1_lower_requests_acquired()<<","<<gpu->dtc_l1_lower_requests_released()<<","<<ld->m_dtc_service_samples<<","<<ld->m_dtc_service_pib_integral<<","<<ld->m_dtc_service_physical_integral<<","<<ld->m_dtc_l1_oo_ready_but_wb_blocked_cycles<<","<<gpu->gpu_sim_insn<<"]\n";
 }
 assert(issued==expected_loads);for(auto n:returned)assert(n==4);dtc_l1::paper_frontend_stats stats;ld->get_dtc_l1_stats(stats);
 assert(stats.oo_retire_count==expected_loads&&stats.oo_completion_dependencies==expected_loads&&stats.oo_completion_dependencies_closed==expected_loads);assert(stats.oo_ready_but_writeback_blocked_cycles>0);assert(stats.oo_active_refs==0&&stats.oo_inflight_current==0);assert(!core->m_scoreboard->pendingWrites(0));

#ifdef Y2_HAS_K1
 normal_snapshot(gpu,"terminal40_a");normal_snapshot(gpu,"terminal40_b");
 if(cfg.m_shader_config.dtc_l1_invalidate_on_source_event){assert(ld->m_dtc_invalidation.requests==4);assert(ld->m_dtc_invalidation.first_request_cycle==10&&ld->m_dtc_invalidation.first_ordinary_commit_cycle==23);assert(ld->m_dtc_invalidation.source_counts[1]==2&&ld->m_dtc_invalidation.source_counts[2]==1&&ld->m_dtc_invalidation.source_counts[3]==1);}
#endif
 // Empty-cluster actual source selection, bounded clock ticks, no kernel.
 auto before_idle=gpu->global_cycle();unsigned ticks=0;
 while(gpu->global_cycle()<before_idle+3&&ticks++<1000)gpu->cycle();
 assert(gpu->global_cycle()==before_idle+3);
#ifdef Y2_HAS_K1
 if(cfg.m_shader_config.dtc_l1_invalidate_on_source_event){assert(ld->m_dtc_invalidation.requests==7);assert(ld->m_dtc_invalidation.source_counts[1]==5);auto*other=gpu->get_simt_core_clusters()[1]->get_shader_cores()[0]->m_ldst_unit;assert(other->m_dtc_invalidation.requests==4&&other->m_dtc_invalidation.source_counts[3]==1&&other->m_dtc_invalidation.source_counts[1]==3);}
 normal_snapshot(gpu,"terminal43");
#endif
 stats=dtc_l1::paper_frontend_stats{};ld->get_dtc_l1_stats(stats);dump_all_stats(stats);
 std::cout<<"Y2_RESULT {\"cycles\":"<<gpu->global_cycle()<<",\"packets\":"<<transport.requests.size()<<",\"bytes\":"<<transport.bytes<<",\"ordinary_packets\":"<<ordinary_transport.requests.size()<<",\"ordinary_bytes\":"<<ordinary_transport.bytes<<",\"retired\":"<<stats.oo_retire_count<<",\"refs\":"<<stats.oo_active_refs<<",\"allocated\":"<<stats.oo_physical_allocated<<",\"wb_blocked\":"<<stats.oo_ready_but_writeback_blocked_cycles<<",\"finite\":[";for(unsigned i=0;i<stats.finite_service.size();++i){if(i)std::cout<<",";std::cout<<stats.finite_service[i];}std::cout<<"]}\n";return 0;
}
