#include <cuda_runtime.h>
#include <cstdio>
typedef unsigned (*Fn)(unsigned);
__device__ __noinline__ unsigned target0(unsigned x){asm volatile("");return x+1;}
__device__ __noinline__ unsigned target1(unsigned x){asm volatile("");return x*3+7;}
__device__ Fn targets[2]={target0,target1};
__global__ void probe(unsigned*out){unsigned i=threadIdx.x;if(i<37){Fn f=targets[i&1];out[i]=f(i);}}
int main(){unsigned *d,h[37];if(cudaMalloc(&d,sizeof(h))!=cudaSuccess)return 2;probe<<<1,37>>>(d);if(cudaGetLastError()!=cudaSuccess||cudaDeviceSynchronize()!=cudaSuccess)return 3;if(cudaMemcpy(h,d,sizeof(h),cudaMemcpyDeviceToHost)!=cudaSuccess)return 4;for(unsigned i=0;i<37;i++)if(h[i]!=((i&1)?i*3+7:i+1))return 5;cudaFree(d);puts("PASS37 indirect candidate");}
