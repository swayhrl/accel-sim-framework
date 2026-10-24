#include <cuda.h>
#include <cstdio>
#include <cstring>
#include <vector>
#define CK(x) do { CUresult s=(x); if(s!=CUDA_SUCCESS){const char *e=nullptr;cuGetErrorString(s,&e);fprintf(stderr,"%s: %s\\n",#x,e?e:"unknown");return 2;} } while(0)
int main(int argc,char **argv){
 if(argc!=3)return 1; const char *mode=argv[2];
 if(strcmp(mode,"grid")&&strcmp(mode,"grid_async")&&strcmp(mode,"launch"))return 1;
 CK(cuInit(0));CUdevice d;CK(cuDeviceGet(&d,0));CUcontext c;CK(cuCtxCreate(&c,0,d));
 CUmodule m;CK(cuModuleLoad(&m,argv[1]));CUfunction f;CK(cuModuleGetFunction(&f,m,"jit_leaf"));
 CUdeviceptr p;CK(cuMemAlloc(&p,65*sizeof(unsigned)));unsigned n=65;
 // Legacy parameter bytes, explicit64-bit pointer at0 and uint32 n at8.
 CK(cuParamSetv(f,0,&p,sizeof(p)));CK(cuParamSeti(f,8,n));CK(cuParamSetSize(f,12));
 CK(cuFuncSetBlockShape(f,!strcmp(mode,"launch")?65:37,1,1));
 CK(cuFuncSetSharedSize(f,0));CUstream stream=nullptr;
 if(!strcmp(mode,"grid")){CK(cuLaunchGrid(f,2,1));}
 else if(!strcmp(mode,"grid_async")){CK(cuStreamCreate(&stream,CU_STREAM_DEFAULT));CK(cuLaunchGridAsync(f,2,1,stream));}
 else {CK(cuLaunch(f));}
 CK(cuCtxSynchronize());std::vector<unsigned> out(n);CK(cuMemcpyDtoH(out.data(),p,n*4));
 for(unsigned i=0;i<n;i++)if(out[i]!=17*i+5){fprintf(stderr,"Mismatch %u %u\\n",i,out[i]);return 3;}
 if(stream)CK(cuStreamDestroy(stream));CK(cuMemFree(p));CK(cuModuleUnload(m));CK(cuCtxDestroy(c));
 printf("Test PASSED legacy_mode=%s full65_reference=1\\n",mode);
}
