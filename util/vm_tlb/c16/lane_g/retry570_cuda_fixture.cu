// C16 Retry570 diagnostic-only CUDA fixture.
// It is intentionally independent of a model, selector, and frozen target.
#include <cuda_runtime.h>

#include <cstdio>
#include <vector>

namespace {

constexpr int kElements = 4096;

__global__ void add_one(const float* input, float* output, int count) {
  const int index = blockIdx.x * blockDim.x + threadIdx.x;
  if (index < count) {
    output[index] = input[index] + 1.0F;
  }
}

bool check(cudaError_t status, const char* stage) {
  if (status == cudaSuccess) {
    return true;
  }
  std::fprintf(stderr, "C16_RETRY570_FIXTURE_ERROR stage=%s cuda=%s\n", stage,
               cudaGetErrorString(status));
  return false;
}

}  // namespace

int main() {
  std::printf("C16_RETRY570_FIXTURE_STAGE=START\n");
  if (!check(cudaFree(nullptr), "CUDA_CONTEXT")) return 2;

  std::vector<float> host_input(kElements, 1.0F);
  std::vector<float> host_output(kElements, 0.0F);
  float* device_input = nullptr;
  float* device_output = nullptr;
  if (!check(cudaMalloc(&device_input, kElements * sizeof(float)), "MALLOC_INPUT") ||
      !check(cudaMalloc(&device_output, kElements * sizeof(float)), "MALLOC_OUTPUT") ||
      !check(cudaMemcpy(device_input, host_input.data(), kElements * sizeof(float),
                        cudaMemcpyHostToDevice), "COPY_INPUT")) {
    cudaFree(device_input);
    cudaFree(device_output);
    return 3;
  }

  add_one<<<(kElements + 255) / 256, 256>>>(device_input, device_output, kElements);
  if (!check(cudaGetLastError(), "KERNEL_LAUNCH") ||
      !check(cudaDeviceSynchronize(), "KERNEL_SYNCHRONIZE") ||
      !check(cudaMemcpy(host_output.data(), device_output, kElements * sizeof(float),
                        cudaMemcpyDeviceToHost), "COPY_OUTPUT")) {
    cudaFree(device_input);
    cudaFree(device_output);
    return 4;
  }
  cudaFree(device_input);
  cudaFree(device_output);

  for (float value : host_output) {
    if (value != 2.0F) {
      std::fprintf(stderr, "C16_RETRY570_FIXTURE_ERROR stage=OUTPUT_CHECK\n");
      return 5;
    }
  }
  std::printf("C16_RETRY570_FIXTURE_KERNEL_OBSERVED=add_one\n");
  std::printf("C16_RETRY570_FIXTURE_TERMINAL_STATE=PASS\n");
  return 0;
}
