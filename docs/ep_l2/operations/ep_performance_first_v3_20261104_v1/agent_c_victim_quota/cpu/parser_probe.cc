#include <cstdio>
#include "/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v2_20261103_v1/agent_a/core_candidate/tests/ep_l2/potential_fixture.h"
#include "/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/framework/gpu-simulator/trace-driven/trace_driven.h"
int main(int argc,char **argv){gpgpu_context ctx;gpgpu_sim_config cfg(&ctx);trace_config tr;option_parser_t p=option_parser_create();ctx.ptx_reg_options(p);ctx.func_sim->ptx_opcocde_latency_options(p);icnt_reg_options(p);cfg.reg_options(p);tr.reg_options(p);for(int i=1;i<argc;++i)option_parser_cfgfile(p,argv[i]);option_parser_print(p,stdout);option_parser_destroy(p);return 0;}
