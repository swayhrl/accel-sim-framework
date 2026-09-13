// Diagnostic-only exact-target NVBit discovery probe for Retry570.
//
// This observes precisely one full-mangled indexSelectLargeIndex launch and
// enumerates its related/root function set. It never inserts a callback,
// enables instrumentation, allocates CUDA memory, emits a trace, or changes a
// kernel. Every slow-stage boundary is printed and flushed so a bounded parent
// can determine the last entered function even when it must terminate us.

#include <atomic>
#include <cctype>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <pthread.h>
#include <stdint.h>
#include <time.h>

#include <string>
#include <unordered_set>
#include <vector>

#include "nvbit.h"
#include "nvbit_tool.h"

static pthread_mutex_t discovery_mutex;
static std::string exact_target_mangled;
static std::string focus_function_mangled;
static std::atomic<bool> discovery_complete{false};
static std::atomic<unsigned long long> target_launches{0};

static uint64_t monotonic_us() {
    struct timespec value;
    clock_gettime(CLOCK_MONOTONIC, &value);
    return static_cast<uint64_t>(value.tv_sec) * 1000000ULL + value.tv_nsec / 1000ULL;
}

static unsigned long long function_handle(CUfunction function) {
    return static_cast<unsigned long long>(reinterpret_cast<uintptr_t>(function));
}

static const char* mangled_name(CUcontext context, CUfunction function) {
    const char* name = nvbit_get_func_name(context, function, true);
    return name == nullptr ? "UNKNOWN" : name;
}

static void event(const char* stage, CUcontext context, CUfunction function,
                  long index, long related_count, long unique_handles,
                  long unique_names, long instruction_count,
                  uint64_t cumulative_us, uint64_t elapsed_us) {
    printf("C16_EXACT_DISCOVERY ts_us=%llu stage=%s launch=%llu function_mangled=%s function_handle=0x%llx index=%ld related_function_count=%ld unique_handle_count=%ld unique_name_count=%ld static_instruction_count=%ld cumulative_us=%llu elapsed_us=%llu\n",
           static_cast<unsigned long long>(monotonic_us()), stage,
           target_launches.load(std::memory_order_relaxed),
           function == nullptr ? "NA" : mangled_name(context, function),
           function == nullptr ? 0ULL : function_handle(function), index,
           related_count, unique_handles, unique_names, instruction_count,
           static_cast<unsigned long long>(cumulative_us),
           static_cast<unsigned long long>(elapsed_us));
    fflush(stdout);
}

static bool extract_launch_function(nvbit_api_cuda_t callback, void* parameters, CUfunction* function) {
    switch (callback) {
        case API_CUDA_cuLaunch:
        case API_CUDA_cuLaunchGrid:
            *function = static_cast<cuLaunch_params*>(parameters)->f;
            return true;
        case API_CUDA_cuLaunchKernel_ptsz:
        case API_CUDA_cuLaunchKernel:
        case API_CUDA_cuLaunchCooperativeKernel:
        case API_CUDA_cuLaunchCooperativeKernel_ptsz:
            *function = static_cast<cuLaunchKernel_params*>(parameters)->f;
            return true;
        case API_CUDA_cuLaunchKernelEx:
        case API_CUDA_cuLaunchKernelEx_ptsz:
            *function = static_cast<cuLaunchKernelEx_params*>(parameters)->f;
            return true;
        default:
            return false;
    }
}

static void require_environment() {
    const char* target = getenv("C16_NVBIT_TARGET_FUNCTION_MANGLED");
    if (target == nullptr || target[0] == '\0') {
        fprintf(stderr, "C16_EXACT_DISCOVERY_CONFIG_ERROR missing exact target mangled name\n");
        abort();
    }
    exact_target_mangled = target;
    const char* focus = getenv("C16_NVBIT_DISCOVERY_FOCUS_FUNCTION_MANGLED");
    if (focus != nullptr && focus[0] != '\0') focus_function_mangled = focus;
}

