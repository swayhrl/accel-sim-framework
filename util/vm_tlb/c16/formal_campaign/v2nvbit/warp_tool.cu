#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <string>
#include <vector>
#include "nvbit.h"
#include "nvbit_tool.h"
#include "utils/utils.h"
#include "warp_common.h"
extern "C" __device__ void c16_warp_record(int,uint64_t,uint32_t,uint64_t,uint64_t,int,int);
static WState* st=nullptr; static std::string fn,out; static unsigned pick=0,operand=0,selected=0; static unsigned long long cap=0; static int cb=0,ce=2147483647; static bool installed=false,skip=false,done=false;
static bool islaunch(nvbit_api_cuda_t k,void*p,CUfunction*f){if(k==API_CUDA_cuLaunchKernel||k==API_CUDA_cuLaunchKernel_ptsz){*f=((cuLaunchKernel_params*)p)->f;return true;}return false;}
static bool mref(Instr*i){for(int n=0;n<i->getNumOperands();n++)if(i->getOperand(n)->type==InstrType::OperandType::MREF)return true;return false;}
static void install(CUcontext c,CUfunction f){if(installed)return;for(auto*i:nvbit_get_instrs(c,f)){auto ms=i->getMemorySpace();if(i->getIdx()!=pick||(ms!=InstrType::MemorySpace::GLOBAL&&ms!=InstrType::MemorySpace::GLOBAL_TO_SHARED)||!mref(i))continue;unsigned n=0,total=0;for(int k=0;k<i->getNumOperands();k++)if(i->getOperand(k)->type==InstrType::OperandType::MREF){if(n==operand){nvbit_insert_call(i,"c16_warp_record",IPOINT_BEFORE);nvbit_add_call_arg_guard_pred_val(i);nvbit_add_call_arg_mref_addr64(i,k);nvbit_add_call_arg_const_val32(i,pick);nvbit_add_call_arg_const_val64(i,(uint64_t)st);nvbit_add_call_arg_const_val64(i,cap);nvbit_add_call_arg_const_val32(i,cb);nvbit_add_call_arg_const_val32(i,ce);}n++;total++;}printf("C16_LDGSTS_OPERANDS static=%u memory_space=%s selected_operand=%u mref_count=%u\n",pick,InstrType::MemorySpaceStr[(int)ms],operand,total);fflush(stdout);}installed=true;}
void nvbit_at_init(){const char*a=getenv("C16_WARP_FUNCTION"),*b=getenv("C16_WARP_OUTPUT"),*c=getenv("C16_WARP_STATIC"),*d=getenv("C16_WARP_FUNCTION_OCCURRENCE"),*e=getenv("C16_WARP_CAPACITY");const char*q=getenv("C16_WARP_OPERAND");if(!a||!b||!c||!d||!e||!q)abort();operand=strtoul(q,0,10);fn=a;out=b;pick=strtoul(c,0,10);selected=strtoul(d,0,10);cap=strtoull(e,0,10);if(getenv("C16_CTA_BEGIN"))cb=atoi(getenv("C16_CTA_BEGIN"));if(getenv("C16_CTA_END"))ce=atoi(getenv("C16_CTA_END"));}
void nvbit_tool_init(CUcontext){CUDA_SAFECALL(cudaMallocManaged(&st,sizeof(WState)));CUDA_SAFECALL(cudaMallocManaged(&st->rec,cap*sizeof(WRec)));st->count=st->overflow=st->seen=0;}
void nvbit_at_cuda_event(CUcontext c,int exit,nvbit_api_cuda_t k,const char*,void*p,CUresult*){if(skip||done)return;CUfunction f;if(!islaunch(k,p,&f)||fn!=std::string(nvbit_get_func_name(c,f,true)))return;if(!exit){install(c,f);bool take=st->seen==selected;if(take){skip=true;CUDA_SAFECALL(cudaDeviceSynchronize());CUDA_SAFECALL(cudaMemset(&st->count,0,sizeof(st->count)));CUDA_SAFECALL(cudaMemset(&st->overflow,0,sizeof(st->overflow)));skip=false;}nvbit_set_at_launch(c,f,st->seen);nvbit_enable_instrumented(c,f,take);st->seen++;}else if(st->seen==selected+1){skip=true;CUDA_SAFECALL(cudaDeviceSynchronize());std::ofstream q(out,std::ios::binary);unsigned long long keep=st->count<cap?st->count:cap;q.write("C16WARP1",8);q.write((char*)&pick,4);q.write((char*)&selected,4);q.write((char*)&st->count,8);q.write((char*)&st->overflow,8);q.write((char*)&keep,8);q.write((char*)st->rec,keep*sizeof(WRec));q.close();printf("C16_WARP_TERMINAL static=%u occurrence=%u records=%llu overflow=%llu\n",pick,selected,st->count,st->overflow);fflush(stdout);done=true;skip=false;}}
void nvbit_at_ctx_term(CUcontext){if(st){if(st->rec)cudaFree(st->rec);cudaFree(st);st=nullptr;}}
