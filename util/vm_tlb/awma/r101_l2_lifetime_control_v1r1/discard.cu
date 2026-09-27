#include <cuda_runtime.h>
#include <cstdint>
#include <cstdio>

// Exactly one destructive 128-byte L2 hint per aligned logical cache line.
// A caller must prove the whole range is dead before calling this function.
__global__ void r101r1_discard_lines(unsigned char* base, unsigned long long lines) {
    const unsigned long long index =
        static_cast<unsigned long long>(blockIdx.x) * blockDim.x + threadIdx.x;
    if (index < lines) {
        unsigned long long ptr = reinterpret_cast<unsigned long long>(base + index * 128ULL);
        asm volatile("discard.global.L2 [%0], 128;" :: "l"(ptr) : "memory");
    }
}

extern "C" int r101r1_discard(void* base, unsigned long long bytes,
                                unsigned long long stream_value) {
    if (!base || bytes == 0 || bytes % 128ULL != 0 ||
        reinterpret_cast<std::uintptr_t>(base) % 128U != 0) {
        return -1;
    }
    const unsigned long long lines = bytes / 128ULL;
    const unsigned long long blocks = (lines + 255ULL) / 256ULL;
    if (blocks > 2147483647ULL) return -2;
    cudaStream_t stream = reinterpret_cast<cudaStream_t>(stream_value);
    r101r1_discard_lines<<<static_cast<unsigned int>(blocks), 256, 0, stream>>>(
        reinterpret_cast<unsigned char*>(base), lines);
    return static_cast<int>(cudaGetLastError());
}

#ifdef R101R1_CAPABILITY_MAIN
int main() {
    cudaDeviceProp prop{};
    int runtime_version = 0, driver_version = 0;
    const cudaError_t device_status = cudaSetDevice(0);
    const cudaError_t prop_status = cudaGetDeviceProperties(&prop, 0);
    const cudaError_t runtime_status = cudaRuntimeGetVersion(&runtime_version);
    const cudaError_t driver_status = cudaDriverGetVersion(&driver_version);
    std::size_t persisting_limit = 0;
    const cudaError_t limit_status = cudaDeviceGetLimit(
        &persisting_limit, cudaLimitPersistingL2CacheSize);
    void* ptr = nullptr;
    const cudaError_t alloc_status = cudaMalloc(&ptr, 128);
    cudaError_t memset_status = cudaSuccess;
    int discard_status = -3;
    cudaError_t sync_status = cudaSuccess;
    if (alloc_status == cudaSuccess) {
        memset_status = cudaMemset(ptr, 0x5a, 128);
        if (memset_status == cudaSuccess) {
            discard_status = r101r1_discard(ptr, 128, 0);
            sync_status = cudaDeviceSynchronize();
        }
        cudaFree(ptr);
    }
    std::printf(
        "{\"device_name\":\"%s\",\"sm_major\":%d,\"sm_minor\":%d,"
        "\"l2_cache_bytes\":%d,\"persisting_l2_max_bytes\":%zu,"
        "\"access_policy_max_window_bytes\":%zu,\"persisting_limit_bytes\":%zu,"
        "\"runtime_version\":%d,\"driver_version\":%d,"
        "\"status_device\":%d,\"status_prop\":%d,\"status_runtime\":%d,"
        "\"status_driver\":%d,\"status_limit\":%d,\"status_alloc\":%d,"
        "\"status_memset\":%d,\"status_discard\":%d,\"status_sync\":%d}\n",
        prop.name, prop.major, prop.minor, prop.l2CacheSize,
        static_cast<std::size_t>(prop.persistingL2CacheMaxSize),
        static_cast<std::size_t>(prop.accessPolicyMaxWindowSize),
        persisting_limit, runtime_version, driver_version,
        static_cast<int>(device_status), static_cast<int>(prop_status),
        static_cast<int>(runtime_status), static_cast<int>(driver_status),
        static_cast<int>(limit_status), static_cast<int>(alloc_status),
        static_cast<int>(memset_status), discard_status, static_cast<int>(sync_status));
    return device_status == cudaSuccess && prop_status == cudaSuccess &&
                   alloc_status == cudaSuccess && memset_status == cudaSuccess &&
                   discard_status == 0 && sync_status == cudaSuccess
               ? 0
               : 1;
}
#endif
