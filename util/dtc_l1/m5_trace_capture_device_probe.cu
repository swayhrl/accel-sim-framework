#include <cuda_runtime.h>
#include <cuda.h>
#include <cstdio>
int main() {
  int n = 0; cudaError_t e = cudaGetDeviceCount(&n);
  if (e != cudaSuccess || n != 1) { std::fprintf(stderr, "FAIL visible_cuda_device_count=%d: %s\n", n, cudaGetErrorString(e)); return 2; }
  cudaDeviceProp p{};
  if (cudaGetDeviceProperties(&p, 0) != cudaSuccess) { std::fprintf(stderr, "FAIL cudaGetDeviceProperties\n"); return 4; }
  CUdevice d{}; CUuuid u{};
  if (cuInit(0) != CUDA_SUCCESS || cuDeviceGet(&d, 0) != CUDA_SUCCESS || cuDeviceGetUuid(&u, d) != CUDA_SUCCESS) { std::fprintf(stderr, "FAIL CUDA Driver UUID query\n"); return 5; }
  std::printf("logical_device\tname\tuuid\tcc\ttotal_mem_bytes\n0\t%s\tGPU-", p.name);
  for (unsigned char b : u.bytes) std::printf("%02x", b);
  std::printf("\t%d.%d\t%zu\n", p.major, p.minor, p.totalGlobalMem);
  return (p.major == 7 && p.minor == 0) ? 0 : 3;
}
