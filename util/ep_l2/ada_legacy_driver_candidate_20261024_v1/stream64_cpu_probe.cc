#include <bitset>
#include "trace_parser.h"
#include "gpgpu-sim/shader.h"
#include "gpgpu-sim/gpu-cache.h"
#include "gpgpu_context.h"
#include <cassert>
#include <cstdio>
#include <cstdint>
class ProbeConfig:public core_config{
 public:ProbeConfig(gpgpu_context*c):core_config(c){warp_size=32;}
 void init()override{}
};
int main(int argc,char**argv){
 assert(argc==2);trace_parser parser;auto*k=parser.parse_kernel_info(argv[1]);
 unsigned long long a=k->cuda_stream_id,b=a^(1ULL<<40);
 assert(a>0xffffffffULL&&uint32_t(a)==uint32_t(b)&&a!=b);
 gpgpu_context ctx;ProbeConfig cfg(&ctx);warp_inst_t i(&cfg);
 i.initiation_interval=1;active_mask_t mask;mask.set(0);
 i.issue(mask,0,0,0,0,a);assert(i.get_streamID()==a);
 i.issue(mask,0,0,0,0,b);assert(i.get_streamID()==b);
 shd_warp_t w(nullptr,32);w.init(0,0,0,mask,0,a);assert(w.get_streamID()==a);
 cache_stats stats;stats.inc_stats(GLOBAL_ACC_W,MISS,a);stats.inc_stats(GLOBAL_ACC_W,MISS,b);stats.inc_stats(GLOBAL_ACC_W,MISS,b);
 assert(stats(GLOBAL_ACC_W,MISS,false,a)==1&&stats(GLOBAL_ACC_W,MISS,false,b)==2);
 printf("CPU_STREAM64_PASS actual_header=%llx same_low32_other=%llx parser_warp_issue_shader_warp_cache_stats_distinct=1 no_simulator_application_started=1\n",a,b);
 parser.kernel_finalizer(k);
}
