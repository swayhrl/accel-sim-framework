// CPU-buildable, GPU-executed-only-by-Lane-A Route-B Q1 fixture.
//
// The extern "C" entry point is deliberately an exact, stable identity for
// the NVBit static-map and Route-B whitelist binding.  It has a direct GLOBAL
// load and store and executes only lanes selected by a nontrivial predicate.
#include <cuda_runtime.h>

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <dlfcn.h>
#include <vector>

extern "C" __global__ void c16_route_b_q1_global_ldst_predicate(
    const uint32_t* source, uint32_t* destination, uint32_t element_count) {
    const uint32_t index = blockIdx.x * blockDim.x + threadIdx.x;
    // A non-contiguous guard makes the executing mask distinct from active.
    if (index < element_count && (threadIdx.x % 3U) != 1U) {
        const uint32_t value = source[index];       // direct GLOBAL load
        destination[index] = value ^ 0x9e3779b9U;   // direct GLOBAL store
    }
}

static void write_exact_owner_receipt() {
    const char* output = getenv("C16_ROUTE_B_Q1_OWNER_RECEIPT_PATH");
    if (output == nullptr || output[0] == '\0') return;
    Dl_info info{};
    if (dladdr(reinterpret_cast<const void*>(&c16_route_b_q1_global_ldst_predicate), &info) == 0 ||
        info.dli_fname == nullptr || info.dli_fname[0] == '\0') {
        std::fprintf(stderr, "C16_ROUTE_B_Q1_OWNER_RECEIPT_FAIL dladdr\n"); std::exit(2);
    }
    FILE* file = std::fopen(output, "w");
    if (file == nullptr) { std::fprintf(stderr, "C16_ROUTE_B_Q1_OWNER_RECEIPT_FAIL open\n"); std::exit(2); }
    std::fprintf(file, "c16_route_b_q1_global_ldst_predicate\t%s\n", info.dli_fname);
    std::fclose(file);
}

static uint64_t checksum(const std::vector<uint32_t>& values) {
    uint64_t result = 0;
    for (uint32_t value : values) result = (result * 0x100000001b3ULL) ^ value;
    return result;
}

int main() {
    write_exact_owner_receipt();
    constexpr uint32_t count = 257;
    constexpr uint32_t block = 64;
    std::vector<uint32_t> input(count), output(count, 0);
    for (uint32_t index = 0; index < count; ++index) input[index] = index * 17U + 3U;
    uint32_t *device_input = nullptr, *device_output = nullptr;
    if (cudaMalloc(&device_input, count * sizeof(uint32_t)) != cudaSuccess ||
        cudaMalloc(&device_output, count * sizeof(uint32_t)) != cudaSuccess ||
        cudaMemcpy(device_input, input.data(), count * sizeof(uint32_t), cudaMemcpyHostToDevice) != cudaSuccess ||
        cudaMemset(device_output, 0, count * sizeof(uint32_t)) != cudaSuccess) return 2;
    // Q1 requires two launches of this same exact function.
    c16_route_b_q1_global_ldst_predicate<<<(count + block - 1) / block, block>>>(device_input, device_output, count);
    c16_route_b_q1_global_ldst_predicate<<<(count + block - 1) / block, block>>>(device_input, device_output, count);
    if (cudaGetLastError() != cudaSuccess || cudaDeviceSynchronize() != cudaSuccess ||
        cudaMemcpy(output.data(), device_output, count * sizeof(uint32_t), cudaMemcpyDeviceToHost) != cudaSuccess) return 3;
    cudaFree(device_input); cudaFree(device_output);
    constexpr uint64_t expected_checksum = 0x044a6de6746b6ab2ULL;
    const uint64_t actual_checksum = checksum(output);
    std::printf("C16_ROUTE_B_Q1_FIXTURE_CHECKSUM=%016llx expected=%016llx\n",
                static_cast<unsigned long long>(actual_checksum), static_cast<unsigned long long>(expected_checksum));
    return actual_checksum == expected_checksum ? 0 : 4;
}
