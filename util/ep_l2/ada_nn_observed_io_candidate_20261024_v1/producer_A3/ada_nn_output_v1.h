
// Exact NN output observation: original successful synchronous DtoH return only.
// No CUDA readback, copy, event or synchronization is introduced by this hook.
struct AdaNNOutput {CUcontext ctx=nullptr;CUdeviceptr source=0;void*host=nullptr;size_t bytes=0;long tid=-1;};
static thread_local std::vector<AdaNNOutput> ada_nn_output_stack;
static unsigned ada_nn_output_count=0,ada_nn_htod_count=0;
static CUdeviceptr ada_nn_input_dst=0,ada_nn_output_arg=0;
static CUcontext ada_nn_input_ctx=nullptr;
static void ada_nn_write(const std::string&path,const void*data,size_t bytes) {
 FILE*f=fopen(path.c_str(),"wx");if(!f)ada_gate_fail("ADA_NN_EXCLUSIVE_OUTPUT_OPEN_FAILURE");
 if(fwrite(data,1,bytes,f)!=bytes||fflush(f)||fsync(fileno(f))||fclose(f))ada_gate_fail("ADA_NN_OUTPUT_DURABILITY_FAILURE");
}

static void ada_nn_input_gate(CUcontext ctx,int is_exit,const char*name,void*params,CUresult*status) {
 std::string api(name);if(api.rfind("cuMemcpyHtoD",0)!=0)return;
 if(api!="cuMemcpyHtoD_v2")ada_gate_fail("ADA_NN_SYNC_HTOD_ONLY");
 auto*p=static_cast<cuMemcpyHtoD_v2_params*>(params);
 if(!is_exit){
  if(ada_nn_htod_count||ada_nn_input_dst||!p->dstDevice||!p->srcHost||p->ByteCount!=342112)ada_gate_fail("ADA_NN_HTOD_EXACT_SCOPE");
  ada_nn_input_dst=p->dstDevice;ada_nn_input_ctx=ctx;
 }else{
  if(!status||*status!=CUDA_SUCCESS||ctx!=ada_nn_input_ctx||p->dstDevice!=ada_nn_input_dst||p->ByteCount!=342112)ada_gate_fail("ADA_NN_HTOD_RETURN_PAIR");
  ++ada_nn_htod_count;
 }
}
static void ada_nn_launch_args(CUcontext ctx,int is_exit,const char*name,void*params,CUresult*status){
 std::string api(name);if(api!="cuLaunchKernel"&&api!="cuLaunchKernel_ptsz")return;
 auto*p=static_cast<cuLaunchKernel_params*>(params);
 if(is_exit)return;
 if(ada_nn_htod_count!=1||ctx!=ada_nn_input_ctx||p->gridDimX!=168||p->gridDimY!=1||p->gridDimZ!=1||p->blockDimX!=256||p->blockDimY!=1||p->blockDimZ!=1||p->sharedMemBytes||p->hStream||p->extra||!p->kernelParams||std::string(nvbit_get_func_name(ctx,p->f,true))!="_Z6euclidP7latLongPfiff")ada_gate_fail("ADA_NN_EXACT_LAUNCH_ARGS");
 CUdeviceptr input=0,output=0;int records=0;uint32_t lat=0,lng=0;
 for(int i=0;i<5;i++)if(!p->kernelParams[i])ada_gate_fail("ADA_NN_NULL_KERNEL_ARG");
 memcpy(&input,p->kernelParams[0],8);memcpy(&output,p->kernelParams[1],8);memcpy(&records,p->kernelParams[2],4);memcpy(&lat,p->kernelParams[3],4);memcpy(&lng,p->kernelParams[4],4);
 if(input!=ada_nn_input_dst||!output||records!=42764||lat!=0x41f00000u||lng!=0x42b40000u)ada_gate_fail("ADA_NN_KERNEL_VALUE_SCOPE");
 ada_nn_output_arg=output;
 std::ostringstream line;line<<"KERNEL_ARGS\t"<<std::hex<<(uintptr_t)ctx<<"\t"<<(uintptr_t)p->f<<"\t"<<input<<"\t"<<output<<"\t"<<lat<<"\t"<<lng<<std::dec<<"\t"<<records<<"\t168,1,1\t256,1,1\tHOST_KERNELPARAMS_ENTRY_OBSERVATION_NOT_FULL_BANK0_SNAPSHOT\n";
 auto text=line.str();ada_nn_write(user_folder+"/traces/ada-nn-kernel-args.tsv",text.data(),text.size());
}
static void ada_nn_static_closure(){
 if(ada_map.size()!=58)ada_gate_fail("ADA_NN_EXPECTED_STATIC_MAP58");
 std::set<std::pair<std::string,unsigned>>seen;
 for(const auto&m:ada_meta){
  if(m.opcode=="NOP")continue;
  if(!m.qualified||m.function!="_Z6euclidP7latLongPfiff"||!seen.emplace(m.function,m.pc).second)ada_gate_fail("ADA_NN_STATIC_UNQUALIFIED_OR_DUPLICATE_PC");
 }
 if(seen.size()!=58)ada_gate_fail("ADA_NN_STATIC_PC_CLOSURE_MISSING");
 for(const auto&kv:ada_map)if(!seen.count(kv.first))ada_gate_fail("ADA_NN_MAP_PC_NOT_INSTRUMENTED");
}

