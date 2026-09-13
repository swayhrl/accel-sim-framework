// Callback-census-only NVBit tool for bounded Retry570 diagnostics.
//
// This tool intentionally observes every CUDA driver callback but does no
// NVBit introspection or instrumentation.  It is therefore suitable for
// separating an application operation boundary from NVBit callback arrival.

#include <atomic>
#include <cstdio>
#include <cstdint>
#include <time.h>
#include <unistd.h>
#include <sys/syscall.h>

#include "nvbit.h"
#include "nvbit_tool.h"

static std::atomic<unsigned long long> callback_sequence{0};

static uint64_t monotonic_ns() {
    struct timespec value;
    clock_gettime(CLOCK_MONOTONIC, &value);
    return static_cast<uint64_t>(value.tv_sec) * 1000000000ULL + value.tv_nsec;
}

static long current_tid() {
    return static_cast<long>(syscall(SYS_gettid));
}

void nvbit_at_init() {
    std::printf("C16_CALLBACK_CENSUS_TOOL_READY mode=CALLBACK_CENSUS_ONLY introspection=0 instrumentation=0 trace=0\n");
    std::fflush(stdout);
}

void nvbit_at_cuda_event(CUcontext, int is_exit, nvbit_api_cuda_t cbid,
                         const char* event_name, void*, CUresult*) {
    const unsigned long long sequence = callback_sequence.fetch_add(1, std::memory_order_relaxed) + 1;
    std::printf("C16_CALLBACK_CENSUS ts_ns=%llu seq=%llu pid=%ld tid=%ld is_exit=%d cbid=%u callback=%s\n",
                static_cast<unsigned long long>(monotonic_ns()), sequence,
                static_cast<long>(getpid()), current_tid(), is_exit,
                static_cast<unsigned int>(cbid), event_name == nullptr ? "UNKNOWN" : event_name);
    std::fflush(stdout);
}

void nvbit_at_term() {
    std::printf("C16_CALLBACK_CENSUS_TOOL_TERMINAL callback_count=%llu\n",
                callback_sequence.load(std::memory_order_relaxed));
    std::fflush(stdout);
}
