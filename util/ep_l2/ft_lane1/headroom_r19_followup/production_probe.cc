// r19 affected-path fixture only: link frozen official production archives.
// No runtime implementation, private-state mutation, or option override.
#include <cassert>
#include <cmath>
#include <cstdio>
#include <map>
#include <set>
#include <vector>
#include "gpgpu_context.h"
#include "gpu-sim.h"
#include "icnt_wrapper.h"
#include "l2cache.h"
#include "mem_latency_stat.h"
#include "option_parser.h"
#include "trace_driven.h"

class clock_probe_gpu : public exec_gpgpu_sim {
 public:
  using exec_gpgpu_sim::exec_gpgpu_sim;
  using exec_gpgpu_sim::next_clock_domain;
};
using versions=std::array<unsigned long long,4>;
struct fixture {
  clock_probe_gpu &gpu; memory_partition_unit &part;
  const memory_config *mc;
  partition_mf_allocator allocator;
  unsigned long long ticks[4]={0,0,0,0};
  unsigned long long last_cycle=(unsigned long long)-1,bank_ops[4]={0,0,0,0};
  unsigned long long max_bank_ops=0;
  bool separate_wad=false,delay_dumped=false;
  std::map<unsigned,mem_fetch *> live;
  std::map<unsigned,unsigned long long> delay_birth;
  std::set<unsigned> delay_verified;
  std::map<unsigned,versions> expected;
  std::set<unsigned> responses;
  fixture(clock_probe_gpu &g,memory_partition_unit &p):gpu(g),part(p),mc(g.getMemoryConfig()),allocator(mc){}
  memory_sub_partition *sp(unsigned i=0){return part.get_sub_partition(i);}
  void step(){
    // Native masks from gpu-sim.cc: CORE=1,L2=2,DRAM=4,ICNT=8.
    int mask=gpu.next_clock_domain();
    auto physical=gpu.gpu_sim_cycle+gpu.gpu_tot_sim_cycle;
    if(physical!=last_cycle){last_cycle=physical;for(auto &n:bank_ops)n=0;}
    if(mask&8){++ticks[3];for(unsigned i=0;i<2;++i)if(auto mf=sp(i)->pop()){
      assert(expected.count(mf->get_request_uid()) && responses.insert(mf->get_request_uid()).second);
      if(!mf->get_is_write()){
        assert(mf->has_ft_wb_data());unsigned sec=(mf->get_addr()>>5)&3;
        assert(mf->get_ft_wb_data()[sec]==expected.at(mf->get_request_uid())[sec]);
      }
      live.erase(mf->get_request_uid());delete mf;
    }}
    // Match production order: response pop, real detailed DRAM, L2, CORE count.
    if(mask&4){
      ++ticks[2];part.dram_cycle();
      for(const auto &entry:live){
        auto status=entry.second->get_status();
        if(status==IN_PARTITION_DRAM_LATENCY_QUEUE){
          if(!delay_birth.count(entry.first))delay_birth[entry.first]=physical;
          if(!delay_dumped){
            char *buffer=NULL;size_t bytes=0;FILE *stream=open_memstream(&buffer,&bytes);
            assert(stream);part.print(stream);fclose(stream);std::string snapshot(buffer,bytes);free(buffer);
            std::string exact="Ready @ "+std::to_string(physical+mc->dram_latency)+" - ";
            assert(snapshot.find(exact)!=std::string::npos);
            printf("R19_DELAY_CAPTURE|gpu_cycle=%llu|ready_gpu_cycle=%llu|fixed_latency_gpu_cycles=%u\n",physical,physical+mc->dram_latency,mc->dram_latency);
            fputs(snapshot.c_str(),stdout);delay_dumped=true;
          }
        }else if(delay_birth.count(entry.first) && !delay_verified.count(entry.first)){
          assert(physical-delay_birth.at(entry.first)>=mc->dram_latency);delay_verified.insert(entry.first);
        }
      }
    }
    if(mask&2){
      ++ticks[1];unsigned long long before[4];
      auto cache=sp()->ft_cache_for_test();for(unsigned b=0;b<4;++b)before[b]=cache->ep_l2_payload_bank_grants(b);
      part.cache_cycle(physical);
      for(unsigned b=0;b<4;++b){bank_ops[b]+=cache->ep_l2_payload_bank_grants(b)-before[b];max_bank_ops=std::max(max_bank_ops,bank_ops[b]);assert(bank_ops[b]<=1);}
      if(!cache->ft_wb_staged() && cache->ep_l2_wad_occupancy())separate_wad=true;
    }
    if(mask&1){++ticks[0];++gpu.gpu_sim_cycle;}
  }
  void wait(unsigned uid){
    auto start=gpu.gpu_sim_cycle;
    while(!responses.count(uid)){assert(gpu.gpu_sim_cycle-start<100000);step();}
  }
  unsigned send(new_addr_type addr,bool write,versions value,unsigned sub=0){
    active_mask_t active;active.set(0);mem_access_sector_mask_t sectors;unsigned sec=(addr>>5)&3;sectors.set(sec);
    mem_access_byte_mask_t bytes;for(unsigned b=sec*32;b<(sec+1)*32;++b)bytes.set(b);
    auto mf=allocator.alloc(addr,write?GLOBAL_ACC_W:GLOBAL_ACC_R,active,bytes,sectors,32,write,
        gpu.gpu_sim_cycle,0,0,0,NULL,0);
    assert(mf->get_tlx_addr().chip==0 && mf->get_sub_partition_id()==sub);
    unsigned uid=mf->get_request_uid();if(write)value[sec]=(unsigned long long)uid+1;
    assert(live.insert({uid,mf}).second);assert(expected.insert({uid,value}).second);assert(!sp(sub)->full());sp(sub)->push(mf,gpu.gpu_sim_cycle);return uid;
  }
  void drain(){
    auto start=gpu.gpu_sim_cycle;
    for(;;){
      bool pending=part.busy();
      for(unsigned i=0;i<2;++i){auto c=sp(i)->ft_cache_for_test();pending|=!sp(i)->l2_char_no_resource_leak()||!c->ft_drained()||!c->miss_queue_empty()||c->mshr_entries_used();}
      if(!pending)break;
      assert(gpu.gpu_sim_cycle-start<100000);step();
    }
  }
};

