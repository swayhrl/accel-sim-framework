#include <cuda_runtime.h>
#include <cstdio>
__device__ __noinline__ unsigned mix(unsigned x){asm volatile("");return x*13+7;}
__global__ void call_probe(unsigned*out,unsigned n){unsigned i=blockIdx.x*blockDim.x+threadIdx.x;if(i<n)out[i]=mix(i)+i*3;}
int main(){unsigned*d,h[65];if(cudaMalloc(&d,sizeof(h))!=cudaSuccess)return 2;call_probe<<<2,64>>>(d,65);if(cudaGetLastError()!=cudaSuccess||cudaDeviceSynchronize()!=cudaSuccess)return 3;if(cudaMemcpy(h,d,sizeof(h),cudaMemcpyDeviceToHost)!=cudaSuccess)return 4;for(unsigned i=0;i<65;i++)if(h[i]!=i*16+7)return 5;cudaFree(d);puts("Test PASSED call_probe65");}
