#include "gpgpu_context.h"
#include "gpu-sim.h"
#include "icnt_wrapper.h"
#include "option_parser.h"
#include <cassert>
#include "trace_driven.h"
int main(int argc,char**argv){gpgpu_context c;gpgpu_sim_config cfg(&c);option_parser_t p=option_parser_create();c.ptx_reg_options(p);c.func_sim->ptx_opcocde_latency_options(p);icnt_reg_options(p);cfg.reg_options(p);trace_config trace;trace.reg_options(p);option_parser_cmdline(p,argc,const_cast<const char**>(argv));option_parser_print(p,stdout);option_parser_destroy(p);return 0;}
