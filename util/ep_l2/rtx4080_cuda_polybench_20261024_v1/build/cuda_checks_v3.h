#include <cuda_runtime.h>
#include <stdio.h>
#include <stdlib.h>
static inline cudaError_t ep_cuda_checked(cudaError_t e,const char *op,int line){if(e!=cudaSuccess){fprintf(stderr,"CUDA_ERROR line=%d op=%s err=%s\n",line,op,cudaGetErrorString(e));exit(3);}return e;}
#define cudaMalloc(...) ep_cuda_checked(cudaMalloc(__VA_ARGS__),"cudaMalloc",__LINE__)
#define cudaMemcpy(...) ep_cuda_checked(cudaMemcpy(__VA_ARGS__),"cudaMemcpy",__LINE__)
#define cudaFree(...) ep_cuda_checked(cudaFree(__VA_ARGS__),"cudaFree",__LINE__)
#define cudaSetDevice(...) ep_cuda_checked(cudaSetDevice(__VA_ARGS__),"cudaSetDevice",__LINE__)
#undef cudaGetDeviceProperties
#define cudaGetDeviceProperties(...) ep_cuda_checked(cudaGetDeviceProperties_v2(__VA_ARGS__),"cudaGetDeviceProperties",__LINE__)
#define cudaGetDeviceCount(...) ep_cuda_checked(cudaGetDeviceCount(__VA_ARGS__),"cudaGetDeviceCount",__LINE__)
#define cudaThreadSynchronize(...) ep_cuda_checked(cudaThreadSynchronize(__VA_ARGS__),"cudaThreadSynchronize",__LINE__)
