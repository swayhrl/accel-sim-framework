#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <map>
#include <set>
#include <sstream>
#include <fstream>
#include <iomanip>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <sys/resource.h>
#include <unistd.h>
#include <openssl/sha.h>
using CUcontext=void*;using CUstream=void*;using CUfunction=void*;using CUdeviceptr=uint64_t;using CUresult=int;
static constexpr int CUDA_SUCCESS=0;
struct cuMemcpyDtoH_v2_params {void*dstHost;CUdeviceptr srcDevice;size_t ByteCount;};
struct cuMemcpyHtoD_v2_params {CUdeviceptr dstDevice;const void*srcHost;size_t ByteCount;};
struct cuLaunchKernel_params {CUfunction f;unsigned gridDimX,gridDimY,gridDimZ,blockDimX,blockDimY,blockDimZ,sharedMemBytes;CUstream hStream;void**kernelParams;void**extra;};
static std::string user_folder;
static unsigned ada_context_lifetimes=1;static CUcontext ada_process_context=(void*)1;static bool ada_context_closed=false;
static uint64_t ada_launch_entries=1,ada_launch_exits=1,ada_pending_launch=0;static CUstream ada_launch_stream=nullptr;
static void ada_gate_fail(const char*r){fprintf(stderr,"%s\n",r);abort();}
static uint64_t ada_gate_ns(){return 123;}
static std::string ada_hex_digest(const unsigned char*d){std::ostringstream s;s<<std::hex<<std::setfill('0');for(int i=0;i<32;i++)s<<std::setw(2)<<unsigned(d[i]);return s.str();}
static const char*nvbit_get_func_name(CUcontext,CUfunction,bool){return "_Z6euclidP7latLongPfiff";}
struct AdaMeta {std::string opcode,function;unsigned pc;bool qualified;};
static std::vector<AdaMeta>ada_meta;
static std::map<std::pair<std::string,unsigned>,AdaMeta>ada_map;
#include "/data/c16/ada_call_snapshot_nn_20261024_v1/producer_A3/ada_nn_output_v1.h"
static void run(int mode){
 user_folder="/data/c16/ada_call_snapshot_nn_20261024_v1/cpu_hook_cases/mode"+std::to_string(mode);mkdir(user_folder.c_str(),0700);mkdir((user_folder+"/traces").c_str(),0700);
 std::vector<unsigned char>input(342112);std::vector<float>output(42764,1.f);int status=0;
 cuMemcpyHtoD_v2_params h{0x100000,input.data(),input.size()};
 ada_nn_input_gate((void*)1,0,"cuMemcpyHtoD_v2",&h,&status);
 if(mode==1)h.ByteCount--;
 if(mode==2)status=1;
 ada_nn_input_gate((void*)1,1,"cuMemcpyHtoD_v2",&h,&status);
 CUdeviceptr a=0x100000,b=0x200000;int n=42764;float lat=30.f,lng=90.f;
 if(mode==3)n--;
 if(mode==4)a+=4;
 void*args[]={&a,&b,&n,&lat,&lng};
 cuLaunchKernel_params k{(void*)2,168,1,1,256,1,1,0,nullptr,args,nullptr};
 ada_nn_launch_args((void*)1,0,"cuLaunchKernel",&k,&status);
 cuMemcpyDtoH_v2_params d{output.data(),b,output.size()*4};
 if(mode==5)d.ByteCount--;
 if(mode==6)d.srcDevice+=4;
 if(mode==7)ada_context_closed=true;
 if(mode==8)ada_launch_stream=(void*)3;
 if(mode==9){ada_nn_output_event((void*)1,0,"cuMemcpyDtoHAsync_v2",&d,&status);return;}
 ada_nn_output_event((void*)1,0,"cuMemcpyDtoH_v2",&d,&status);
 if(mode==10)status=1;
 if(mode==11)d.dstHost=input.data();
 ada_nn_output_event((void*)1,1,"cuMemcpyDtoH_v2",&d,&status);
 if(mode==12){ada_nn_output_event((void*)1,0,"cuMemcpyDtoH_v2",&d,&status);return;}
 ada_nn_output_end();
 for(unsigned pc=0;pc<58;pc++){AdaMeta m{"MOV","_Z6euclidP7latLongPfiff",pc*16,true};ada_map[{m.function,m.pc}]=m;ada_meta.push_back(m);}
 if(mode==13)ada_meta.pop_back();
 if(mode==14)ada_meta.push_back(ada_meta.back());
 if(mode==15)ada_meta[0].qualified=false;
 ada_nn_static_closure();
}
int main(){
 rlimit r{0,0};setrlimit(RLIMIT_CORE,&r);
 mkdir("/data/c16/ada_call_snapshot_nn_20261024_v1/cpu_hook_cases",0700);
 for(int mode=0;mode<=15;mode++){
  pid_t p=fork();if(p==0){run(mode);_exit(0);}int st;waitpid(p,&st,0);
  if(mode==0){if(!WIFEXITED(st)||WEXITSTATUS(st))return 2;}
  else if(!WIFSIGNALED(st)||WTERMSIG(st)!=SIGABRT)return 3;
 }
 puts("NN_ACTUAL_HOST_HEADER_PASS positives=1 negatives=15 no_CUDA_driver_or_runtime_link no_GPU no_SIM");
}
