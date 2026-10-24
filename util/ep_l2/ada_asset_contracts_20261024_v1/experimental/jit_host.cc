#include <cuda.h>
#include <cstdio>
#include <vector>
#define CK(x) do{CUresult api_result=(x);if(api_result!=CUDA_SUCCESS){const char*s;cuGetErrorString(api_result,&s);fprintf(stderr,"%s\n",s);return 2;}}while(0)
int main(int argc,char**argv){if(argc!=2)return 2;CK(cuInit(0));CUdevice d;CK(cuDeviceGet(&d,0));CUcontext c;CK(cuCtxCreate(&c,0,d));CUmodule m;CK(cuModuleLoad(&m,argv[1]));CUfunction f;CK(cuModuleGetFunction(&f,m,"jit_leaf"));CUdeviceptr p;CK(cuMemAlloc(&p,65*4));unsigned n=65;void*args[]={&p,&n};CK(cuLaunchKernel(f,2,1,1,37,1,1,0,0,args,0));CK(cuCtxSynchronize());std::vector<unsigned> out(n);CK(cuMemcpyDtoH(out.data(),p,n*4));for(unsigned i=0;i<n;i++)if(out[i]!=17*i+5){fprintf(stderr,"Mismatch %u %u\n",i,out[i]);return 3;}CK(cuMemFree(p));CK(cuModuleUnload(m));CK(cuCtxDestroy(c));puts("Test PASSED");}
