#include <cuda_runtime.h>
#include <cstdio>
#include <cstring>
__global__ void cache_friendly(const float* a,float* b,int n){for(int i=threadIdx.x;i<n;i+=blockDim.x)b[i]=a[i]+b[i];}
__global__ void streaming(const float* a,float* b,int n){for(int i=(int)blockIdx.x*blockDim.x+threadIdx.x;i<n;i+=blockDim.x*gridDim.x)b[i]=a[i]+1.f;}
__global__ void compute_mixed(float* a,int n){for(int i=(int)blockIdx.x*blockDim.x+threadIdx.x;i<n;i+=blockDim.x*gridDim.x){float x=a[i]; for(int j=0;j<64;j++)x=x*1.000001f+0.000001f;a[i]=x;}}
int main(int argc,char**argv){const char* m=argc>1?argv[1]:"cache";int n=argc>2?atoi(argv[2]):(1<<20),r=argc>3?atoi(argv[3]):100;float *a,*b;cudaMalloc(&a,(size_t)n*4);cudaMalloc(&b,(size_t)n*4);cudaMemset(a,0,(size_t)n*4);cudaMemset(b,0,(size_t)n*4);cudaEvent_t s,e;cudaEventCreate(&s);cudaEventCreate(&e);auto k=[&](){if(!strcmp(m,"cache"))cache_friendly<<<1,256>>>(a,b,n);else if(!strcmp(m,"stream"))streaming<<<4096,256>>>(a,b,n);else compute_mixed<<<4096,256>>>(a,n);};k();cudaDeviceSynchronize();cudaEventRecord(s);for(int i=0;i<r;i++)k();cudaEventRecord(e);cudaEventSynchronize(e);float ms;cudaEventElapsedTime(&ms,s,e);printf("mode\telements\trepetitions\telapsed_ms\n%s\t%d\t%d\t%.6f\n",m,n,r,ms);}
