// Calls the actual published shader_core_config option registration and parser.
// Never initializes a GPU, launches a thread, loads a kernel, or calls cycle().
#include "gpgpu-sim/shader.h"
#include "gpgpu-sim/gpu-sim.h"
#include "gpgpu_context.h"
#include "option_parser.h"
#include <cstdio>
int main(int argc, const char **argv) {
  gpgpu_context ctx;
  gpgpu_sim_config config(&ctx);
  option_parser_t parser = option_parser_create();
  config.reg_options(parser);
  option_parser_cmdline(parser, argc, argv);
  option_parser_print(parser, stdout);
  printf("LANE_Y_OPTIONS_ONLY flush_l1=%u\n", unsigned(config.flush_l1()));
  option_parser_destroy(parser);
  return 0;
}
