#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <string>
#include <unistd.h>
#include <vector>
#include "nvbit.h"
#include "nvbit_tool.h"
static std::string path,code,match;static std::atomic<bool> done{false};
static bool launch(nvbit_api_cuda_t c,void*p,CUfunction*f){switch(c){case API_CUDA_cuLaunch:case API_CUDA_cuLaunchGrid:case API_CUDA_cuLaunchGridAsync:*f=((cuLaunch_params*)p)->f;return true;case API_CUDA_cuLaunchKernel:case API_CUDA_cuLaunchKernel_ptsz:case API_CUDA_cuLaunchCooperativeKernel:case API_CUDA_cuLaunchCooperativeKernel_ptsz:*f=((cuLaunchKernel_params*)p)->f;return true;case API_CUDA_cuLaunchKernelEx:case API_CUDA_cuLaunchKernelEx_ptsz:*f=((cuLaunchKernelEx_params*)p)->f;return true;default:return false;}}
static bool mref(Instr*i){for(int n=0;n<i->getNumOperands();n++)if(i->getOperand(n)->type==InstrType::OperandType::MREF)return true;return false;}
static std::string esc(const char*x){std::string s=x?x:"";for(char&c:s)if(c=='\t'||c=='\n'||c=='\r')c=' ';return s;}
static void emit(CUcontext c,CUfunction f){auto v=nvbit_get_instrs(c,f);std::string tmp=path+".tmp."+std::to_string(getpid());std::ofstream o(tmp);auto full=esc(nvbit_get_func_name(c,f));auto mang=esc(nvbit_get_func_name(c,f,true));char addr[32];snprintf(addr,sizeof(addr),"0x%llx",(unsigned long long)nvbit_get_func_addr(c,f));o<<"nvbit_static_index\tvector_ordinal\tinstruction_offset\topcode\tmemory_space\tis_load\tis_store\thas_mref\tsass\tfunction_full_name\tfunction_mangled_name\tfunction_address\tlibtorch_cuda_sha256\n";for(size_t n=0;n<v.size();n++){Instr*i=v[n];o<<i->getIdx()<<'\t'<<n<<'\t'<<i->getOffset()<<'\t'<<esc(i->getOpcode())<<'\t'<<InstrType::MemorySpaceStr[(int)i->getMemorySpace()]<<'\t'<<(i->isLoad()?1:0)<<'\t'<<(i->isStore()?1:0)<<'\t'<<(mref(i)?1:0)<<'\t'<<esc(i->getSass())<<'\t'<<full<<'\t'<<mang<<'\t'<<addr<<'\t'<<code<<'\n';}o.close();if(rename(tmp.c_str(),path.c_str())==0){done=true;printf("C16_V23R1_STATIC_DISCOVERY_COMPLETE function_mangled=%s static_instruction_count=%zu map=%s\n",mang.c_str(),v.size(),path.c_str());fflush(stdout);}}
void nvbit_at_init(){char*p=getenv("C16_NVBIT_STATIC_MAP_PATH"),*s=getenv("C16_NVBIT_CODE_OBJECT_SHA256"),*m=getenv("C16_V23R1_MATCH");if(!p||!s||!m||strlen(s)!=64)abort();path=p;code=s;match=m;printf("C16_V23R1_STATIC_DISCOVERY_READY match=%s\n",match.c_str());fflush(stdout);}
void nvbit_at_cuda_event(CUcontext c,int exit,nvbit_api_cuda_t cb,const char*,void*p,CUresult*){if(exit||done)return;CUfunction f=nullptr;if(!launch(cb,p,&f)||!f)return;const char*n=nvbit_get_func_name(c,f);if(n&&strstr(n,match.c_str()))emit(c,f);}
void nvbit_at_term(){printf("C16_V23R1_STATIC_DISCOVERY_TERMINAL map_emitted=%d\n",done?1:0);fflush(stdout);}
