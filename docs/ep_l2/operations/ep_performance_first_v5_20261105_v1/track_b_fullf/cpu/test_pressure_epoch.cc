// Production l2_cache + real allocator/mshr/Tag/lower/response hooks.
#include <cassert>
#include <cstdio>
#include <deque>
#include <map>
#include <set>
#include "/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v5_20261105_v1/track_b_fullf/core/libcuda/gpgpu_context.h"
#include "/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v5_20261105_v1/track_b_fullf/core/src/gpgpu-sim/gpu-sim.h"
#include "/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v5_20261105_v1/track_b_fullf/core/src/gpgpu-sim/icnt_wrapper.h"
#include "/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v5_20261105_v1/track_b_fullf/core/src/gpgpu-sim/l2cache.h"
#include "/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v5_20261105_v1/track_b_fullf/core/src/gpgpu-sim/ep-l2-ro-sha256.h"
#include "/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v5_20261105_v1/track_b_fullf/core/src/option_parser.h"
struct lower : mem_fetch_interface {
  bool blocked=true;std::deque<mem_fetch*> packets;
  bool full(unsigned,bool)const override{return blocked;}
  void push(mem_fetch*m)override{packets.push_back(m);}
};
struct rig {
  gpgpu_context ctx;gpgpu_sim_config cfg;exec_gpgpu_sim *gpu;
  partition_mf_allocator *alloc;l2_cache *cache;lower port;
  unsigned time=1;std::set<unsigned> replies;bool validate_reference=true;
  rig(const char *base,const char *overlay,const char *binding,unsigned d,unsigned b,unsigned sets=1,bool activate=true,unsigned pressure=0):cfg(&ctx) {
    option_parser_t p=option_parser_create();ctx.ptx_reg_options(p);ctx.func_sim->ptx_opcocde_latency_options(p);icnt_reg_options(p);cfg.reg_options(p);
    option_parser_cfgfile(p,base);option_parser_cfgfile(p,overlay);option_parser_cfgfile(p,binding);
    std::string ps=std::to_string(pressure),ds=std::to_string(d),bs=std::to_string(b),geometry="S:"+std::to_string(sets)+":128:1,L:B:m:L:L,A:128:32,1024:0,32";
    const char *a[]={"ro-test","-gpgpu_ep_l2_ft_mode","2","-gpgpu_ep_l2_wbuf_entries","16","-gpgpu_ep_l2_ro_tag_detach",ds.c_str(),"-gpgpu_ep_l2_ro_line_mshr_bypass",bs.c_str(),"-gpgpu_cache:dl2",geometry.c_str(),"-gpgpu_ep_l2_ro_pressure_epoch",ps.c_str()};
    option_parser_cmdline(p,13,a);cfg.init();option_parser_destroy(p);
    gpu=new exec_gpgpu_sim(cfg,&ctx);auto mc=gpu->getMemoryConfig();alloc=new partition_mf_allocator(mc);
    cache=new l2_cache("RO_RUNTIME",const_cast<memory_config*>(mc)->m_L2_config,0,0,&port,alloc,IN_PARTITION_L2_MISS_QUEUE,gpu,L2_GPU_CACHE);
    if(activate){cache->ro_bind_commandlist(command.c_str());cache->ro_begin_epoch();}
  }
  static std::string command;
  ~rig(){delete cache;delete alloc;delete gpu;}
  mem_fetch*make(new_addr_type a,mem_access_type type=GLOBAL_ACC_R,bool wr=false){
    active_mask_t active;active.set(0);mem_access_byte_mask_t bytes;unsigned n=(a>>5)&3;
    for(unsigned b=32*n;b<32*n+32;++b)bytes.set(b);
    return alloc->alloc(a,type,active,bytes,mem_access_sector_mask_t(1<<n),32,wr,time,0,0,0,NULL,0);
  }
  void tick(){gpu->gpu_sim_cycle=time++;cache->cycle();}
  cache_request_status admit(mem_fetch*m) {
    // Wait only for the explicit paid lookup. Never hide a capacity refusal.
    for(unsigned wait=0;wait<8;++wait) {
      gpu->gpu_sim_cycle=time;
      auto v=cache->tvd_frontend(m,time,true);
      if(v==l2_cache::TVD_WAIT){tick();continue;}
      assert(v==l2_cache::TVD_NORMAL);
      cache->ro_frontend_cycle(m);l2_access_plan p;cache->preview_access(m->get_addr(),m,p);
      if(!p.ep_l2_ro_lookup_wait)break;
      tick();
    }
    gpu->gpu_sim_cycle=time;
    l2_access_plan plan;cache->preview_access(m->get_addr(),m,plan);
    std::list<cache_event> ev;auto r=cache->access(m->get_addr(),m,time,ev);tick();return r;
  }
  ep_l2::PayloadHandle tag(unsigned i=0){return cache->ep_l2_tag_payload_handle_for_test(i);}
  void issue(){port.blocked=false;for(unsigned n=0;n<2048&&!cache->miss_queue_empty();++n)tick();assert(cache->miss_queue_empty());}
  bool fill(mem_fetch*m){
    gpu->gpu_sim_cycle=time;
    bool done;
    if(m->ro_lower_packet()) {
      std::array<unsigned long long,4> v;for(unsigned n=0;n<4;++n)v[n]=0x1000+(m->get_addr()/128)*4+n;
      m->set_ft_wb_data(v);done=cache->ro_return(m,time);
    }
    else {done=cache->ep_l2_payload_fill_request(m,time)==ep_l2_payload_store::GRANTED;if(done)cache->fill(m,time);}
    tick();if(done&&m->ro_lower_packet())delete m;return done;
  }
  void consume(unsigned expected){
    for(unsigned n=0;n<10000&&replies.size()<expected;++n){
      gpu->gpu_sim_cycle=time;
      if(cache->access_ready()&&cache->ft_response_ready(time)){
        auto m=cache->peek_next_access();assert(replies.insert(m->get_request_uid()).second);
        if(validate_reference && cache->ro_enabled() && m->get_access_type()==GLOBAL_ACC_R && m->get_addr()<0x40000) {
          assert(m->has_ft_wb_data());for(unsigned n=0;n<4;++n)if(m->get_access_sector_mask().test(n))
            assert(m->get_ft_wb_data()[n]==0x1000+(m->get_addr()/128)*4+n);
        }
        // global cycle must be the read-grant/enqueue cycle.
        gpu->gpu_sim_cycle=time;cache->commit_next_access();delete m;
      }
      tick();
    }
    assert(replies.size()==expected);
  }
  void finish(){assert(cache->ft_drained());assert(!cache->ep_l2_descriptor_count_used());cache->ro_end_epoch();cache->ro_print(stdout,0);}
};
std::string rig::command;

