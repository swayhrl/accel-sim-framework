#include <cuda_runtime.h>
#include <cstdio>
#include <cstdint>
__constant__ uint32_t table[64];
__global__ void constant_probe(uint32_t *out,unsigned n) {
 unsigned i=blockIdx.x*blockDim.x+threadIdx.x;
 if(i<n){ unsigned j=(i*7+3)&63;out[i]=table[j]+i; }
}
int main(){uint32_t h[64],out[65];for(unsigned i=0;i<64;i++)h[i]=i*13+11;
 if(cudaMemcpyToSymbol(table,h,sizeof(h))!=cudaSuccess)return 2;
 uint32_t *d;if(cudaMalloc(&d,sizeof(out))!=cudaSuccess)return 3;
 constant_probe<<<2,64>>>(d,65);
 if(cudaGetLastError()!=cudaSuccess||cudaDeviceSynchronize()!=cudaSuccess)return 4;
 if(cudaMemcpy(out,d,sizeof(out),cudaMemcpyDeviceToHost)!=cudaSuccess)return 5;
 uint64_t digest=0;for(unsigned i=0;i<65;i++){if(out[i]!=h[(i*7+3)&63]+i)return 6;digest=digest*131+out[i];}
 cudaFree(d);printf("Test PASSED elements=65 digest=%016llx\n",(unsigned long long)digest);return 0;}
