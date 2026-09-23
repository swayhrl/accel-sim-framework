#include <cuda_runtime_api.h>

#include <cstddef>
#include <cstdint>
#include <cstring>

extern "C" {

struct C16CudaCapability {
  int runtime_version;
  int driver_version;
  int device_ordinal;
  int l2_bytes;
  int max_persisting_l2_bytes;
  int max_access_policy_window_bytes;
  char device_name[256];
};

int c16_query_capability(int device, C16CudaCapability* output) {
  if (output == nullptr) return static_cast<int>(cudaErrorInvalidValue);
  std::memset(output, 0, sizeof(*output));
  output->device_ordinal = device;
  cudaError_t status = cudaRuntimeGetVersion(&output->runtime_version);
  if (status != cudaSuccess) return static_cast<int>(status);
  status = cudaDriverGetVersion(&output->driver_version);
  if (status != cudaSuccess) return static_cast<int>(status);
  cudaDeviceProp properties{};
  status = cudaGetDeviceProperties(&properties, device);
  if (status != cudaSuccess) return static_cast<int>(status);
  std::strncpy(output->device_name, properties.name, sizeof(output->device_name) - 1);
  status = cudaDeviceGetAttribute(&output->l2_bytes, cudaDevAttrL2CacheSize, device);
  if (status != cudaSuccess) return static_cast<int>(status);
  status = cudaDeviceGetAttribute(&output->max_persisting_l2_bytes, cudaDevAttrMaxPersistingL2CacheSize, device);
  if (status != cudaSuccess) return static_cast<int>(status);
  status = cudaDeviceGetAttribute(&output->max_access_policy_window_bytes, cudaDevAttrMaxAccessPolicyWindowSize, device);
  return static_cast<int>(status);
}

int c16_set_persisting_limit(std::size_t bytes) {
  return static_cast<int>(cudaDeviceSetLimit(cudaLimitPersistingL2CacheSize, bytes));
}

int c16_get_persisting_limit(std::size_t* bytes) {
  return static_cast<int>(cudaDeviceGetLimit(bytes, cudaLimitPersistingL2CacheSize));
}

int c16_reset_persisting_l2() {
  return static_cast<int>(cudaCtxResetPersistingL2Cache());
}

int c16_set_access_policy(std::uintptr_t stream_value,
                          std::uintptr_t base_pointer,
                          std::size_t num_bytes,
                          float hit_ratio,
                          int miss_is_streaming) {
  cudaStreamAttrValue attribute{};
  attribute.accessPolicyWindow.base_ptr = reinterpret_cast<void*>(base_pointer);
  attribute.accessPolicyWindow.num_bytes = num_bytes;
  attribute.accessPolicyWindow.hitRatio = hit_ratio;
  attribute.accessPolicyWindow.hitProp = cudaAccessPropertyPersisting;
  attribute.accessPolicyWindow.missProp = miss_is_streaming ? cudaAccessPropertyStreaming : cudaAccessPropertyNormal;
  auto stream = reinterpret_cast<cudaStream_t>(stream_value);
  return static_cast<int>(cudaStreamSetAttribute(stream, cudaStreamAttributeAccessPolicyWindow, &attribute));
}

int c16_set_access_policy_mode(std::uintptr_t stream_value,
                               std::uintptr_t base_pointer,
                               std::size_t num_bytes,
                               float hit_ratio,
                               int hit_mode,
                               int miss_mode) {
  auto decode_property = [](int mode) {
    if (mode == 2) return cudaAccessPropertyPersisting;
    if (mode == 1) return cudaAccessPropertyStreaming;
    return cudaAccessPropertyNormal;
  };
  cudaStreamAttrValue attribute{};
  attribute.accessPolicyWindow.base_ptr = reinterpret_cast<void*>(base_pointer);
  attribute.accessPolicyWindow.num_bytes = num_bytes;
  attribute.accessPolicyWindow.hitRatio = hit_ratio;
  attribute.accessPolicyWindow.hitProp = decode_property(hit_mode);
  attribute.accessPolicyWindow.missProp = decode_property(miss_mode);
  auto stream = reinterpret_cast<cudaStream_t>(stream_value);
  return static_cast<int>(cudaStreamSetAttribute(stream, cudaStreamAttributeAccessPolicyWindow, &attribute));
}

int c16_clear_access_policy(std::uintptr_t stream_value) {
  cudaStreamAttrValue attribute{};
  attribute.accessPolicyWindow.base_ptr = nullptr;
  attribute.accessPolicyWindow.num_bytes = 0;
  attribute.accessPolicyWindow.hitRatio = 0.0f;
  attribute.accessPolicyWindow.hitProp = cudaAccessPropertyNormal;
  attribute.accessPolicyWindow.missProp = cudaAccessPropertyNormal;
  auto stream = reinterpret_cast<cudaStream_t>(stream_value);
  return static_cast<int>(cudaStreamSetAttribute(stream, cudaStreamAttributeAccessPolicyWindow, &attribute));
}

const char* c16_cuda_error_string(int status) {
  return cudaGetErrorString(static_cast<cudaError_t>(status));
}

}
