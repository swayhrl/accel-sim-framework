#include <bits/stdc++.h>
#include <sys/stat.h>
#include <unistd.h>
using CUcontext=void*;using CUstream=void*;using CUdeviceptr=uint64_t;using CUresult=int;
const int CUDA_SUCCESS=0;
struct cuMemcpyHtoD_v2_params{CUdeviceptr dstDevice;const void*srcHost;size_t ByteCount;};
struct cuMemcpyHtoDAsync_v2_params{CUdeviceptr dstDevice;const void*srcHost;size_t ByteCount;CUstream hStream;};
struct cuMemcpyDtoH_v2_params{void*dstHost;CUdeviceptr srcDevice;size_t ByteCount;};
struct cuStreamSynchronize_params{CUstream hStream;};
struct cuMemAlloc_v2_params{CUdeviceptr*dptr;size_t bytesize;};struct cuMemFree_v2_params{CUdeviceptr dptr;};
std::string user_folder;
#include "../shared/gaussian_scope_v1.h"
#include "../producer/ada_input_snapshot.h"
#include "../producer/gaussian_io_observer.h"
int main(int argc,char**argv){user_folder=argv[1];std::filesystem::create_directories(user_folder+"/traces");setenv("ADA_INPUT_SNAPSHOT","1",1);
 CUcontext ctx=(void*)1;CUresult ok=0;unsigned char src[16],dst[16];for(int i=0;i<16;i++)src[i]=i;
 cuMemcpyHtoD_v2_params h{0x1000,src,16};ada_input_event(ctx,0,"cuMemcpyHtoD_v2",&h,&ok);ada_input_event(ctx,1,"cuMemcpyHtoD_v2",&h,&ok);
 cuMemcpyDtoH_v2_params d{dst,0x1000,16};gaussian_output_event(ctx,0,"cuMemcpyDtoH_v2",&d,&ok);memcpy(dst,src,16);
 if(argc>2&&std::string(argv[2])=="async"){gaussian_output_event(ctx,1,"cuMemcpyDtoHAsync_v2",&d,&ok);return 5;}
 gaussian_output_event(ctx,1,"cuMemcpyDtoH_v2",&d,&ok);gaussian_io_finish(ctx);std::cout<<"PASS_CPU_API_STUB_NOT_GPU\n";
}
