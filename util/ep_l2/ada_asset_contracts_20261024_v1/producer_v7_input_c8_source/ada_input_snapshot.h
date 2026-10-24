#include <sys/syscall.h>
#include <iomanip>
#include <openssl/sha.h>
#include <mutex>
#include <sys/statvfs.h>
#include <array>
struct AdaInputCopy { uint64_t id=0; CUcontext context=nullptr; CUdeviceptr dst=0; const void*src=nullptr; size_t bytes=0; CUstream stream=nullptr; bool async=false;std::string path,digest,api; };
static std::mutex ada_input_mutex;
static uint64_t ada_input_next=0,ada_input_total=0;
static long ada_input_thread=-1;
static std::vector<AdaInputCopy> ada_input_pending;
static void ada_input_complete(CUcontext ctx,CUstream stream,bool whole_context,const char*boundary){
 std::lock_guard<std::mutex>g(ada_input_mutex);
 for(auto it=ada_input_pending.begin();it!=ada_input_pending.end();) {
  if(it->context==ctx&&(whole_context||it->stream==stream)) {
   std::ofstream log(user_folder+"/traces/ada-input.tsv",std::ios::app);log<<"COMPLETE\t"<<it->id<<"\t"<<boundary<<"\t"<<it->bytes<<"\t"<<it->digest<<"\tHOST_BYTES_FROZEN_AND_EXISTING_GPU_COMPLETION_BOUNDARY\n";it=ada_input_pending.erase(it);
  }else ++it;
 }
}

