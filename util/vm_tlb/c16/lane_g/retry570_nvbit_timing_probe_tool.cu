// Diagnostic-only NVBit 1.8 timing probe for PyTorch first-kernel staging.
// It instruments exactly one instruction per newly seen related function with
// a no-op device callback.  It emits host-side stage timestamps; it produces
// no trace, address records, model result, or C target outcome.

#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <time.h>

#include <string>
#include <unordered_set>
#include <vector>

#include "nvbit.h"
#include "nvbit_tool.h"
#include "utils/utils.h"

extern "C" __device__ void c16_timing_probe_noop();

static pthread_mutex_t timing_mutex;
static std::unordered_set<CUfunction> seen_functions;
static uint64_t launch_number = 0;

static uint64_t monotonic_us() {
    struct timespec value;
    clock_gettime(CLOCK_MONOTONIC, &value);
    return static_cast<uint64_t>(value.tv_sec) * 1000000ULL + value.tv_nsec / 1000ULL;
}

static const char* function_name(CUcontext context, CUfunction function) {
    const char* value = nvbit_get_func_name(context, function, true);
    return value == nullptr ? "UNKNOWN" : value;
}

static void event(const char* stage, CUcontext context, CUfunction function, long related_count, long static_count) {
    printf("C16_NVBIT_TIMING ts_us=%llu stage=%s launch=%llu function=%s related_count=%ld static_instruction_count=%ld\n",
           static_cast<unsigned long long>(monotonic_us()), stage,
           static_cast<unsigned long long>(launch_number),
           function == nullptr ? "NA" : function_name(context, function), related_count, static_count);
    fflush(stdout);
}

static bool launch_function(nvbit_api_cuda_t callback, void* parameters, CUfunction* function) {
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

static void instrument_related(CUcontext context, CUfunction kernel) {
    event("RELATED_FUNCTIONS_BEGIN", context, kernel, -1, -1);
    std::vector<CUfunction> related = nvbit_get_related_functions(context, kernel);
    related.push_back(kernel);
    event("RELATED_FUNCTIONS_END", context, kernel, static_cast<long>(related.size()), -1);
    for (CUfunction function : related) {
        if (!seen_functions.insert(function).second) continue;
        event("GET_INSTRS_BEGIN", context, function, static_cast<long>(related.size()), -1);
        const std::vector<Instr*>& instructions = nvbit_get_instrs(context, function);
        const long count = static_cast<long>(instructions.size());
        event("GET_INSTRS_END", context, function, static_cast<long>(related.size()), count);
        if (instructions.empty()) continue;
        event("INSERTION_BEGIN", context, function, static_cast<long>(related.size()), count);
        nvbit_insert_call(instructions.front(), "c16_timing_probe_noop", IPOINT_BEFORE);
        event("INSERTION_END", context, function, static_cast<long>(related.size()), count);
    }
}

void nvbit_at_init() {
    pthread_mutex_init(&timing_mutex, nullptr);
    printf("C16_NVBIT_TIMING_TOOL_READY diagnostic_only=1 no_trace=1 one_instruction_per_function=1\n");
    fflush(stdout);
}

void nvbit_at_cuda_event(CUcontext context, int is_exit, nvbit_api_cuda_t callback,
                         const char*, void* parameters, CUresult*) {
    CUfunction function = nullptr;
    if (!launch_function(callback, parameters, &function) || function == nullptr) return;
    if (!is_exit) {
        event("LAUNCH_CALLBACK_ENTER", context, function, -1, -1);
        pthread_mutex_lock(&timing_mutex);
        event("MUTEX_ACQUIRED", context, function, -1, -1);
        instrument_related(context, function);
        event("ENABLE_INSTRUMENTED_BEGIN", context, function, -1, -1);
        nvbit_enable_instrumented(context, function, true);
        event("ENABLE_INSTRUMENTED_END", context, function, -1, -1);
        event("KERNEL_LAUNCH_RETURN", context, function, -1, -1);
    } else {
        event("LAUNCH_CALLBACK_EXIT", context, function, -1, -1);
        event("CUDA_SYNCHRONIZE_BEGIN", context, function, -1, -1);
        CUDA_SAFECALL(cudaDeviceSynchronize());
        event("CUDA_SYNCHRONIZE_END", context, function, -1, -1);
        ++launch_number;
        pthread_mutex_unlock(&timing_mutex);
        event("MUTEX_RELEASED", context, function, -1, -1);
    }
}

void nvbit_at_term() {
    printf("C16_NVBIT_TIMING_TERMINAL launch_count=%llu instrumented_function_count=%zu\n",
           static_cast<unsigned long long>(launch_number), seen_functions.size());
    fflush(stdout);
}
