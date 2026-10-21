// E DRAFT ONLY: not compiled or executed. Link independently to the final,
// source-verified NEW production archive under the original E native-test lease.
// Requires -I <exact released Core root>; no A source or main changes.
// Real GPU host-memcpy -> real partition -> native Tag/payload; lower completion
// is a bounded external fixture, using production FIFOs and response callbacks.
#include <cassert>
#include <cstdio>
#include <map>
#include <set>
#include "libcuda/gpgpu_context.h"
#include "src/gpgpu-sim/gpu-sim.h"
#include "src/gpgpu-sim/icnt_wrapper.h"
#include "src/gpgpu-sim/l2cache.h"
#include "src/option_parser.h"

struct capacity_test_gpu : exec_gpgpu_sim {
  capacity_test_gpu(const gpgpu_sim_config &c,gpgpu_context *ctx)
      : exec_gpgpu_sim(c,ctx) {}
  memory_partition_unit *partition() { return m_memory_partition_unit[0]; }
};

struct capacity_host_fixture {
  using versions=std::array<unsigned long long,4>;
  gpgpu_context ctx;
  gpgpu_sim_config cfg;
  capacity_test_gpu *gpu;
  memory_partition_unit *part;
  memory_sub_partition *sp;
  partition_mf_allocator *alloc;
  std::map<new_addr_type,mem_fetch *> lower_reads;
  std::set<unsigned> sent,received;
  unsigned lower_issued=0;

