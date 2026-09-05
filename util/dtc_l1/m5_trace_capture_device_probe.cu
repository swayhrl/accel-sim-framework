#include <cuda_runtime.h>
#include <cstdio>
int main() {
  int n = 0; cudaError_t e = cudaGetDeviceCount(&n);
  if (e != cudaSuccess || n != 1) { std::fprintf(stderr, "FAIL visible_cuda_device_count=%d: %s\n", n, cudaGetErrorString(e)); return 2; }
  cudaDeviceProp p{}; cudaDeviceGetProperties(&p, 0); cudaUUID_t u{}; cudaDeviceGetUuid(&u, 0);
  std::printf("logical_device\tname\tuuid\tcc\ttotal_mem_bytes\n0\t%s\tGPU-", p.name);
  for (unsigned char b : u.bytes) std::printf("%02x", b);
  std::printf("\t%d.%d\t%zu\n", p.major, p.minor, p.totalGlobalMem);
  return (p.major == 7 && p.minor == 0) ? 0 : 3;
}
