#include <cuda_profiler_api.h>
#include <cstdio>
__global__ void add_one(int *p) { p[threadIdx.x] += 1; }
int main() { int *p=nullptr; cudaMalloc(&p, 256*sizeof(int)); cudaProfilerStart(); add_one<<<1,256>>>(p); cudaDeviceSynchronize(); cudaProfilerStop(); cudaFree(p); return 0; }