static void ada_nn_output_event(CUcontext ctx,int is_exit,const char*name,void*params,CUresult*status){
 std::string api(name);
 if(api.rfind("cuMemcpyDtoH",0)!=0)return;
 if(api!="cuMemcpyDtoH_v2")ada_gate_fail("ADA_NN_UNSUPPORTED_DTOH_API");
 auto*p=static_cast<cuMemcpyDtoH_v2_params*>(params);
 if(!is_exit) {
  if(ada_context_lifetimes!=1||ctx!=ada_process_context||ada_context_closed||ada_launch_entries!=1||ada_launch_exits!=1||ada_pending_launch||ada_launch_stream!=nullptr||ada_nn_output_count||!ada_nn_output_stack.empty())ada_gate_fail("ADA_NN_DTOH_LIFETIME_OR_LAUNCH_SCOPE");
  if(!p->dstHost||!p->srcDevice||p->srcDevice!=ada_nn_output_arg||p->ByteCount!=171056)ada_gate_fail("ADA_NN_DTOH_EXACT_RANGE");
  ada_nn_output_stack.push_back({ctx,p->srcDevice,p->dstHost,p->ByteCount,syscall(SYS_gettid)});
 } else {
  if(ada_nn_output_stack.size()!=1||!status||*status!=CUDA_SUCCESS)ada_gate_fail("ADA_NN_DTOH_RETURN_STATUS");
  auto x=ada_nn_output_stack.back();ada_nn_output_stack.pop_back();
  if(ctx!=x.ctx||p->dstHost!=x.host||p->srcDevice!=x.source||p->ByteCount!=x.bytes||syscall(SYS_gettid)!=x.tid)ada_gate_fail("ADA_NN_DTOH_CALLBACK_PAIR");
  unsigned char digest[SHA256_DIGEST_LENGTH];SHA256(static_cast<const unsigned char*>(x.host),x.bytes,digest);
  std::string path=user_folder+"/traces/nn-output-1.bin";ada_nn_write(path,x.host,x.bytes);
  std::ostringstream line;line<<"OUTPUT_SUCCESS\t1\t"<<api<<"\t"<<std::hex<<(uintptr_t)ctx<<"\t"<<x.source<<"\t"<<(uintptr_t)x.host<<std::dec<<"\t"<<x.bytes<<"\t"<<ada_hex_digest(digest)<<"\t"<<x.tid<<"\t"<<ada_gate_ns()<<"\tSYNC_SUCCESS_RETURN_HOST_BYTES_NOT_ADDED_DEVICE_READBACK\n";
  auto text=line.str();ada_nn_write(user_folder+"/traces/ada-nn-output.tsv",text.data(),text.size());++ada_nn_output_count;
 }
}
static void ada_nn_output_end(){if(ada_nn_output_count!=1||!ada_nn_output_stack.empty())ada_gate_fail("ADA_NN_OUTPUT_NOT_CLOSED");}
