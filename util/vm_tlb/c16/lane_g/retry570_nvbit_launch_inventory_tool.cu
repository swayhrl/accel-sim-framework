// Diagnostic-only direct NVBit launch inventory.  It emits no instruction
// map, inserts no callbacks, and makes no target selection by kernel name.

#include <atomic>
#include <cstdio>
#include <cstdlib>

#include "nvbit.h"
#include "nvbit_tool.h"

static FILE* output = nullptr;
static std::atomic<unsigned long long> ordinal{0};

static bool launch_function(nvbit_api_cuda_t callback, void* parameters, CUfunction* function,
                            unsigned* gx, unsigned* gy, unsigned* gz, unsigned* bx, unsigned* by, unsigned* bz) {
    if (callback == API_CUDA_cuLaunchKernel || callback == API_CUDA_cuLaunchKernel_ptsz
        || callback == API_CUDA_cuLaunchCooperativeKernel
        || callback == API_CUDA_cuLaunchCooperativeKernel_ptsz) {
        auto* value = static_cast<cuLaunchKernel_params*>(parameters);
        *function = value->f; *gx = value->gridDimX; *gy = value->gridDimY; *gz = value->gridDimZ;
        *bx = value->blockDimX; *by = value->blockDimY; *bz = value->blockDimZ;
        return true;
    }
    if (callback == API_CUDA_cuLaunch || callback == API_CUDA_cuLaunchGrid) {
        *function = static_cast<cuLaunch_params*>(parameters)->f;
        *gx = *gy = *gz = *bx = *by = *bz = 0;
        return true;
    }
    if (callback == API_CUDA_cuLaunchKernelEx || callback == API_CUDA_cuLaunchKernelEx_ptsz) {
        auto* value = static_cast<cuLaunchKernelEx_params*>(parameters);
        *function = value->f; *gx = *gy = *gz = *bx = *by = *bz = 0;
        return true;
    }
    return false;
}

void nvbit_at_init() {
    const char* path = getenv("C16_NVBIT_LAUNCH_INVENTORY_PATH");
    if (path == nullptr || path[0] == '\0') {
        std::fprintf(stderr, "C16_LAUNCH_INVENTORY_CONFIG_ERROR missing output path\n");
        std::abort();
    }
    output = std::fopen(path, "wx");
    if (output == nullptr) {
        std::fprintf(stderr, "C16_LAUNCH_INVENTORY_CONFIG_ERROR cannot create output\n");
        std::abort();
    }
    std::fprintf(output, "global_launch_ordinal\tfunction_full_name\tfunction_mangled_name\tfunction_address\tgrid\tblock\n");
    std::fflush(output);
}

void nvbit_at_cuda_event(CUcontext context, int is_exit, nvbit_api_cuda_t callback, const char*, void* parameters, CUresult*) {
    if (is_exit || output == nullptr) return;
    CUfunction function = nullptr; unsigned gx, gy, gz, bx, by, bz;
    if (!launch_function(callback, parameters, &function, &gx, &gy, &gz, &bx, &by, &bz) || function == nullptr) return;
    const unsigned long long index = ordinal.fetch_add(1, std::memory_order_relaxed) + 1;
    const char* full = nvbit_get_func_name(context, function);
    const char* mangled = nvbit_get_func_name(context, function, true);
    std::fprintf(output, "%llu\t%s\t%s\t0x%llx\t%ux%ux%u\t%ux%ux%u\n", index,
                 full ? full : "", mangled ? mangled : "",
                 static_cast<unsigned long long>(nvbit_get_func_addr(context, function)), gx, gy, gz, bx, by, bz);
    std::fflush(output);
}

void nvbit_at_term() {
    if (output != nullptr) { std::fclose(output); output = nullptr; }
}
