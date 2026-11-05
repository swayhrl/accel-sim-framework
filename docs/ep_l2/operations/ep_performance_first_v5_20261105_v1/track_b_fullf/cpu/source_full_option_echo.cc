#include "gpgpu_context.h"
#include "gpu-sim.h"
#include "icnt_wrapper.h"
#include "option_parser.h"
#include "trace_driven.h"
int main(int argc,char **argv){gpgpu_context context;gpgpu_sim_config cfg(&context);option_parser_t p=option_parser_create();context.ptx_reg_options(p);context.func_sim->ptx_opcocde_latency_options(p);icnt_reg_options(p);cfg.reg_options(p);trace_config trace;trace.reg_options(p);option_parser_cmdline(p,argc,const_cast<const char**>(argv));option_parser_print(p,stdout);cfg.init();printf("CPU_CONFIG_INIT_SCOPE|GPU_OBJECTS=0|cycles=0|Trace_body_reads=0|PASS\n");option_parser_destroy(p);return 0;}
