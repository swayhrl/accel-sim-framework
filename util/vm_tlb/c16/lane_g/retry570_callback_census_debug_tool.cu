// Debug-symbol-equivalent callback census.  This preserves the census tool's
// callback behaviour while declaring NVBit core's external bookkeeping map so
// gdb can inspect its true type without an in-callback lookup or mutation.

#include <atomic>
#include <cstdio>
#include <cstdint>
#include <string>
#include <time.h>
#include <unordered_map>
#include <unistd.h>
#include <sys/syscall.h>
#include <vector>

#include "nvbit.h"
#include "nvbit_tool.h"

using NvbitLinkAnchor = const char* (*)(CUcontext, CUfunction, bool);
__attribute__((used)) static NvbitLinkAnchor const c16_nvbit_link_anchor = &nvbit_get_func_name;

// This map is defined by NVBit's precompiled core (its archive retains the
// string ``nvbit.cpp`` but no DWARF source lines).  The declaration exists
// only for debug type information; this tool neither reads nor writes it.
class Function;
using NvbitElfModuleMap = std::unordered_map<std::string, std::vector<Function*>>;
extern NvbitElfModuleMap elfModuleHashMap;
__attribute__((used)) static NvbitElfModuleMap* const c16_debug_elf_module_map = &elfModuleHashMap;

static std::atomic<unsigned long long> callback_sequence{0};

static uint64_t monotonic_ns() {
    struct timespec value;
    clock_gettime(CLOCK_MONOTONIC, &value);
    return static_cast<uint64_t>(value.tv_sec) * 1000000000ULL + value.tv_nsec;
}

void nvbit_at_init() {
    std::printf("C16_CALLBACK_CENSUS_TOOL_READY mode=CALLBACK_CENSUS_ONLY_DEBUG introspection=0 instrumentation=0 trace=0 debug_symbols=1\n");
    std::fflush(stdout);
}

void nvbit_at_cuda_event(CUcontext, int is_exit, nvbit_api_cuda_t cbid,
                         const char* event_name, void*, CUresult*) {
    const unsigned long long sequence = callback_sequence.fetch_add(1, std::memory_order_relaxed) + 1;
    std::printf("C16_CALLBACK_CENSUS ts_ns=%llu seq=%llu pid=%ld tid=%ld is_exit=%d cbid=%u callback=%s\n",
                static_cast<unsigned long long>(monotonic_ns()), sequence,
                static_cast<long>(getpid()), static_cast<long>(syscall(SYS_gettid)), is_exit,
                static_cast<unsigned int>(cbid), event_name == nullptr ? "UNKNOWN" : event_name);
    std::fflush(stdout);
}

void nvbit_at_term() {
    std::printf("C16_CALLBACK_CENSUS_TOOL_TERMINAL callback_count=%llu\n", callback_sequence.load(std::memory_order_relaxed));
    std::fflush(stdout);
}
