#include <cuda_runtime.h>

#include <cstdint>
#include <cstdio>
#include <vector>

namespace {

constexpr std::size_t kElements = 1U << 20;

__global__ void c16_vector_add_kernel(const std::uint32_t* a,
                                      const std::uint32_t* b,
                                      std::uint32_t* c,
                                      std::size_t count) {
  const std::size_t index = static_cast<std::size_t>(blockIdx.x) * blockDim.x + threadIdx.x;
  if (index < count) c[index] = a[index] + b[index];
}

bool check(cudaError_t status, const char* expression) {
  if (status == cudaSuccess) return true;
  std::fprintf(stderr, "CUDA_FAILURE expression=%s error=%s\n", expression,
               cudaGetErrorString(status));
  return false;
}

}  // namespace

int main() {
  std::vector<std::uint32_t> a(kElements);
  std::vector<std::uint32_t> b(kElements);
  std::vector<std::uint32_t> c(kElements, 0);
  for (std::size_t i = 0; i < kElements; ++i) {
    a[i] = static_cast<std::uint32_t>(i * 17U + 3U);
    b[i] = static_cast<std::uint32_t>(i * 29U + 11U);
  }

  std::uint32_t *device_a = nullptr, *device_b = nullptr, *device_c = nullptr;
  if (!check(cudaMalloc(&device_a, kElements * sizeof(*device_a)), "cudaMalloc(device_a)") ||
      !check(cudaMalloc(&device_b, kElements * sizeof(*device_b)), "cudaMalloc(device_b)") ||
      !check(cudaMalloc(&device_c, kElements * sizeof(*device_c)), "cudaMalloc(device_c)")) {
    cudaFree(device_a);
    cudaFree(device_b);
    cudaFree(device_c);
    return 2;
  }
  if (!check(cudaMemcpy(device_a, a.data(), kElements * sizeof(*device_a), cudaMemcpyHostToDevice),
             "cudaMemcpy(a)") ||
      !check(cudaMemcpy(device_b, b.data(), kElements * sizeof(*device_b), cudaMemcpyHostToDevice),
             "cudaMemcpy(b)")) {
    cudaFree(device_a);
    cudaFree(device_b);
    cudaFree(device_c);
    return 2;
  }

  constexpr unsigned int kThreads = 256;
  const unsigned int blocks = static_cast<unsigned int>((kElements + kThreads - 1) / kThreads);
  c16_vector_add_kernel<<<blocks, kThreads>>>(device_a, device_b, device_c, kElements);
  if (!check(cudaGetLastError(), "c16_vector_add_kernel launch") ||
      !check(cudaDeviceSynchronize(), "cudaDeviceSynchronize") ||
      !check(cudaMemcpy(c.data(), device_c, kElements * sizeof(*device_c), cudaMemcpyDeviceToHost),
             "cudaMemcpy(c)")) {
    cudaFree(device_a);
    cudaFree(device_b);
    cudaFree(device_c);
    return 2;
  }

  std::uint64_t checksum = 0;
  for (std::size_t i = 0; i < kElements; ++i) {
    const std::uint32_t expected = a[i] + b[i];
    if (c[i] != expected) {
      std::fprintf(stderr, "RESULT_MISMATCH index=%zu got=%u expected=%u\n", i, c[i], expected);
      cudaFree(device_a);
      cudaFree(device_b);
      cudaFree(device_c);
      return 3;
    }
    checksum += c[i];
  }

  cudaFree(device_a);
  cudaFree(device_b);
  cudaFree(device_c);
  std::printf("C16_NCU_CANARY_NATIVE_PASS elements=%zu checksum=%llu kernel=c16_vector_add_kernel\n",
              kElements, static_cast<unsigned long long>(checksum));
  return 0;
}
