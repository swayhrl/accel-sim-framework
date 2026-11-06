#include <cassert>
#include <cstdio>
#include <fstream>
#include <sstream>
#include "gpgpu_context.h"
#include "gpu-sim.h"
#include "gpu-cache.h"
#include "ep-l2-ro-oracle.h"
#include "ep-l2-ro-sha256.h"
// Configuration-only derived class uses protected, not private, fields.
// No GPU object, cycle, request, allocator, partition, kernel, or trace-body read.
struct loader_config : cache_config {
 char geometry[64]="S:32:128:8,L:B:m:L:P,A:128:1,128:0,32";
 loader_config(char **v) {
  init(geometry,FuncCachePreferNone);
  m_ep_l2_ft_mode=2;m_ep_l2_wbuf_entries=16;m_ep_l2_payload_mode=2;
  m_ep_l2_descriptor_pool_size=512;m_ep_l2_descriptor_per_line_cap=32;
  m_ep_l2_wad_entries=128;m_ep_l2_bank_ops=1;
  m_ep_l2_tvd_clean=true;m_ep_l2_tvd_dirty=true;
  m_ep_l2_ms_observer=true;m_ep_l2_m0a_stats=true;
  m_ro_tag_detach=true;m_ro_line_mshr_bypass=true;m_ro_pressure_epoch=std::stoul(v[8]);
  m_ro_manifest=v[1];m_ro_manifest_sha256=v[2];m_ro_ranges=v[3];
  m_ro_ranges_sha256=v[4];m_ro_scope=v[5];
 }
};
int main(int argc,char**v) {
 assert(argc==9);
 loader_config cfg(v);
 assert(cfg.get_nset()==32 && cfg.get_assoc()==8 && cfg.get_line_sz()==128);
 {
  // Null dependencies are never used: actual ctor loader+bind only, no timing API.
  l2_cache cache("EXTERNAL_CPU_RO_LOADER_ONLY",cfg,0,0,nullptr,nullptr,
      IN_PARTITION_L2_MISS_QUEUE,nullptr,L2_GPU_CACHE);
  assert(cache.ro_enabled() && cache.ro_tag_detach_enabled_for_test());
  assert(cache.ep_l2_payload_for_test().physical_slots()==1168);
  cache.ro_bind_commandlist(v[6]);
  assert(cache.ro_drained());
  puts("SOURCE812_RO_LOADER_PRODUCTION|new_source_static_library_ctor=1|manifest_sha_verified=1|ranges_sha_verified=1|whole_commandlist_sha_verified=1|FT=2|T=1|M=1|sets=32|ways=8|physical_payload=1168|no_gpu_object=1|no_epoch_started=1|no_request_sent=1|PASS");
 }
 std::ifstream f(v[3]);ep_l2_ro::oracle_certificate cert(f,v[2],v[5]);
 unsigned count=0;unsigned long long n=0,previous=0,first=0,last=0;
 std::ifstream lines(v[3]);std::string row;assert(std::getline(lines,row));
 while(std::getline(lines,row)) {
  if(row.empty() || row=="\r") continue;
  const auto comma=row.find(',');assert(comma!=std::string::npos);
  const uint64_t a=std::stoull(row.substr(0,comma),nullptr,16);
  const uint64_t b=std::stoull(row.substr(comma+1),nullptr,16);
  assert(a%128==0 && b%128==0 && b>=a);
  assert(cert.contains(a) && cert.contains(b));
  assert(!cert.contains(a+1));
  if(count){assert(a>previous);if(a>previous+128)assert(!cert.contains(previous+128));}
  else {first=a;if(a>=128)assert(!cert.contains(a-128));}
  previous=last=b;n+=(b-a)/128+1;++count;
 }
 assert(count==cert.range_count() && n==std::stoull(v[7]));
 if(count)assert(!cert.contains(last+128));
 printf("RO_LOADER_BOUNDARIES_GENERIC|ranges=%u|lines=%llu|line_bytes=128|first_last=PASS|outside_gap=PASS|unaligned=REJECT|scope=TRACE_MODEL_CLOSED_WORLD|epoch=whole_commandlist|domain=CANONICAL_GPU_GLOBAL_VA_NO_TRANSLATION_ALIAS|no_trace_body_read=1|PASS\n",count,n);
}
