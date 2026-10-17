// Read exact ordered application fragments through the production parser.
#include <cassert>
#include <cstdio>
#include "gpgpu_context.h"
#include "gpu-sim.h"
#include "icnt_wrapper.h"
#include "l2cache.h"
#include "mem_latency_stat.h"
#include "option_parser.h"
#include "trace_driven.h"
int main(int argc,char **argv) {
 assert(argc>=6);setvbuf(stdout,NULL,_IOLBF,0);
 gpgpu_context ctx;gpgpu_sim_config cfg(&ctx);trace_config trace;
 auto p=option_parser_create();ctx.ptx_reg_options(p);ctx.func_sim->ptx_opcocde_latency_options(p);
 icnt_reg_options(p);cfg.reg_options(p);trace.reg_options(p);
 for(int i=1;i<argc;++i)option_parser_cfgfile(p,argv[i]);
 puts("NATIVE_EFFECTIVE_OPTIONS_BEGIN");option_parser_print(p,stdout);puts("NATIVE_EFFECTIVE_OPTIONS_END");
 cfg.init();trace.parse_config();option_parser_destroy(p);exec_gpgpu_sim gpu(cfg,&ctx);
 auto mc=gpu.getMemoryConfig();memory_stats_t stats(cfg.num_shader(),gpu.getShaderCoreConfig(),mc,&gpu);
 // Real constructor enforces supported combinations, not string-only parsing.
 memory_partition_unit part(0,mc,&stats,&gpu);
 printf("PARALLEL_EFFECTIVE_PASS|mem_channels=%u|slices=%u|tag_lines=%u|ft=%u|detailed_dram=%u|dram_latency=%u\n",
 mc->m_n_mem,mc->m_n_mem_sub_partition,mc->m_L2_config.get_num_lines(),mc->m_L2_config.ep_l2_ft_mode(),!mc->simple_dram_model,mc->dram_latency);
 // Registered ideal values are in the native parser dump above; the real
 // constructor has enforced their guards. Do not expose private cache fields.
 part.get_sub_partition(0)->print_ep_l2_b0_snapshot(stdout,(unsigned long long)-1);
}
