// C16 U8 no-match/no-trace NVBit 1.7.5 prewarm tool for the RTX4080 platform.
#include <cstdio>

#include "nvbit.h"
#include "nvbit_tool.h"

void nvbit_at_init() {
  std::printf("C16_NVBIT175_NO_MATCH_READY no_instrumentation=1 no_trace_output=1\n");
  std::fflush(stdout);
}

void nvbit_at_ctx_init(CUcontext ctx) {
  // Link and exercise a non-instrumenting NVBit API without inspecting functions.
  (void)nvbit_get_sm_family(ctx);
}

void nvbit_at_cuda_event(CUcontext, int, nvbit_api_cuda_t, const char*, void*, CUresult*) {
  // Deliberately no function matching, instruction enumeration, or instrumentation.
}

void nvbit_at_term() {
  std::printf("C16_NVBIT175_NO_MATCH_TERMINAL\n");
  std::fflush(stdout);
}