  capacity_host_fixture(const char *base,const char *qualified_on_overlay)
      : cfg(&ctx) {
    auto p=option_parser_create();
    ctx.ptx_reg_options(p);ctx.func_sim->ptx_opcocde_latency_options(p);
    icnt_reg_options(p);cfg.reg_options(p);
    option_parser_cfgfile(p,base);option_parser_cfgfile(p,qualified_on_overlay);
    // One physical slice bounds this native fixture's memory. Scale64 and the
    // actual native set/way/role dimensions remain completely unchanged.
    const char *args[]={"E-capacity-host-prefill",
      "-gpgpu_n_mem","1","-gpgpu_n_sub_partition_per_mchannel","1",
      "-gpgpu_perf_sim_memcpy","1","-gpgpu_simple_dram_model","0",
      "-gpgpu_ep_l2_ft_mode","1","-gpgpu_ep_l2_wbuf_entries","16"};
    option_parser_cmdline(p,sizeof(args)/sizeof(args[0]),args);
    cfg.init();option_parser_destroy(p);
    gpu=new capacity_test_gpu(cfg,&ctx);part=gpu->partition();
    sp=part->get_sub_partition(0);alloc=new partition_mf_allocator(gpu->getMemoryConfig());
    const auto &c=gpu->getMemoryConfig()->m_L2_config;
    assert(gpu->getMemoryConfig()->m_n_mem_sub_partition==1);
    assert(c.ep_l2_large_enabled() && c.get_nset()==4096 && c.get_assoc()==16);
    assert(cache()->ep_l2_payload_for_test().physical_slots()==74752);
    assert(cache()->ep_l2_payload_for_test().resident_capacity()==65536);
  }
  ~capacity_host_fixture() {delete alloc;delete gpu;}
  l2_cache *cache() {return sp->ft_cache_for_test();}
  unsigned long long clock() const {return gpu->gpu_sim_cycle+gpu->gpu_tot_sim_cycle;}
  unsigned long long grants() {return cache()->ep_l2_payload_for_test().bank_grants();}
  mem_fetch *make(new_addr_type address,bool write=false) {
    active_mask_t active;active.set(0);mem_access_byte_mask_t bytes;
    unsigned sec=(address>>5)&3;
    for(unsigned b=sec*32;b<(sec+1)*32;++b)bytes.set(b);
    mem_access_sector_mask_t sectors;sectors.set(sec);
    return alloc->alloc(address,write?GLOBAL_ACC_W:GLOBAL_ACC_R,active,bytes,sectors,
      32,write,clock(),0,0,0,nullptr,0);
  }
  l2_access_plan plan(new_addr_type address) {
    auto r=make(address);l2_access_plan p;cache()->preview_access(address,r,p);delete r;return p;
  }
  ep_l2::PayloadHandle handle(new_addr_type address) {
    auto p=plan(address);assert(p.probe_status==HIT);
    return cache()->ep_l2_tag_payload_handle_for_test(p.cache_index);
  }
  void warm(new_addr_type address,size_t count) {
    auto before=grants();gpu->perf_memcpy_to_gpu(address,count);assert(grants()==before);
  }
  bool try_warm(new_addr_type address,unsigned sec=0) {
    mem_access_sector_mask_t m;m.set(sec);
    return sp->ft_try_force_l2_tag_update(address,clock(),m);
  }
  void issue(mem_fetch *r) {
    assert(sent.insert(r->get_request_uid()).second && !sp->full());sp->push(r,clock());
  }
  void return_zero_read(new_addr_type address) {
    auto it=lower_reads.find(address);assert(it!=lower_reads.end());
    auto r=it->second;lower_reads.erase(it);
    assert(!sp->dram_L2_queue_full());r->set_ft_wb_data(versions{{0,0,0,0}});
    r->set_reply();sp->dram_L2_queue_push(r);
  }
  void step(bool return_lower=true) {
    part->cache_cycle(clock());cache()->ft_assert_quota();
    // This fixture issues no dirty eviction. Any unexpected WB is a failure,
    // rather than a fake completion that could hide a lost dirty version.
    while(!sp->L2_dram_queue_empty()) {
      auto r=sp->L2_dram_queue_top();
      assert(r->get_access_type()!=L2_WRBK_ACC);
      sp->L2_dram_queue_pop();++lower_issued;
      assert(lower_reads.insert({r->get_addr(),r}).second);
    }
    if(return_lower) {
      while(!lower_reads.empty() && !sp->dram_L2_queue_full())
        return_zero_read(lower_reads.begin()->first);
    }
    assert(grants()==0);++gpu->gpu_sim_cycle;
  }
  void until_response(bool return_lower=true) {
    for(unsigned n=0;n<2000 && !sp->ep_l2_l2icnt_occupancy();++n)step(return_lower);
    assert(sp->ep_l2_l2icnt_occupancy());
  }
  void consume(mem_fetch *r,bool version_zero) {
    until_response();assert(sp->top()==r);
    assert(received.insert(r->get_request_uid()).second);
    if(version_zero) {
      assert(!r->get_is_write() && r->has_ft_wb_data());
      assert(r->get_ft_wb_data()[(r->get_addr()>>5)&3]==0);
    }
    assert(sp->pop()==r);delete r;
  }
  void drain() {
    for(unsigned n=0;n<2000 && part->busy();++n) {
      assert(!sp->ep_l2_l2icnt_occupancy());step();
    }
    assert(!part->busy() && sp->l2_char_no_resource_leak());
    assert(lower_reads.empty() && cache()->ft_drained());
    auto &p=cache()->ep_l2_payload_for_test();
    assert(p.ownership_consistent_deep() && p.pending_sector_count()==0);
    assert(cache()->mshr_entries_used()==0 && cache()->ep_l2_descriptor_count_used()==0);
    assert(cache()->ep_l2_wad_occupancy()==0 && p.bank_grants()==0);
    assert(sent==received);
  }
};

