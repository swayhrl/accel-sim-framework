// Actual Core + Framework option registration only. No cfg.init(), GPU object,
// trace parser instance/file open, kernel, cycle(), or simulation thread.
#include "gpgpu_context.h"
#include "gpgpu-sim/gpu-sim.h"
#include "gpgpu-sim/icnt_wrapper.h"
#include "option_parser.h"
#include "trace_driven.h"
#include <cassert>
#include <cstdio>
#include <dlfcn.h>

int main(int argc,const char **argv) {
  gpgpu_context ctx;
  gpgpu_sim_config cfg(&ctx);
  trace_config traces;
  auto parser=option_parser_create();
  ctx.ptx_reg_options(parser);
  ctx.func_sim->ptx_opcocde_latency_options(parser);
  icnt_reg_options(parser);
  cfg.reg_options(parser);
  traces.reg_options(parser);
  option_parser_cmdline(parser,argc,argv);
  option_parser_print(parser,stdout);
  Dl_info library{};
  auto symbol=dlsym(RTLD_DEFAULT,"_ZN9ldst_unit5cycleEv");
  assert(symbol && dladdr(symbol,&library));
  std::printf("AG_CPU_OPTIONS_LIBRARY %s\n",library.dli_fname);
  std::puts("AG_CPU_OPTIONS_RESULT actual_production_registration=1 kernels=0 GPU_cycle_calls=0 simulation_threads_started=0 trace_files_opened=0");
}
