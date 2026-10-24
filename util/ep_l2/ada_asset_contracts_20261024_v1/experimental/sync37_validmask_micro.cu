#include <cuda_runtime.h>
#include <cstdio>
__global__ void sync_probe(unsigned*out,unsigned n,unsigned mask_argument){
 __shared__ unsigned values[64];unsigned i=blockIdx.x*blockDim.x+threadIdx.x;
 if(i<n){values[threadIdx.x]=i+100;unsigned mask=mask_argument & __activemask();__syncwarp(mask);unsigned peer=__ffs(mask)-1;out[i]=values[(threadIdx.x&~31u)+peer];}
}
int main(){unsigned*d,h[65];if(cudaMalloc(&d,sizeof(h))!=cudaSuccess)return 2;sync_probe<<<2,37>>>(d,65,0xffffffffu);
 if(cudaGetLastError()!=cudaSuccess||cudaDeviceSynchronize()!=cudaSuccess)return 3;if(cudaMemcpy(h,d,sizeof(h),cudaMemcpyDeviceToHost)!=cudaSuccess)return 4;
 for(unsigned i=0;i<65;i++)if(h[i]!=(i/37)*37+((i%37)/32)*32+100)return 5;cudaFree(d);puts("Test PASSED sync_probe65");}