static void full_address_and_version_zero(const char *base,const char *overlay) {
  capacity_host_fixture f(base,overlay);
  // Find a real native Tag index outside the original1024-tag range. Address
  // selection uses the native index function; it never forces a Tag or hit.
  new_addr_type a=0x100004000ULL;
  for(unsigned n=0;n<131072 && f.plan(a).cache_index<1024;++n)a+=128;
  assert(a>0xffffffffULL && f.plan(a).cache_index>=1024);
  auto before=f.sp->ft_memcpy_offset_for_test();f.warm(a,0);
  assert(f.sp->ft_memcpy_offset_for_test()==before);
  f.warm(a+31,2);auto h=f.handle(a);
  assert(h==f.handle(a+32) && h.payload_id>=1024);
  assert(f.plan(a&0xffffffffULL).probe_status==MISS);
  auto &p=f.cache()->ep_l2_payload_for_test();
  assert(p.inspect(h).owner==a && p.inspect(h).ready_sector_mask.to_ulong()==3);
  f.warm(a+32,32);assert(f.handle(a)==h);
  f.gpu->gpu_tot_sim_cycle+=1000000;
  f.warm(a+96,32);assert(f.handle(a)==h);
  assert(p.inspect(h).ready_sector_mask.to_ulong()==11);
  for(unsigned sec:{0u,1u,3u}) {auto r=f.make(a+sec*32);f.issue(r);f.consume(r,true);}
  assert(f.lower_issued==0);f.drain();
  puts("E_CAPACITY_HOST_PREFILL_FULL_ADDRESS_SCALED_INDEX_SECTORS_EPOCH_VERSION_ZERO PASS");
}

static void dirty_owner_refusal(const char *base,const char *overlay) {
  capacity_host_fixture f(base,overlay);const new_addr_type a=0x100004000ULL;
  f.warm(a,32);auto w=f.make(a,true);const auto write_version=(unsigned long long)w->get_request_uid()+1;
  f.issue(w);f.consume(w,false);f.drain();
  auto h=f.handle(a);auto before=f.cache()->ep_l2_payload_for_test().inspect(h);
  const auto offset=f.sp->ft_memcpy_offset_for_test();
  assert(before.status==ep_l2_payload_store::RESIDENT_DIRTY);
  assert(before.versions[0]==write_version);
  assert(!f.try_warm(a));
  assert(f.handle(a)==h && f.sp->ft_memcpy_offset_for_test()==offset);
  const auto &after=f.cache()->ep_l2_payload_for_test().inspect(h);
  assert(after.versions==before.versions && after.generation==before.generation);
  assert(after.owner==before.owner && after.status==before.status);
  f.drain();puts("E_CAPACITY_HOST_PREFILL_DIRTY_REFUSAL_PRESERVES_IDENTITY_VERSION_OFFSET PASS");
}

static void pending_and_response_refusal(const char *base,const char *overlay) {
  capacity_host_fixture f(base,overlay);
  const new_addr_type a=0x100004000ULL,b=a+128;
  auto r=f.make(a);f.issue(r);auto offset=f.sp->ft_memcpy_offset_for_test();
  assert(!f.try_warm(b) && f.sp->ft_memcpy_offset_for_test()==offset);
  for(unsigned n=0;n<2000 && f.lower_reads.empty();++n)f.step(false);
  assert(f.lower_reads.count(a));
  assert(!f.try_warm(b) && f.sp->ft_memcpy_offset_for_test()==offset);
  f.return_zero_read(a);f.until_response(false);
  // A queued actual requester response still prevents host prefill.
  assert(!f.try_warm(b) && f.sp->ft_memcpy_offset_for_test()==offset);
  f.consume(r,true);f.drain();assert(f.try_warm(b));
  auto q=f.make(b);f.issue(q);f.consume(q,true);f.drain();
  assert(f.lower_issued==1);
  puts("E_CAPACITY_HOST_PREFILL_PENDING_RESPONSE_REFUSAL_REAL_RETURN_DRAIN_RETRY PASS");
}

int main(int argc,char **argv) {
  assert(argc==3);setvbuf(stdout,nullptr,_IOLBF,0);
  full_address_and_version_zero(argv[1],argv[2]);
  dirty_owner_refusal(argv[1],argv[2]);
  pending_and_response_refusal(argv[1],argv[2]);
  puts("E_CAPACITY_HOST_PREFILL_PRODUCTION_SUITE PASS");
}
