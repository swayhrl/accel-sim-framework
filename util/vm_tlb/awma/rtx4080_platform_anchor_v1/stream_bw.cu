#include <cuda_runtime.h>
#include <cstdio>
#include <cstdlib>
__global__ void stream_copy(const float* __restrict__ in,float* __restrict__ out,size_t n){for(size_t i=(size_t)blockIdx.x*blockDim.x+threadIdx.x;i<n;i+=(size_t)blockDim.x*gridDim.x)out[i]=in[i]+1.0f;}
int main(int argc,char**argv){size_t n=1<<26;int reps=100;if(argc>1)n=strtoull(argv[1],0,0);if(argc>2)reps=atoi(argv[2]);float *a,*b;cudaMalloc(&a,n*4);cudaMalloc(&b,n*4);cudaMemset(a,0,n*4);stream_copy<<<4096,256>>>(a,b,n);cudaDeviceSynchronize();cudaEvent_t s,e;cudaEventCreate(&s);cudaEventCreate(&e);cudaEventRecord(s);for(int i=0;i<reps;i++)stream_copy<<<4096,256>>>(a,b,n);cudaEventRecord(e);cudaEventSynchronize(e);float ms;cudaEventElapsedTime(&ms,s,e);printf("elements\trepetitions\tbytes_per_iteration\telapsed_ms\tgb_per_s\n%zu\t%d\t%zu\t%.6f\t%.6f\n",n,reps,n*8,ms,(double)(n*8*reps)/(ms*1e6));cudaFree(a);cudaFree(b);}
