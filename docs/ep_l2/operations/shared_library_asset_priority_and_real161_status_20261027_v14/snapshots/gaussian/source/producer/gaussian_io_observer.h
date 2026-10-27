#pragma once
struct GaussianOutputCopy { CUcontext ctx; CUdeviceptr src; void*dst; size_t bytes; std::string api; uint64_t id; };
static thread_local std::vector<GaussianOutputCopy> gaussian_output_stack;
static uint64_t gaussian_output_next=0,gaussian_output_total=0;
static void gaussian_output_event(CUcontext ctx,int is_exit,const char*name,void*params,CUresult*status){
 std::string api(name);
 if(api.find("DtoH")!=std::string::npos&&api!="cuMemcpyDtoH_v2"&&api!="cuMemcpyDtoH_v2_ptds")ada_input_fail("GAUSSIAN_OUTPUT_UNSUPPORTED_ASYNC_OR_COPY_API");
 if(api!="cuMemcpyDtoH_v2"&&api!="cuMemcpyDtoH_v2_ptds")return;
 if(!is_exit){
  auto*p=(cuMemcpyDtoH_v2_params*)params;GaussianOutputCopy c{ctx,p->srcDevice,p->dstHost,p->ByteCount,api,++gaussian_output_next};
  if(c.bytes>8ull*1024*1024||gaussian_output_total>32ull*1024*1024-c.bytes)ada_input_fail("GAUSSIAN_OUTPUT_CAP");
  gaussian_output_total+=c.bytes;gaussian_output_stack.push_back(c);
  std::ofstream l(user_folder+"/traces/ada-output.tsv",std::ios::app);l<<"ENTRY\t"<<c.id<<"\t"<<api<<"\t"<<std::hex<<(uintptr_t)ctx<<"\t"<<c.src<<"\t"<<(uintptr_t)c.dst<<"\t"<<std::dec<<c.bytes<<"\n";
 }else{
  if(gaussian_output_stack.empty())ada_input_fail("GAUSSIAN_OUTPUT_EXIT_WITHOUT_ENTRY");
  auto c=gaussian_output_stack.back();gaussian_output_stack.pop_back();
  if(c.ctx!=ctx||c.api!=api||!status||*status!=CUDA_SUCCESS)ada_input_fail("GAUSSIAN_OUTPUT_FAILED_OR_UNPAIRED_API");
  std::string dir=user_folder+"/traces/outputs";if(mkdir(dir.c_str(),0700)&&errno!=EEXIST)ada_input_fail("GAUSSIAN_OUTPUT_MKDIR");
  std::ostringstream p;p<<dir<<"/copy_"<<std::setw(6)<<std::setfill('0')<<c.id<<".bin";
  struct statvfs space;if(statvfs(user_folder.c_str(),&space)||uint64_t(space.f_bavail)*space.f_frsize<5ull*1024*1024*1024+c.bytes)ada_input_fail("GAUSSIAN_OUTPUT_SPACE_FLOOR");
  FILE*f=fopen(p.str().c_str(),"wbx");if(!f)ada_input_fail("GAUSSIAN_OUTPUT_EXCLUSIVE_OPEN");
  SHA256_CTX h;SHA256_Init(&h);
  for(size_t off=0;off<c.bytes;){size_t n=std::min(size_t(65536),c.bytes-off);if(fwrite((const unsigned char*)c.dst+off,1,n,f)!=n)ada_input_fail("GAUSSIAN_OUTPUT_WRITE");SHA256_Update(&h,(const unsigned char*)c.dst+off,n);off+=n;}
  unsigned char digest[SHA256_DIGEST_LENGTH];SHA256_Final(digest,&h);auto expected=ada_hex_digest(digest);
  if(fflush(f)||fsync(fileno(f))||fclose(f))ada_input_fail("GAUSSIAN_OUTPUT_CLOSE");
  if(gaussian16::file_sha(p.str())!=expected)ada_input_fail("GAUSSIAN_OUTPUT_CLOSED_REOPEN_SHA");
  std::ofstream l(user_folder+"/traces/ada-output.tsv",std::ios::app);l<<"COMPLETE\t"<<c.id<<"\t"<<api<<"\t"<<std::hex<<(uintptr_t)ctx<<"\t"<<c.src<<"\t"<<std::dec<<c.bytes<<"\t"<<expected<<"\t"<<p.str()<<"\tSYNC_DTOH_API_SUCCESS_ACTUAL_HOST_BYTES\n";
 }
}
static void gaussian_lifecycle_event(CUcontext ctx,int is_exit,const char*name,void*params,CUresult*status){
 std::string api(name);if(api!="cuMemAlloc_v2"&&api!="cuMemFree_v2")return;
 if(!is_exit)return;if(!status||*status!=CUDA_SUCCESS)ada_input_fail("GAUSSIAN_ALLOCATION_API_FAILURE");
 std::ofstream l(user_folder+"/traces/ada-allocation.tsv",std::ios::app);
 if(api=="cuMemAlloc_v2"){auto*p=(cuMemAlloc_v2_params*)params;l<<"ALLOC\t"<<std::hex<<(uintptr_t)ctx<<"\t"<<*p->dptr<<"\t"<<std::dec<<p->bytesize<<"\tCUDA_SUCCESS\n";}
 else {auto*p=(cuMemFree_v2_params*)params;l<<"FREE\t"<<std::hex<<(uintptr_t)ctx<<"\t"<<p->dptr<<"\tCUDA_SUCCESS\n";}
}
static void gaussian_io_finish(CUcontext ctx){
 if(!ada_input_pending.empty()||!ada_input_stack.empty()||!gaussian_output_stack.empty())ada_input_fail("GAUSSIAN_IO_UNCLOSED_LIFECYCLE");
 std::ofstream i(user_folder+"/traces/ada-input.tsv",std::ios::app);i<<"EOF\t"<<ada_input_next<<"\t"<<ada_input_total<<"\t"<<std::hex<<(uintptr_t)ctx<<"\n";
 std::ofstream o(user_folder+"/traces/ada-output.tsv",std::ios::app);o<<"EOF\t"<<std::dec<<gaussian_output_next<<"\t"<<gaussian_output_total<<"\t"<<std::hex<<(uintptr_t)ctx<<"\n";
}
