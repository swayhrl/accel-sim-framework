#include <cuda.h>
#include <iostream>
#include <vector>
#include <string>
struct Call { std::string name; int rc; std::string error; };
std::vector<Call> calls;
bool check(const char* name, CUresult rc) {
 const char* error=nullptr;cuGetErrorName(rc,&error);calls.push_back({name,(int)rc,error?error:"UNKNOWN"});return rc==CUDA_SUCCESS;
}
int main() {
 int version=0, sm=0, major=0,minor=0,lookup_status=-1;CUdevice device=0;CUdevResource resource{};void* fn=nullptr;bool init=false,device_ok=false,resource_ok=false;std::string state="PRECONDITION_STOP";
 init=check("cuInit",cuInit(0));
 if(init && check("cuDriverGetVersion",cuDriverGetVersion(&version)) && check("cuDeviceGet",cuDeviceGet(&device,0))) {
  device_ok=check("cuDeviceGetAttribute.SM_COUNT",cuDeviceGetAttribute(&sm,CU_DEVICE_ATTRIBUTE_MULTIPROCESSOR_COUNT,device)) && check("cuDeviceGetAttribute.CC_MAJOR",cuDeviceGetAttribute(&major,CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MAJOR,device)) && check("cuDeviceGetAttribute.CC_MINOR",cuDeviceGetAttribute(&minor,CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MINOR,device));
  if(device_ok)resource_ok=check("cuDeviceGetDevResource",cuDeviceGetDevResource(device,&resource,CU_DEV_RESOURCE_TYPE_SM));
  CUdriverProcAddressQueryResult status=CU_GET_PROC_ADDRESS_SYMBOL_NOT_FOUND;
  bool lookup_ok=check("cuGetProcAddress.cuStreamGetDevResource",cuGetProcAddress("cuStreamGetDevResource",&fn,CUDA_VERSION,CU_GET_PROC_ADDRESS_DEFAULT,&status));lookup_status=(int)status;
  state=(!lookup_ok || fn==nullptr || status!=CU_GET_PROC_ADDRESS_SUCCESS)?"STOP_REQUIRED_STREAM_RESOURCE_ENTRYPOINT_UNAVAILABLE":"STOP_REQUIRED_ENTRYPOINT_NOT_DECLARED_IN_FROZEN_HEADER";
 }
 // The required named entrypoint was not safely invocable. Do not construct a substitute
 // stream/context quota proof, allocate a partition, launch a kernel, or advance downstream.
 std::cout<<"{\"stage\":\"G1\",\"status\":\""<<state<<"\",\"header_CUDA_VERSION\":"<<CUDA_VERSION<<",\"driver_version\":"<<version<<",\"physical_device_sm_count\":"<<sm<<",\"device_resource_sm_count\":"<<(resource_ok?std::to_string(resource.sm.smCount):"null")<<",\"compute_capability_major\":"<<major<<",\"compute_capability_minor\":"<<minor<<",\"required_symbol_lookup_status\":"<<lookup_status<<",\"required_symbol_nonnull\":"<<(fn?"true":"false")<<",\"actual_green_quota_sm_count\":null,\"quota_partition_attempts\":0,\"green_contexts_created\":0,\"green_streams_created\":0,\"kernel_launches\":0,\"formal_timing_samples\":0,\"calls\":[";
 for(size_t i=0;i<calls.size();++i){if(i)std::cout<<",";std::cout<<"{\"name\":\""<<calls[i].name<<"\",\"return_code\":"<<calls[i].rc<<",\"error_name\":\""<<calls[i].error<<"\"}";}
 std::cout<<"]}"<<std::endl;return 2;
}
