#include <mutex>
#include <sys/syscall.h>
#include <time.h>
static std::mutex ada_gate_mutex;
static unsigned ada_context_lifetimes=0;
static CUcontext ada_process_context=nullptr;
static bool ada_context_closed=false,ada_process_ended=false,ada_have_launch_stream=false;
static uint64_t ada_launch_entries=0,ada_launch_exits=0,ada_pending_launch=0;
static long ada_launch_host_tid=-1;
static CUstream ada_launch_stream=nullptr;
static std::string ada_pending_api;
static void ada_gate_fail(const char*reason){fprintf(stderr,"%s\n",reason);abort();}
static std::ofstream ada_gate_log(){
 std::string dir=user_folder+"/traces";if(mkdir(dir.c_str(),0700)&&errno!=EEXIST)ada_gate_fail("ADA_GATE_TRACE_DIRECTORY_FAILURE");
 std::ofstream log(dir+"/ada-lifecycle.tsv",std::ios::app);if(!log)ada_gate_fail("ADA_GATE_JOURNAL_FAILURE");return log;
}
static uint64_t ada_gate_ns(){timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return uint64_t(t.tv_sec)*1000000000+t.tv_nsec;}
static void ada_gate_context_begin(CUcontext ctx){
 std::lock_guard<std::mutex>g(ada_gate_mutex);unsigned generation=++ada_context_lifetimes;
 auto log=ada_gate_log();log<<"CTX_BEGIN\t"<<generation<<"\t"<<std::hex<<(uintptr_t)ctx<<"\t"<<std::dec<<syscall(SYS_gettid)<<"\t"<<ada_gate_ns()<<"\n";log.flush();
 if(generation!=1||!ctx||ada_process_ended)ada_gate_fail("ADA_UNSUPPORTED_SECOND_CONTEXT_LIFETIME_BEFORE_HEADER_RESET");
 ada_process_context=ctx;ada_context_closed=false;
}
static void ada_gate_context_end(CUcontext ctx){
 std::lock_guard<std::mutex>g(ada_gate_mutex);if(ctx!=ada_process_context||ada_context_closed)ada_gate_fail("ADA_CONTEXT_END_MISMATCH");ada_context_closed=true;
 auto log=ada_gate_log();log<<"CTX_END\t"<<ada_context_lifetimes<<"\t"<<std::hex<<(uintptr_t)ctx<<"\t"<<std::dec<<syscall(SYS_gettid)<<"\t"<<ada_gate_ns()<<"\n";
}
static void ada_gate_event(CUcontext ctx,int is_exit,const char*name,void*params,CUresult*status){
 std::string api(name);
 if(api.find("Graph")!=std::string::npos||api.find("Capture")!=std::string::npos)ada_gate_fail("ADA_UNSUPPORTED_GRAPH_OR_CAPTURE_API");
 bool ex=api=="cuLaunchKernelEx"||api=="cuLaunchKernelEx_ptsz";
 bool direct=ex||api=="cuLaunchKernel"||api=="cuLaunchKernel_ptsz"||api=="cuLaunchCooperativeKernel"||api=="cuLaunchCooperativeKernel_ptsz";
 if(!direct){if(api.find("Launch")!=std::string::npos)ada_gate_fail("ADA_UNSUPPORTED_LEGACY_OR_UNKNOWN_LAUNCH_API");return;}
 CUfunction function;CUstream stream;
 if(ex){auto*p=(cuLaunchKernelEx_params*)params;function=p->f;stream=p->config->hStream;}
 else{auto*p=(cuLaunchKernel_params*)params;function=p->f;stream=p->hStream;}
 std::lock_guard<std::mutex>g(ada_gate_mutex);long tid=syscall(SYS_gettid);
 if(ada_context_lifetimes!=1||ctx!=ada_process_context||ada_context_closed||ada_process_ended)ada_gate_fail("ADA_LAUNCH_CONTEXT_LIFETIME_MISMATCH");
 if(ada_launch_host_tid<0)ada_launch_host_tid=tid;
 if(ada_launch_host_tid!=tid)ada_gate_fail("ADA_UNSUPPORTED_MULTIPLE_LAUNCH_HOST_THREADS");
 if(ada_have_launch_stream&&ada_launch_stream!=stream)ada_gate_fail("ADA_UNSUPPORTED_MULTIPLE_LAUNCH_STREAMS");
 ada_have_launch_stream=true;ada_launch_stream=stream;
 uint64_t ordinal;
 if(!is_exit){if(ada_pending_launch)ada_gate_fail("ADA_OVERLAPPED_LAUNCH_CALLBACK");ordinal=++ada_launch_entries;ada_pending_launch=ordinal;ada_pending_api=api;}
 else {if(!ada_pending_launch||ada_pending_api!=api||!status||*status!=CUDA_SUCCESS)ada_gate_fail("ADA_LAUNCH_RETURN_PAIR_OR_STATUS_FAILURE");ordinal=ada_pending_launch;++ada_launch_exits;ada_pending_launch=0;}
 auto log=ada_gate_log();log<<(is_exit?"LAUNCH_EXIT":"LAUNCH_ENTRY")<<"\t"<<ordinal<<"\t"<<api<<"\t"<<std::hex<<(uintptr_t)ctx<<"\t"<<(uintptr_t)stream<<"\t"<<(uintptr_t)function<<"\t"<<nvbit_get_func_name(ctx,function,true)<<"\t"<<std::dec<<tid<<"\t"<<ada_gate_ns()<<"\t"<<(is_exit?int(*status):-1)<<"\n";
}
static void ada_gate_process_end(){
 std::lock_guard<std::mutex>g(ada_gate_mutex);if(ada_process_ended||ada_pending_launch||ada_launch_entries!=ada_launch_exits)ada_gate_fail("ADA_UNCLOSED_LAUNCH_AT_PROCESS_END");ada_process_ended=true;
 auto log=ada_gate_log();log<<"PROCESS_END\t"<<ada_context_lifetimes<<"\t"<<ada_launch_entries<<"\t"<<ada_launch_exits<<"\t"<<ada_gate_ns()<<"\n";
}
