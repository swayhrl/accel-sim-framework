// Small known-mask production cache driver. Byte values are NOT a simulator output.
// Links unchanged Core7b8 archives; external lower response carries sector labels.
#include <cassert>
#include <cstdio>
#include <deque>
#include <set>
#include <sys/wait.h>
#include <unistd.h>
#include "gpgpu_context.h"
#include "gpu-sim.h"
#include "icnt_wrapper.h"
#include "l2cache.h"
#include "option_parser.h"
#include "trace_driven.h"
struct port : mem_fetch_interface {
  std::deque<mem_fetch *> packets;
  bool full(unsigned,bool) const override{return false;}
  void push(mem_fetch *mf) override {packets.push_back(mf);}
};
struct inspected_cache : l2_cache {
  using l2_cache::l2_cache;
  mem_access_byte_mask_t dirty(unsigned idx) const{return m_tag_array->get_block(idx)->get_dirty_byte_mask();}
};
struct fixture {
  gpgpu_context ctx;gpgpu_sim_config cfg;trace_config trace;exec_gpgpu_sim *gpu;
  partition_mf_allocator *allocator;inspected_cache *cache;port lower;unsigned long long time=1;
  std::set<unsigned> committed;unsigned lower_reads=0;
  fixture(int argc,char **argv):cfg(&ctx){
    auto op=option_parser_create();ctx.ptx_reg_options(op);ctx.func_sim->ptx_opcocde_latency_options(op);icnt_reg_options(op);cfg.reg_options(op);trace.reg_options(op);
    for(int i=2;i<argc;++i)option_parser_cfgfile(op,argv[i]);cfg.init();trace.parse_config();option_parser_destroy(op);
    gpu=new exec_gpgpu_sim(cfg,&ctx);gpu->gpu_sim_cycle=time;auto mc=gpu->getMemoryConfig();allocator=new partition_mf_allocator(mc);
    auto &cc=const_cast<memory_config *>(mc)->m_L2_config;
    cache=new inspected_cache("LANE3_MASK_ONLY",cc,0,0,&lower,allocator,IN_PARTITION_L2_MISS_QUEUE,gpu,L2_GPU_CACHE);
  }
  void tick(){assert(time==gpu->gpu_sim_cycle);cache->cycle();gpu->gpu_sim_cycle=++time;}
  mem_fetch *make(new_addr_type addr,bool write,unsigned bytes){
    assert((bytes==4||bytes==8||bytes==32) && (addr&31)+bytes<=32);
    active_mask_t active;active.set(0);mem_access_sector_mask_t sector;sector.set((addr>>5)&3);mem_access_byte_mask_t mask;
    for(unsigned i=0;i<bytes;++i)mask.set((addr&127)+i);
    return allocator->alloc(addr,write?GLOBAL_ACC_W:GLOBAL_ACC_R,active,mask,sector,32,write,time,0,0,0,NULL,0);
  }
  void access(mem_fetch *mf){
    auto mask=mf->get_access_byte_mask();auto sector=mf->get_access_sector_mask();
    for(unsigned n=0;n<100;++n){std::list<cache_event> events;auto status=cache->access(mf->get_addr(),mf,time,events);tick();assert(mf->get_access_byte_mask()==mask && mf->get_access_sector_mask()==sector);if(status!=RESERVATION_FAIL)return;}
    assert(!"cache access timeout");
  }
  unsigned index(mem_fetch *mf){unsigned idx;auto status=cache->ft_raw_probe_for_test(mf,idx);assert(status==HIT||status==SECTOR_MISS||status==HIT_RESERVED);return idx;}
  void fill_pending(){
    for(unsigned n=0;n<100;++n){tick();if(!lower.packets.empty())break;}
    while(!lower.packets.empty()){
      auto mf=lower.packets.front();lower.packets.pop_front();assert(!mf->get_is_write());++lower_reads;
      mf->set_ft_wb_data({{101,202,303,404}});
      for(unsigned n=0;;++n){assert(n<100);auto result=cache->ep_l2_payload_fill_request(mf,time);tick();if(result==ep_l2_payload_store::GRANTED)break;}
      cache->fill(mf,time);tick();
    }
  }
  void retire(){
    for(unsigned n=0;cache->access_ready();++n){assert(n<100);if(cache->ft_response_ready(time)){
      auto mf=cache->peek_next_access();assert(committed.insert(mf->get_request_uid()).second);cache->commit_next_access();
    }tick();}
    assert(cache->mshr_entries_used()==0 && cache->ft_pending_lower_reads()==0 && cache->ep_l2_payload_pending_operations()==0);
  }
};
int main(int argc,char **argv){
  assert(argc>=7);setvbuf(stdout,NULL,_IOLBF,0);std::string scenario=argv[1];fixture f(argc,argv);
  if(scenario=="mask32"||scenario=="mask64"){
    unsigned width=scenario=="mask32"?4:8;unsigned offset=scenario=="mask32"?8:32;
    auto a=f.make(0x1000+(width==8?24:0),true,width);auto b=f.make(0x1000+offset,true,width);
    f.access(a);f.access(b);auto index=f.index(b);auto expect=a->get_access_byte_mask()|b->get_access_byte_mask();
    assert(f.cache->dirty(index)==expect && expect.count()==2*width);
    auto h=f.cache->ep_l2_tag_payload_handle_for_test(index);const auto &s=f.cache->ep_l2_payload_for_test().inspect(h);
    assert(s.versions[(b->get_addr()>>5)&3]==(unsigned long long)b->get_request_uid()+1);
    if(width==8)assert(s.versions[0]==(unsigned long long)a->get_request_uid()+1);
    auto read=f.make(0x1000,false,32);f.access(read);f.fill_pending();f.retire();
    assert(f.cache->dirty(index)==expect && f.committed.size()==1);
    printf("MASK_PRODUCTION_PASS|case=%s|mode=%u|dirty_bytes=%zu|mask_preserved=1|uncovered_bytes_numeric=UNOBSERVABLE|lower_reads=%u|read_exact_once=1|pending_drained=1\n",scenario.c_str(),f.gpu->getMemoryConfig()->m_L2_config.ep_l2_ft_mode(),expect.count(),f.lower_reads);
    delete a;delete b;delete read;
  }else if(scenario=="snapshot"){
    auto read=f.make(0x2000,false,32);f.access(read);f.fill_pending();
    for(unsigned n=0;!f.cache->ft_response_ready(f.time);++n){assert(n<100);f.tick();}
    auto response=f.cache->peek_next_access();assert(response==read);auto snapshot=response->get_ft_wb_data();auto h=f.cache->ep_l2_tag_payload_handle_for_test(f.index(read));
    auto write=f.make(0x2000,true,4);auto pins=f.cache->ep_l2_payload_for_test().inspect(h).pins;assert(pins==1);
    for(unsigned i=0;i<5;++i){std::list<cache_event> e;assert(f.cache->access(write->get_addr(),write,f.time,e)==RESERVATION_FAIL);assert(response->get_ft_wb_data()==snapshot);assert(f.cache->ep_l2_payload_for_test().inspect(h).pins==pins);f.tick();}
    // A later same-line producer cannot alter a response held at the consumer.
    f.retire();assert(f.committed.size()==1 && f.cache->ep_l2_payload_for_test().inspect(h).pins==0);f.access(write);
    assert(response->get_ft_wb_data()==snapshot && f.cache->ep_l2_payload_for_test().inspect(h).versions[0]==(unsigned long long)write->get_request_uid()+1);
    puts("SNAPSHOT_PRODUCTION_PASS|held_cycles=5|partial_write_refused_while_pinned=1|response_snapshot_unchanged_after_later_producer=1|commit_once=1|pins=0");delete read;delete write;
  }else if(scenario=="stale_handle"){
    ep_l2_payload_store pool(2,2,16);auto old=pool.reserve(0,ep_l2_payload_store::RESIDENT,0x1000,ep_l2_payload_store::RESIDENT_VALID);pool.release(old);
    auto fresh=pool.reserve(0,ep_l2_payload_store::RESIDENT,0x2000,ep_l2_payload_store::RESIDENT_VALID);assert(old.generation!=fresh.generation && !pool.handle_live(old));
    pid_t pid=fork();assert(pid>=0);if(!pid){pool.inspect(old);_exit(3);}int status;assert(waitpid(pid,&status,0)==pid && WIFSIGNALED(status) && WTERMSIG(status)==SIGABRT);
    assert(pool.handle_owner_matches(fresh,0x2000) && pool.inspect(fresh).versions[0]==0);pool.release(fresh);assert(pool.pending_operations()==0);
    puts("STALE_HANDLE_PRODUCTION_TYPE_PASS|old_generation_rejected=1|fresh_owner_unchanged=1|not_full_late_packet_or_wraparound_proof=1");
  }else assert(!"unknown scenario");
}
