#include <cstdio>
#include <cassert>
#include "gpgpu_context.h"
#include "gpgpu-sim/gpu-sim.h"
#include "gpgpu-sim/icnt_wrapper.h"
#include "gpgpu-sim/l2cache.h"
#include "gpgpu-sim/mem_latency_stat.h"
#include "option_parser.h"
#include "trace_driven.h"
int main(int argc,char**argv){
 gpgpu_context c;gpgpu_sim_config cfg(&c);auto p=option_parser_create();
 c.ptx_reg_options(p);c.func_sim->ptx_opcocde_latency_options(p);icnt_reg_options(p);cfg.reg_options(p);trace_config tc;tc.reg_options(p);
 for(int i=1;i<argc;++i)option_parser_cfgfile(p,argv[i]);
 puts("V5_OPTIONS_BEGIN");option_parser_print(p,stdout);puts("V5_OPTIONS_END");cfg.init();option_parser_destroy(p);
 auto gpu=new exec_gpgpu_sim(cfg,&c);auto mc=gpu->getMemoryConfig();
 auto stats=new memory_stats_t(cfg.num_shader(),gpu->getShaderCoreConfig(),mc,gpu);
 auto part=new memory_partition_unit(0,mc,stats,gpu);
 assert(!part->busy());delete part;delete stats;delete gpu;
 puts("V5_REAL_CONSTRUCTOR_PASS|commands=0|kernels=0|models=0");
}
