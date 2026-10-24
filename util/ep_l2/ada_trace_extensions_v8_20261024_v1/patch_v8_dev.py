import pathlib
R=pathlib.Path('/data/c16/ada_trace_extensions_v8_20261024_v1/producer')
p=R/'tracer_tool.cu';s=p.read_text().replace('#define TRACER_VERSION "7"','#define TRACER_VERSION "8"')
a=s.index('      // Temporary workaround for a bug');b=s.index('      uint32_t selection_index',a);s=s[:a]+s[b:]
a=s.index('__global__ void flush_channel()');b=s.index('static void enter_kernel_launch',a)
s=s[:a]+'''#include "tool_func/flush_channel.c"
static CUmodule ada_flush_module;
static CUfunction ada_flush_function;
static void ada_flush(CUcontext ctx,CUstream stream=nullptr) {
  ChannelDev *pointer=&channel_dev;void*args[]={&pointer};
  nvbit_launch_kernel(ctx,ada_flush_function,1,1,1,1,1,1,0,stream,args,nullptr);
}
static std::set<CUcontext> ada_contexts;
static void ada_api(const char*name,CUcontext ctx,int is_exit) {
  mkdir((std::string(getcwd(nullptr,0))+"/traces").c_str(),0755);
  std::ofstream out(std::string(getcwd(nullptr,0))+"/traces/ada-api.tsv",std::ios::app);
  out<<name<<"\\t"<<std::hex<<(uintptr_t)ctx<<"\\t"<<std::dec<<is_exit<<"\\n";
  if(std::string(name).find("Graph")!=std::string::npos){fprintf(stderr,"ADA_UNSUPPORTED_GRAPH_API %s\\n",name);abort();}
}
''' +s[b:]
s=s.replace('flush_channel<<<1, 1>>>();','ada_flush(ctx);').replace('flush_channel<<<1, 1, 0, p->hStream>>>();','ada_flush(ctx,p->hStream);')
s=s.replace('  if (skip_flag)\n    return;','  if (skip_flag)\n    return;\n  ada_api(name,ctx,is_exit);')
s=s.replace('  // Everytime we init a context, add the foldername and kernelid to the set','''  if(!ada_contexts.insert(ctx).second || ada_contexts.size()>1){fprintf(stderr,"ADA_UNSUPPORTED_MULTIPLE_CONTEXTS\\n");abort();}
  skip_flag=true;
  nvbit_load_tool_module(ctx,(const void*)ada_flush_bin,&ada_flush_module);
  nvbit_find_function_by_name(ctx,ada_flush_module,"ada_flush_channel",&ada_flush_function);
  skip_flag=false;
  // Everytime we init a context, add the foldername and kernelid to the set''')
s=s.replace('ADA7 %08x','ADA8 %08x')
p.write_text(s)
(R/'tool_func').mkdir()
(R/'tool_func/flush_channel.cu').write_text('''#include "utils/channel.hpp"
#include "common.h"
extern "C" __global__ void ada_flush_channel(ChannelDev *channel) {inst_trace_t ma;ma.cta_id_x=-1;channel->push(&ma,sizeof(ma));channel->flush();}
''')
p=R/'Makefile';s=p.read_text().replace('/data/c16/env/nvbit-1.7.5/core','/data/c16/env/nvbit-1.7.7.1/core')
s=s.replace('all: $(NVBIT_TOOL)','''all: $(NVBIT_TOOL)
tool_func/flush_channel.fatbin: tool_func/flush_channel.cu common.h
\t$(NVCC) -arch=$(ARCH) $(INCLUDES) -I. -O3 -fatbin $< -o $@
tool_func/flush_channel.c: tool_func/flush_channel.fatbin
\tbin2c -c --name ada_flush_bin $< > $@
tracer_tool.o: tool_func/flush_channel.c
''')
p.write_text(s)