int main(int argc,char **argv){
  assert(argc>=7);setvbuf(stdout,NULL,_IOLBF,0);
  std::string regime=argv[1];assert(regime=="H0"||regime=="Q4"||regime=="D4"||regime=="D2"||regime=="L25");
  gpgpu_context ctx;gpgpu_sim_config cfg(&ctx);trace_config trace;
  auto parser=option_parser_create();ctx.ptx_reg_options(parser);ctx.func_sim->ptx_opcocde_latency_options(parser);
  icnt_reg_options(parser);cfg.reg_options(parser);trace.reg_options(parser);
  // Every supplied fragment in order, including native trace config. No cmdline
  // parser invocation or fixture-specific queue/clock/geometry override follows.
  for(int i=2;i<argc;++i)option_parser_cfgfile(parser,argv[i]);
  puts("R19_NATIVE_EFFECTIVE_OPTIONS_BEGIN");option_parser_print(parser,stdout);puts("R19_NATIVE_EFFECTIVE_OPTIONS_END");
  cfg.init();trace.parse_config();option_parser_destroy(parser);
  clock_probe_gpu gpu(cfg,&ctx);gpu.gpu_sim_cycle=1;auto mc=gpu.getMemoryConfig();
  assert(mc->m_n_mem==32 && mc->m_n_mem_sub_partition==64 && mc->m_n_sub_partition_per_memory_channel==2);
  assert(!mc->simple_dram_model && !mc->l2_ideal && !mc->seperate_write_queue_enabled);
  assert(mc->dram_latency==(regime=="L25"?25u:100u) && mc->m_L2_config.get_num_lines()==1024 && mc->m_L2_config.get_assoc()==16);
  assert(mc->m_L2_config.ep_l2_ft_mode()==1 || mc->m_L2_config.ep_l2_ft_mode()==2);
  unsigned q0,q1,q2,q3;assert(sscanf(mc->gpgpu_L2_queue_config,"%u:%u:%u:%u",&q0,&q1,&q2,&q3)==4);
  assert(q0==64 && q3==64 && q1==(regime=="H0"?128u:512u) && q2==(regime=="H0"?64u:256u));
  assert(mc->gpgpu_frfcfs_dram_sched_queue_size==(regime=="H0"?128u:512u));
  assert(mc->gpgpu_dram_return_queue_size==(regime=="H0"?192u:768u));
  unsigned shared=mc->gpgpu_frfcfs_dram_sched_queue_size+mc->gpgpu_dram_return_queue_size-(mc->m_n_sub_partition_per_memory_channel-1);
  assert(shared==(regime=="H0"?319u:1279u));
  const double expected_dram_hz=(regime=="D4"||regime=="L25")?3400e6:(regime=="D2"?1700e6:850e6);
  printf("R19_EFFECTIVE|regime=%s|mode=%u|nmem=%u|slices=%u|queues=%u:%u:%u:%u|scheduler=%u|dram_return=%u|shared_credit_derived=%u|private_per_subpart=1|wb_progress_credit=%u|dram_latency_gpu_cycles=%u|detailed_dram=1|expected_dram_hz=%.0f|atom=%u|burst=%u|busW=%u|dram_banks=%u\n",
      regime.c_str(),mc->m_L2_config.ep_l2_ft_mode(),mc->m_n_mem,mc->m_n_mem_sub_partition,q0,q1,q2,q3,mc->gpgpu_frfcfs_dram_sched_queue_size,mc->gpgpu_dram_return_queue_size,shared,mc->gpgpu_l2_wb_progress_credit,mc->dram_latency,expected_dram_hz,mc->dram_atom_size,mc->BL,mc->busW,mc->nbk);
  memory_stats_t stats(cfg.num_shader(),gpu.getShaderCoreConfig(),mc,&gpu);memory_partition_unit part(0,mc,&stats,&gpu);fixture f(gpu,part);
  // Real native clock scheduler, not a hand-coded D4 loop multiplier.
  while(f.ticks[0]<10000)f.step();
  assert(std::abs((double)f.ticks[2]-f.ticks[0]*expected_dram_hz/1132e6)<4);
  assert(f.ticks[0]==f.ticks[1] && f.ticks[0]==f.ticks[3]);
  printf("R19_CLOCK|core_ticks=%llu|l2_ticks=%llu|dram_ticks=%llu|icnt_ticks=%llu|native_next_clock_domain=1\n",f.ticks[0],f.ticks[1],f.ticks[2],f.ticks[3]);
  std::vector<new_addr_type> addresses;
  for(new_addr_type addr=0;addr<128ull*2000000 && addresses.size()<22;addr+=128){
    addrdec_t d;mc->m_address_mapping.addrdec_tlx(addr,&d);
    if(d.chip==0 && d.sub_partition==0 && mc->m_L2_config.set_index(addr)==0)addresses.push_back(addr);
  }
  assert(addresses.size()==22);std::map<new_addr_type,versions> stored;
  auto cache=f.sp()->ft_cache_for_test();
  for(unsigned i=0;i<16;++i){
    versions v={{0,0,0,0}};
    for(unsigned sec:{0u,2u}){auto uid=f.send(addresses[i]+32*sec,true,v);v[sec]=(unsigned long long)uid+1;f.wait(uid);}
    stored[addresses[i]]=v;
  }
  for(unsigned i=16;i<20;++i){
    auto before=cache->ep_l2_wad_lifetime_count();versions zero={{0,0,0,0}};
    auto uid=f.send(addresses[i],true,zero);zero[0]=(unsigned long long)uid+1;stored[addresses[i]]=zero;f.wait(uid);f.drain();
    const auto &got=cache->ft_last_wb_versions();const auto &want=stored.at(addresses[i-16]);
    printf("R19_WB_CHECK|i=%u|before=%llu|after=%llu|want=%llu,%llu,%llu,%llu|got=%llu,%llu,%llu,%llu|staged=%u|wad=%u\n",i,before,cache->ep_l2_wad_lifetime_count(),want[0],want[1],want[2],want[3],got[0],got[1],got[2],got[3],cache->ft_wb_staged(),cache->ep_l2_wad_occupancy());
    cache->ft_print(stdout,0);
    assert(cache->ep_l2_wad_lifetime_count()==before+1 && got==want);
  }
  // Independent cold symbols from untouched lower memory, two real sectors;
  // and a resident read hit to a real UID-labelled store.
  versions zero={{0,0,0,0}};auto cold=f.send(addresses[20],false,zero);auto sector=f.send(addresses[20]+64,false,zero);
  f.wait(cold);f.wait(sector);f.drain();assert(cache->ft_last_wb_versions()==stored.at(addresses[4]));
  auto hit=f.send(addresses[19],false,stored.at(addresses[19]));f.wait(hit);f.drain();
  // A second real subpartition shares the same downstream credit controller.
  new_addr_type other=0;bool found=false;
  for(new_addr_type a=0;a<128ull*100000;++a){addrdec_t d;mc->m_address_mapping.addrdec_tlx(a,&d);if(d.chip==0 && d.sub_partition==1 && a%128==0){other=a;found=true;break;}}
  assert(found);auto remote=f.send(other,false,zero,1);f.wait(remote);f.drain();
  assert(f.delay_dumped && f.delay_verified.size()>=3);
  assert(f.responses.size()==f.expected.size() && cache->ep_l2_wad_lifetime_count()==5 && f.separate_wad);
  assert(part.l2_char_no_credit_leak() && !part.busy());
  for(unsigned i=0;i<2;++i)assert(f.sp(i)->l2_char_no_resource_leak() && f.sp(i)->ft_drained_for_test());
  assert(f.max_bank_ops==1 && cache->ep_l2_payload_for_test().physical_slots()==1168);
  part.print(stdout);
  printf("R19_PRODUCTION_PASS|regime=%s|mode=%u|exact_once=%zu|wb_lower_accept_and_set_done=5|two_dirty_sector_versions=1|cold_sectors=2|subpartitions_exercised=2|credit_drained=1|bank_max_ops_per_physical_cycle=%llu|fixed_delay_gpu_cycles=%u|fixed_delay_verified=1|runtime_archives_unchanged=1\n",regime.c_str(),mc->m_L2_config.ep_l2_ft_mode(),f.responses.size(),f.max_bank_ops,mc->dram_latency);
}
