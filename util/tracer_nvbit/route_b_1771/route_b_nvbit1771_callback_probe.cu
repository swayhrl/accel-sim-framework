#include <atomic>
#include <cstdio>
#include "nvbit_tool.h"
#include "nvbit.h"

static std::atomic<unsigned long long> callbacks{0};
void nvbit_at_cuda_event(CUcontext, int, nvbit_api_cuda_t, const char*, void*, CUresult*) {
  callbacks.fetch_add(1, std::memory_order_relaxed);
}
void nvbit_at_ctx_term(CUcontext) {
  std::fprintf(stdout, "ROUTEB_CALLBACK_PROBE count=%llu\n", callbacks.load());
  std::fflush(stdout);
}