static void drain(rig &f,unsigned count){
 f.issue();
 while(!f.port.packets.empty()){auto p=f.port.packets.back();f.port.packets.pop_back();while(!f.fill(p)){}}
 f.consume(count);f.finish();
}
static void no_pressure(const char*b,const char*o,const char*c,unsigned policy){
 rig f(b,o,c,1,1,1024,true,policy);f.validate_reference=false;
 for(unsigned i=0;i<20;++i)assert(f.admit(f.make(i*128))!=RESERVATION_FAIL);
 assert(f.cache->ep_l2_descriptor_count_used()==20);
 assert(!f.cache->ro_pressure_epoch_active_for_test());
 assert(f.cache->mshr_entries_used()==(policy?20u:0u));
 assert(f.cache->ro_query_count_for_test()==(policy?0u:20u));
 f.issue();assert(f.port.packets.size()==20);
 for(auto p:f.port.packets)assert(p->ro_lower_packet()==!policy);
 const auto before=f.cache->ep_l2_descriptor_count_used();
 auto writer=f.make(0,GLOBAL_ACC_W,true);bool rejected=false;
 try{f.admit(writer);}catch(const std::logic_error&){rejected=true;}
 assert(rejected && before==f.cache->ep_l2_descriptor_count_used());delete writer;
 while(!f.port.packets.empty()){auto p=f.port.packets.back();f.port.packets.pop_back();while(!f.fill(p)){}}
 f.consume(20);const auto end=f.time;f.finish();
 printf("B1_DELTA|case=no_pressure|policy=%u|queries=%llu|cycle=%u|PASS\n",policy,f.cache->ro_query_count_for_test(),end);
}
static void tag_activation(const char*b,const char*o,const char*c){
 rig f(b,o,c,1,1,1,true,1);f.validate_reference=false;
 assert(f.admit(f.make(0))!=RESERVATION_FAIL);auto native=f.tag();
 assert(!f.cache->ro_pressure_epoch_active_for_test());
 auto pending=f.make(128);l2_access_plan observation;
 for(unsigned i=0;i<10;++i)f.cache->preview_access(128,pending,observation);
 assert(!f.cache->ro_pressure_epoch_active_for_test() && !f.cache->ro_query_count_for_test());
 assert(f.admit(pending)==RESERVATION_FAIL);
 assert(f.cache->ro_pressure_epoch_active_for_test() && f.cache->ro_query_count_for_test()==1);
 assert(f.cache->ep_l2_descriptor_count_used()==1 && f.tag()==native);
 f.issue();assert(f.port.packets.size()==1 && !f.port.packets.front()->ro_lower_packet());
 auto np=f.port.packets.front();f.port.packets.pop_front();while(!f.fill(np)){}f.consume(1);
 assert(f.admit(pending)!=RESERVATION_FAIL);auto old=f.tag();
 assert(f.cache->ro_pressure_epoch_active_for_test());
 auto alien=f.make(128,TEXTURE_ACC_R);
 assert(f.admit(alien)==RESERVATION_FAIL);delete alien;
 auto next=f.make(256);assert(f.admit(next)!=RESERVATION_FAIL);auto fresh=f.tag();assert(old!=fresh);
 f.issue();assert(f.port.packets.size()==2);
 auto newer=f.port.packets.back();f.port.packets.pop_back();assert(newer->ro_lower_packet());
 while(!f.fill(newer)){}
 auto older=f.port.packets.front();f.port.packets.pop_front();assert(older->ro_lower_packet());
 assert(older->get_ep_l2_payload_id()==old.payload_id);
 while(!f.fill(older)){}
 assert(f.tag()==fresh);
 for(unsigned i=0;i<8;++i)f.tick(); // ICNT response stall retains actual descriptor/pins.
 assert(f.cache->ep_l2_descriptor_count_used()==2);
 f.consume(3);f.finish();
 puts("B1_DELTA|case=tag_pressure_timed_activation_preview_purity_native_owner_late_return_icnt|PASS");
}
static void line_activation(const char*b,const char*o,const char*c){
 rig f(b,o,c,1,1,1024,true,1);f.validate_reference=false;
 for(unsigned i=0;i<128;++i)assert(f.admit(f.make(i*128))!=RESERVATION_FAIL);
 assert(!f.cache->ro_pressure_epoch_active_for_test() && f.cache->mshr_entries_used()==128);
 auto ro=f.make(128*128);assert(f.admit(ro)!=RESERVATION_FAIL);
 assert(f.cache->ro_pressure_epoch_active_for_test() && f.cache->ro_query_count_for_test()==1);
 assert(f.cache->mshr_entries_used()==128 && f.cache->ep_l2_descriptor_count_used()==129);
 auto synthetic=f.make(128*128,L2_WR_ALLOC_R);assert(f.admit(synthetic)==RESERVATION_FAIL);delete synthetic;
 f.issue();unsigned nr=0,nn=0;for(auto q:f.port.packets){nr+=q->ro_lower_packet();nn+=!q->ro_lower_packet();}
 assert(nr==1 && nn==128);drain(f,129);
 puts("B1_DELTA|case=line128_activation_shared_descriptors_mixed_return_native_owner|PASS");
}
int main(int argc,char**argv){
 assert(argc==5);rig::command=argv[4];
 no_pressure(argv[1],argv[2],argv[3],0);no_pressure(argv[1],argv[2],argv[3],1);
 tag_activation(argv[1],argv[2],argv[3]);line_activation(argv[1],argv[2],argv[3]);
 puts("PFV5_B1_PRODUCTION_CPU|PASS|full_application_models=0");
}