static thread_local std::vector<AdaInputCopy> ada_input_stack;
static std::string ada_hex_digest(const unsigned char *digest) { std::ostringstream s;s<<std::hex<<std::setfill('0');for(int i=0;i<SHA256_DIGEST_LENGTH;i++)s<<std::setw(2)<<unsigned(digest[i]);return s.str(); }
static void ada_input_fail(const char *reason){fprintf(stderr,"%s\n",reason);abort();}
static void ada_input_event(CUcontext ctx,int is_exit,const char*name,void*params,CUresult*status) {
 if(!getenv("ADA_INPUT_SNAPSHOT"))return;
 if(is_exit&&status&&*status==CUDA_SUCCESS){if(std::string(name)=="cuCtxSynchronize")ada_input_complete(ctx,nullptr,true,"EXISTING_APPLICATION_CTX_SYNC");else if(std::string(name)=="cuStreamSynchronize"||std::string(name)=="cuStreamSynchronize_ptsz")ada_input_complete(ctx,((cuStreamSynchronize_params*)params)->hStream,false,"EXISTING_APPLICATION_STREAM_SYNC");}
 const std::string api(name);bool async=api=="cuMemcpyHtoDAsync_v2"||api=="cuMemcpyHtoDAsync_v2_ptsz";
 bool sync=api=="cuMemcpyHtoD_v2"||api=="cuMemcpyHtoD_v2_ptds";
 if(!async&&!sync) {
  if(api.find("cuMemcpy")!=std::string::npos && api.find("DtoH")==std::string::npos && api.find("DtoD")==std::string::npos)ada_input_fail("ADA_INPUT_UNSUPPORTED_COPY_API");
  return;
 }
 if(!is_exit) {
  AdaInputCopy c;c.api=api;c.context=ctx;c.async=async;
  if(async){auto*p=(cuMemcpyHtoDAsync_v2_params*)params;c.dst=p->dstDevice;c.src=p->srcHost;c.bytes=p->ByteCount;c.stream=p->hStream;}
  else {auto*p=(cuMemcpyHtoD_v2_params*)params;c.dst=p->dstDevice;c.src=p->srcHost;c.bytes=p->ByteCount;}
  {
   std::lock_guard<std::mutex> guard(ada_input_mutex);long tid=syscall(SYS_gettid);
   if(ada_input_thread<0)ada_input_thread=tid;if(ada_input_thread!=tid)ada_input_fail("ADA_INPUT_MULTI_HOST_THREAD_UNSUPPORTED");
   uint64_t per=getenv("ADA_INPUT_MAX_COPY_BYTES")?std::stoull(getenv("ADA_INPUT_MAX_COPY_BYTES")):8ull*1024*1024;
   uint64_t total=getenv("ADA_INPUT_MAX_TOTAL_BYTES")?std::stoull(getenv("ADA_INPUT_MAX_TOTAL_BYTES")):32ull*1024*1024;
   if(c.bytes>per||c.bytes>total||ada_input_total>total-c.bytes)ada_input_fail("ADA_INPUT_CAP_EXCEEDED_BEFORE_COPY");
   struct statvfs space;if(statvfs(user_folder.c_str(),&space)||uint64_t(space.f_bavail)*space.f_frsize<5ull*1024*1024*1024+c.bytes)ada_input_fail("ADA_INPUT_SPACE_FLOOR");
   c.id=++ada_input_next;ada_input_total+=c.bytes;
  }
  std::string dir=user_folder+"/traces/inputs";if(mkdir(dir.c_str(),0700)&&errno!=EEXIST)ada_input_fail("ADA_INPUT_MKDIR_FAILED");
  std::ostringstream path;path<<dir<<"/copy_"<<std::setw(6)<<std::setfill('0')<<c.id<<".bin";c.path=path.str();
  FILE*f=fopen(c.path.c_str(),"wbx");if(!f)ada_input_fail("ADA_INPUT_EXCLUSIVE_OPEN_FAILED");
  SHA256_CTX hash;SHA256_Init(&hash);const unsigned char*source=(const unsigned char*)c.src;
  for(size_t off=0;off<c.bytes;){size_t n=std::min(size_t(1024*1024),c.bytes-off);if(fwrite(source+off,1,n,f)!=n)ada_input_fail("ADA_INPUT_WRITE_FAILED");SHA256_Update(&hash,source+off,n);off+=n;}
  unsigned char digest[SHA256_DIGEST_LENGTH];SHA256_Final(digest,&hash);c.digest=ada_hex_digest(digest);
  if(fflush(f)||fsync(fileno(f))||fclose(f))ada_input_fail("ADA_INPUT_CLOSE_FAILED");
  {std::ofstream log(user_folder+"/traces/ada-input.tsv",std::ios::app);log<<"ENTRY\t"<<c.id<<"\t"<<c.api<<"\t"<<std::hex<<(uintptr_t)c.context<<"\t"<<(uintptr_t)c.stream<<"\t"<<c.dst<<"\t"<<(uintptr_t)c.src<<"\t"<<std::dec<<c.bytes<<"\t"<<c.digest<<"\t"<<c.path<<"\n";}
  ada_input_stack.push_back(c);
 } else {
  if(ada_input_stack.empty())ada_input_fail("ADA_INPUT_EXIT_WITHOUT_ENTRY");
  AdaInputCopy c=ada_input_stack.back();ada_input_stack.pop_back();if(c.context!=ctx||c.api!=api)ada_input_fail("ADA_INPUT_API_PAIR_MISMATCH");
  {std::ofstream log(user_folder+"/traces/ada-input.tsv",std::ios::app);log<<"API_EXIT\t"<<c.id<<"\t"<<(status?int(*status):-999)<<"\n";}
  if(!status||*status!=CUDA_SUCCESS)ada_input_fail("ADA_INPUT_COPY_API_FAILURE");
  // Source-byte observation only; no driver GPU call is made from the early API callback.
  FILE*f=fopen(c.path.c_str(),"rb");if(!f)ada_input_fail("ADA_INPUT_REOPEN_FAILED");
  std::array<unsigned char,65536> expected;SHA256_CTX hash;SHA256_Init(&hash);
  for(size_t off=0;off<c.bytes;) {
   size_t n=std::min(expected.size(),c.bytes-off);if(fread(expected.data(),1,n,f)!=n)ada_input_fail("ADA_INPUT_TRUNCATED_CAPSULE");
   if(memcmp(expected.data(),(const unsigned char*)c.src+off,n))ada_input_fail("ADA_INPUT_HOST_SOURCE_CHANGED_DURING_API");
   SHA256_Update(&hash,expected.data(),n);off+=n;
  }
  if(fgetc(f)!=EOF||fclose(f))ada_input_fail("ADA_INPUT_TRAILING_OR_CLOSE_ERROR");
  unsigned char digest[SHA256_DIGEST_LENGTH];SHA256_Final(digest,&hash);if(ada_hex_digest(digest)!=c.digest)ada_input_fail("ADA_INPUT_REOPEN_HASH_MISMATCH");
  if(c.async){std::lock_guard<std::mutex>g(ada_input_mutex);ada_input_pending.push_back(c);}
  else {std::ofstream log(user_folder+"/traces/ada-input.tsv",std::ios::app);log<<"COMPLETE\t"<<c.id<<"\tSYNC_API_SUCCESS_SOURCE_BYTES_FROZEN\t"<<c.bytes<<"\t"<<c.digest<<"\tHOST_BYTES_EQUAL_CLOSED_CAPSULE_NOT_DEVICE_READBACK\n";}

 }
}
