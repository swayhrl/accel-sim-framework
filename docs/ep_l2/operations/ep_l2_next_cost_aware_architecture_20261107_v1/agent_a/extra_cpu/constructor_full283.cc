
#include <cstdio>
#include <cassert>
#include "/root/data/ep_l2_full_workload_performance_20261027_v1/research/next_cost_aware_architecture_20261107_v1/agent_a/core/libcuda/gpgpu_context.h"
#include "/root/data/ep_l2_full_workload_performance_20261027_v1/research/next_cost_aware_architecture_20261107_v1/agent_a/core/src/gpgpu-sim/gpu-sim.h"
#include "/root/data/ep_l2_full_workload_performance_20261027_v1/research/next_cost_aware_architecture_20261107_v1/agent_a/core/src/gpgpu-sim/icnt_wrapper.h"
#include "/root/data/ep_l2_full_workload_performance_20261027_v1/research/next_cost_aware_architecture_20261107_v1/agent_a/core/src/gpgpu-sim/l2cache.h"
#include "/root/data/ep_l2_full_workload_performance_20261027_v1/research/next_cost_aware_architecture_20261107_v1/agent_a/core/src/gpgpu-sim/mem_latency_stat.h"
#include "/root/data/ep_l2_full_workload_performance_20261027_v1/research/next_cost_aware_architecture_20261107_v1/agent_a/core/src/option_parser.h"
#include "/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/framework/gpu-simulator/trace-driven/trace_driven.h"
int main(int argc,char**argv) {
 assert(argc==3);gpgpu_context context;gpgpu_sim_config cfg(&context);
 option_parser_t p=option_parser_create();context.ptx_reg_options(p);
 context.func_sim->ptx_opcocde_latency_options(p);icnt_reg_options(p);cfg.reg_options(p);
 trace_config trace_options;trace_options.reg_options(p);
 option_parser_cfgfile(p,argv[1]);option_parser_cfgfile(p,argv[2]);
 option_parser_print(p,stdout);cfg.init();option_parser_destroy(p);
 exec_gpgpu_sim gpu(cfg,&context);const auto mc=gpu.getMemoryConfig();
 memory_stats_t stats(cfg.num_shader(),gpu.getShaderCoreConfig(),mc,&gpu);
 memory_partition_unit part(0,mc,&stats,&gpu);
 printf("OPTIONAL128_CONSTRUCTOR_PASS|mode=%u|cycles=%llu|applications_started=0\n",
      mc->m_L2_config.optional_segment_mode(),gpu.gpu_sim_cycle);
 assert(gpu.gpu_sim_cycle==0);
}
