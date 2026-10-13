#include <cuda.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include <type_traits>
#include <cstddef>
#include <cstdint>
static_assert(std::is_same<decltype(&cuStreamGetCtx_v2),CUresult(CUDAAPI*)(CUstream,CUcontext*,CUgreenCtx*)>::value,"Stream ABI signature");
static_assert(std::is_same<decltype(&cuGreenCtxGetDevResource),CUresult(CUDAAPI*)(CUgreenCtx,CUdevResource*,CUdevResourceType)>::value,"Resource ABI signature");
static_assert(sizeof(CUdevResource)==144 && offsetof(CUdevResource,sm)==96,"Frozen CUDA12.6 resource ABI1 layout");
struct Call{std::string name;int rc;std::string error;};std::vector<Call> calls;
bool call(const char* n,CUresult rc){const char* e=nullptr;cuGetErrorName(rc,&e);calls.push_back({n,(int)rc,e?e:"UNKNOWN"});return rc==CUDA_SUCCESS;}
#define TRY(name,expr) do {if(!call(name,expr))throw std::string(name);}while(0)
template<typename T> unsigned long long handle(T x){return (unsigned long long)(uintptr_t)x;}
int main(int argc,char**argv){
 if(argc!=2)return 64;
 CUdevice dev=0;CUdevResource whole{},part{},remaining{},quota{},active_resource{};CUdevResourceDesc desc=nullptr;CUgreenCtx green=nullptr,queriedGreen=nullptr,afterGreen=nullptr;CUstream stream=nullptr;CUcontext original=nullptr,normalCtx=nullptr,converted=nullptr,current=nullptr,popped=nullptr,restored=nullptr,afterNormal=nullptr;CUmodule module=nullptr;CUfunction kernel=nullptr;CUdeviceptr memory=0;void* host=nullptr;
 bool pushed=false,g1=false,g2=false,owner_equal=false,post_owner_equal=false,context_restored=false,cleanup_ok=true;int physical=0,major=0,minor=0,version=0;unsigned int request=0,groups=1,N=256;std::string stage="G1",error="";std::vector<unsigned int> output;
 try{
  TRY("cuInit",cuInit(0));TRY("cuDriverGetVersion",cuDriverGetVersion(&version));TRY("cuCtxGetCurrent.original",cuCtxGetCurrent(&original));TRY("cuDeviceGet",cuDeviceGet(&dev,0));TRY("cuDeviceGetAttribute.SM_COUNT",cuDeviceGetAttribute(&physical,CU_DEVICE_ATTRIBUTE_MULTIPROCESSOR_COUNT,dev));TRY("cuDeviceGetAttribute.CC_MAJOR",cuDeviceGetAttribute(&major,CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MAJOR,dev));TRY("cuDeviceGetAttribute.CC_MINOR",cuDeviceGetAttribute(&minor,CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MINOR,dev));
  if(major!=8||minor!=9)throw std::string("DEVICE_IDENTITY_STOP");TRY("cuDeviceGetDevResource",cuDeviceGetDevResource(dev,&whole,CU_DEV_RESOURCE_TYPE_SM));if(whole.sm.smCount!=(unsigned)physical)throw std::string("DEVICE_RESOURCE_IDENTITY_STOP");
  request=((whole.sm.smCount+1)/2+1)/2*2;if(request<4)request=4;
  TRY("cuDevSmResourceSplitByCount.single_candidate",cuDevSmResourceSplitByCount(&part,&groups,&whole,&remaining,0,request));if(groups!=1||part.sm.smCount==0||part.sm.smCount>=whole.sm.smCount)throw std::string("INVALID_ACTUAL_QUOTA");
  TRY("cuDevResourceGenerateDesc",cuDevResourceGenerateDesc(&desc,&part,1));TRY("cuGreenCtxCreate",cuGreenCtxCreate(&green,desc,dev,CU_GREEN_CTX_DEFAULT_STREAM));TRY("cuGreenCtxStreamCreate",cuGreenCtxStreamCreate(&stream,green,CU_STREAM_NON_BLOCKING,0));
  TRY("cuStreamGetCtx_v2",cuStreamGetCtx_v2(stream,&normalCtx,&queriedGreen));owner_equal=queriedGreen==green;if(!owner_equal)throw std::string("STREAM_GREEN_HANDLE_MISMATCH");TRY("cuGreenCtxGetDevResource.queried_owner",cuGreenCtxGetDevResource(queriedGreen,&quota,CU_DEV_RESOURCE_TYPE_SM));if(quota.sm.smCount!=part.sm.smCount)throw std::string("STREAM_BOUND_RESOURCE_MISMATCH");g1=true;
  stage="G2";TRY("cuCtxFromGreenCtx",cuCtxFromGreenCtx(&converted,green));TRY("cuCtxPushCurrent",cuCtxPushCurrent(converted));pushed=true;TRY("cuCtxGetCurrent.active",cuCtxGetCurrent(&current));if(current!=converted)throw std::string("CURRENT_CONTEXT_MISMATCH");TRY("cuCtxGetDevResource.active",cuCtxGetDevResource(current,&active_resource,CU_DEV_RESOURCE_TYPE_SM));if(active_resource.sm.smCount!=quota.sm.smCount)throw std::string("CURRENT_RESOURCE_MISMATCH");
  TRY("cuModuleLoad.local_precompiled_cubin",cuModuleLoad(&module,argv[1]));TRY("cuModuleGetFunction",cuModuleGetFunction(&kernel,module,"a16r1_integer_canary"));TRY("cuMemAlloc.owned",cuMemAlloc(&memory,N*sizeof(unsigned int)));TRY("cuMemAllocHost.owned",cuMemAllocHost(&host,N*sizeof(unsigned int)));void* args[]={&memory,&N};
  TRY("cuLaunchKernel.green_stream.single",cuLaunchKernel(kernel,2,1,1,128,1,1,0,stream,args,nullptr));TRY("cuMemcpyDtoHAsync.green_stream",cuMemcpyDtoHAsync(host,memory,N*sizeof(unsigned int),stream));TRY("cuStreamSynchronize.output_ready",cuStreamSynchronize(stream));output.assign((unsigned int*)host,(unsigned int*)host+N);
  for(unsigned int i=0;i<N;++i)if(output[i]!=3*i+11)throw std::string("KERNEL_OUTPUT_MISMATCH");TRY("cuStreamGetCtx_v2.after_kernel",cuStreamGetCtx_v2(stream,&afterNormal,&afterGreen));post_owner_equal=afterGreen==green;if(!post_owner_equal)throw std::string("POST_KERNEL_OWNER_MISMATCH");g2=true;stage="COMPLETE_G1_G2";
 }catch(const std::string& e){error=e;}
 // Only self-owned objects are cleaned. No primary-context reset/destruction.
 if(stream&&!pushed&&green){if(call("cleanup.cuCtxFromGreenCtx",cuCtxFromGreenCtx(&converted,green))&&call("cleanup.cuCtxPushCurrent",cuCtxPushCurrent(converted)))pushed=true;else cleanup_ok=false;}
 if(stream)cleanup_ok=call("cleanup.cuStreamSynchronize",cuStreamSynchronize(stream))&&cleanup_ok;
 if(memory)cleanup_ok=call("cleanup.cuMemFree.owned",cuMemFree(memory))&&cleanup_ok;
 if(host)cleanup_ok=call("cleanup.cuMemFreeHost.owned",cuMemFreeHost(host))&&cleanup_ok;
 if(module)cleanup_ok=call("cleanup.cuModuleUnload.owned",cuModuleUnload(module))&&cleanup_ok;
 if(stream)cleanup_ok=call("cleanup.cuStreamDestroy.owned",cuStreamDestroy(stream))&&cleanup_ok;
 if(pushed){cleanup_ok=call("cleanup.cuCtxPopCurrent",cuCtxPopCurrent(&popped))&&cleanup_ok;if(popped!=converted)cleanup_ok=false;}
 cleanup_ok=call("cleanup.cuCtxGetCurrent.restored",cuCtxGetCurrent(&restored))&&cleanup_ok;context_restored=restored==original;if(!context_restored)cleanup_ok=false;
 if(green)cleanup_ok=call("cleanup.cuGreenCtxDestroy.owned",cuGreenCtxDestroy(green))&&cleanup_ok;
 std::cout<<"{\"status\":\""<<(g1&&g2&&cleanup_ok?"PASS_G1_G2":("STOP_"+stage))<<"\",\"error\":\""<<error<<"\",\"G1\":\""<<(g1?"PASS":"STOP")<<"\",\"G2\":\""<<(g2?"PASS":g1?"STOP":"NOT_RUN_G1_STOP")<<"\",\"header_CUDA_VERSION\":"<<CUDA_VERSION<<",\"driver_version\":"<<version<<",\"resource_ABI_size\":"<<sizeof(CUdevResource)<<",\"resource_SM_offset\":"<<offsetof(CUdevResource,sm)<<",\"physical_SM_count\":"<<physical<<",\"requested_minimum_SM_count\":"<<request<<",\"partition_actual_SM_count\":"<<part.sm.smCount<<",\"stream_bound_actual_SM_count\":"<<(g1?std::to_string(quota.sm.smCount):"null")<<",\"split_flags\":0,\"split_candidates\":1,\"groups_returned\":"<<groups<<",\"green_handle\":"<<handle(green)<<",\"green_stream\":"<<handle(stream)<<",\"queried_green_handle\":"<<handle(queriedGreen)<<",\"normal_primary_context\":"<<handle(normalCtx)<<",\"converted_context\":"<<handle(converted)<<",\"original_context\":"<<handle(original)<<",\"restored_context\":"<<handle(restored)<<",\"owner_handle_equal\":"<<(owner_equal?"true":"false")<<",\"post_kernel_owner_equal\":"<<(post_owner_equal?"true":"false")<<",\"previous_context_restored\":"<<(context_restored?"true":"false")<<",\"cleanup_success\":"<<(cleanup_ok?"true":"false")<<",\"kernel_launches\":"<<(output.empty()?0:1)<<",\"kernel_output\":[";
 for(size_t i=0;i<output.size();++i){if(i)std::cout<<",";std::cout<<output[i];}std::cout<<"],\"calls\":[";for(size_t i=0;i<calls.size();++i){if(i)std::cout<<",";std::cout<<"{\"name\":\""<<calls[i].name<<"\",\"return_code\":"<<calls[i].rc<<",\"error_name\":\""<<calls[i].error<<"\"}";}std::cout<<"]}"<<std::endl;return g1&&g2&&cleanup_ok?0:2;
}
