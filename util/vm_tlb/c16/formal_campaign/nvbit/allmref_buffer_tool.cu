#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <string>
#include <vector>
#include "nvbit.h"
#include "nvbit_tool.h"
#include "utils/utils.h"
#include "allmref_buffer_common.h"
extern "C" __device__ void c16_record_mref(int,uint64_t,uint32_t,uint64_t,uint64_t,uint64_t);
static unsigned pick=0; static std::string target,out; static unsigned long long want=0,ord=0,cap=0; static int cta_begin=0,cta_end=1; static C16Rec* rec=nullptr; static C16Ctr* ctr=nullptr; static bool installed=false;
static bool hasm(Instr*i){for(int n=0;n<i->getNumOperands();n++)if(i->getOperand(n)->type==InstrType::OperandType::MREF)return true;return false;}
static bool launch(nvbit_api_cuda_t c,void*p,CUfunction*f){if(c==API_CUDA_cuLaunchKernel||c==API_CUDA_cuLaunchKernel_ptsz){*f=((cuLaunchKernel_params*)p)->f;return true;}return false;}
static void setup(CUcontext c,CUfunction f){if(installed)return;for(auto*i:nvbit_get_instrs(c,f)){if(i->getMemorySpace()!=InstrType::MemorySpace::GLOBAL||!hasm(i)||i->getIdx()!=pick)continue;int m=-1,nm=0;for(int k=0;k<i->getNumOperands();k++)if(i->getOperand(k)->type==InstrType::OperandType::MREF){m++;nm++;}for(int k=0;k<nm;k++){nvbit_insert_call(i,"c16_record_mref",IPOINT_BEFORE);nvbit_add_call_arg_guard_pred_val(i);nvbit_add_call_arg_mref_addr64(i,k);nvbit_add_call_arg_const_val32(i,i->getIdx());nvbit_add_call_arg_const_val64(i,(uint64_t)rec);nvbit_add_call_arg_const_val64(i,(uint64_t)ctr);nvbit_add_call_arg_const_val64(i,cap);nvbit_add_call_arg_const_val32(i,cta_begin);nvbit_add_call_arg_const_val32(i,cta_end);}}installed=true;}
void nvbit_at_init(){const char*f=getenv("C16_MREF_FUNCTION"),*o=getenv("C16_MREF_OUTPUT"),*w=getenv("C16_MREF_LAUNCH"),*z=getenv("C16_MREF_CAPACITY"),*q=getenv("C16_MREF_STATIC_INDEX");if(!f||!o||!w||!z||!q)abort(); pick=(unsigned)strtoul(q,0,10);target=f;out=o;want=strtoull(w,0,10);cap=strtoull(z,0,10); const char*a=getenv("C16_CTA_BEGIN"),*b=getenv("C16_CTA_END"); if(a)cta_begin=atoi(a); if(b)cta_end=atoi(b); if(cta_end<=cta_begin)abort();}
void nvbit_tool_init(CUcontext){CUDA_SAFECALL(cudaMallocManaged(&rec,cap*sizeof(C16Rec)));CUDA_SAFECALL(cudaMallocManaged(&ctr,sizeof(C16Ctr)));ctr->count=ctr->overflow=0;}
void nvbit_at_cuda_event(CUcontext c,int exit,nvbit_api_cuda_t k,const char*,void*p,CUresult*){if(exit)return;CUfunction f;if(!launch(k,p,&f))return;ord++;if(target!=std::string(nvbit_get_func_name(c,f,true)))return;setup(c,f);nvbit_set_at_launch(c,f,ord);nvbit_enable_instrumented(c,f,ord==want);}
void nvbit_at_term(){cudaDeviceSynchronize();std::ofstream q(out,std::ios::binary);unsigned long long n=ctr?ctr->count:0,keep=n<cap?n:cap;q.write("C16MREF1",8);q.write((char*)&want,8);q.write((char*)&n,8);q.write((char*)&ctr->overflow,8);q.write((char*)&keep,8);q.write((char*)rec,keep*sizeof(C16Rec));q.close();printf("C16_MREF_TERMINAL launch=%llu records=%llu overflow=%llu\n",want,n,ctr->overflow);}