static void discover(CUcontext context, CUfunction kernel) {
    const uint64_t total_begin = monotonic_us();
    event("RELATED_FUNCTIONS_BEGIN", context, kernel, -1, -1, -1, -1, -1, 0, 0);
    std::vector<CUfunction> functions = nvbit_get_related_functions(context, kernel);
    const long related_count = static_cast<long>(functions.size());
    bool root_present = false;
    for (CUfunction candidate : functions) {
        if (candidate == kernel) root_present = true;
    }
    if (!root_present) functions.push_back(kernel);
    const uint64_t related_elapsed = monotonic_us() - total_begin;
    event("RELATED_FUNCTIONS_END", context, kernel, -1, related_count, -1, -1, -1, 0, related_elapsed);

    std::unordered_set<CUfunction> seen_handles;
    std::unordered_set<std::string> seen_names;
    uint64_t cumulative_us = 0;
    long get_instrs_calls = 0;
    long duplicate_entries = 0;
    long skipped_by_focus = 0;
    long total_static_instructions = 0;
    for (size_t position = 0; position < functions.size(); ++position) {
        CUfunction function = functions[position];
        const std::string observed_mangled = mangled_name(context, function);
        const bool new_handle = seen_handles.insert(function).second;
        const bool new_name = seen_names.insert(observed_mangled).second;
        if (!new_handle) {
            ++duplicate_entries;
            event("FUNCTION_DUPLICATE_SKIPPED", context, function, static_cast<long>(position), related_count,
                  static_cast<long>(seen_handles.size()), static_cast<long>(seen_names.size()), -1,
                  cumulative_us, 0);
            continue;
        }
        if (!focus_function_mangled.empty() && observed_mangled != focus_function_mangled) {
            ++skipped_by_focus;
            event("FUNCTION_FOCUS_NOT_SELECTED", context, function, static_cast<long>(position), related_count,
                  static_cast<long>(seen_handles.size()), static_cast<long>(seen_names.size()), -1,
                  cumulative_us, 0);
            continue;
        }
        event("FUNCTION_BEGIN", context, function, static_cast<long>(position), related_count,
              static_cast<long>(seen_handles.size()), static_cast<long>(seen_names.size()), -1,
              cumulative_us, 0);
        const uint64_t function_begin = monotonic_us();
        const std::vector<Instr*>& instructions = nvbit_get_instrs(context, function);
        const uint64_t elapsed = monotonic_us() - function_begin;
        cumulative_us += elapsed;
        ++get_instrs_calls;
        total_static_instructions += static_cast<long>(instructions.size());
        event("FUNCTION_END", context, function, static_cast<long>(position), related_count,
              static_cast<long>(seen_handles.size()), static_cast<long>(seen_names.size()),
              static_cast<long>(instructions.size()), cumulative_us, elapsed);
        (void)new_name;
    }
    event("DISCOVERY_COMPLETE", context, kernel, -1, related_count,
          static_cast<long>(seen_handles.size()), static_cast<long>(seen_names.size()),
          total_static_instructions, cumulative_us, monotonic_us() - total_begin);
    printf("C16_EXACT_DISCOVERY_SUMMARY launch=%llu related_function_count=%ld enumeration_entry_count=%zu unique_handle_count=%zu unique_name_count=%zu get_instrs_call_count=%ld duplicate_entries_skipped=%ld skipped_by_focus=%ld total_static_instruction_count=%ld cumulative_get_instrs_us=%llu\n",
           target_launches.load(std::memory_order_relaxed), related_count, functions.size(), seen_handles.size(),
           seen_names.size(), get_instrs_calls, duplicate_entries, skipped_by_focus,
           total_static_instructions, static_cast<unsigned long long>(cumulative_us));
    fflush(stdout);
}

void nvbit_at_init() {
    require_environment();
    pthread_mutex_init(&discovery_mutex, nullptr);
    printf("C16_EXACT_DISCOVERY_TOOL_READY diagnostic_discovery_only=1 insertion=0 enable_instrumented=0 trace=0 exact_target=%s focus_function=%s\n",
           exact_target_mangled.c_str(), focus_function_mangled.empty() ? "NONE" : focus_function_mangled.c_str());
    fflush(stdout);
}

void nvbit_at_cuda_event(CUcontext context, int is_exit, nvbit_api_cuda_t callback,
                         const char*, void* parameters, CUresult*) {
    if (is_exit) return;
    CUfunction function = nullptr;
    if (!extract_launch_function(callback, parameters, &function) || function == nullptr) return;
    if (exact_target_mangled != std::string(mangled_name(context, function))) return;
    const unsigned long long launch = target_launches.fetch_add(1, std::memory_order_relaxed);
    if (discovery_complete.load(std::memory_order_acquire)) {
        event("TARGET_REUSE_CALLBACK", context, function, static_cast<long>(launch), -1, -1, -1, -1, 0, 0);
        return;
    }
    event("TARGET_CALLBACK_ENTER", context, function, static_cast<long>(launch), -1, -1, -1, -1, 0, 0);
    pthread_mutex_lock(&discovery_mutex);
    if (!discovery_complete.load(std::memory_order_relaxed)) {
        discover(context, function);
        discovery_complete.store(true, std::memory_order_release);
    }
    pthread_mutex_unlock(&discovery_mutex);
}

void nvbit_at_term() {
    printf("C16_EXACT_DISCOVERY_TERMINAL target_launch_count=%llu discovery_complete=%d\n",
           target_launches.load(std::memory_order_relaxed),
           discovery_complete.load(std::memory_order_acquire) ? 1 : 0);
    fflush(stdout);
}
