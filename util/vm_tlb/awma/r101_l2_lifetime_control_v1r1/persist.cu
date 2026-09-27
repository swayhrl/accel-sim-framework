#include <cuda_runtime.h>
#include <cstdint>
#include <vector>

// Existing CUDA runtime controls only. No arithmetic or custom cache mechanism.
extern "C" int r101r1_set_persisting_limit(unsigned long long requested,
                                             unsigned long long* actual) {
    cudaDeviceProp prop{};
    cudaError_t status = cudaGetDeviceProperties(&prop, 0);
    if (status != cudaSuccess) return static_cast<int>(status);
    if (requested == 0 || requested > static_cast<unsigned long long>(prop.persistingL2CacheMaxSize))
        return -1;
    status = cudaDeviceSetLimit(cudaLimitPersistingL2CacheSize,
                                static_cast<std::size_t>(requested));
    if (status != cudaSuccess) return static_cast<int>(status);
    std::size_t got = 0;
    status = cudaDeviceGetLimit(&got, cudaLimitPersistingL2CacheSize);
    if (status != cudaSuccess) return static_cast<int>(status);
    *actual = static_cast<unsigned long long>(got);
    return got >= requested ? 0 : -2;
}

extern "C" int r101r1_attach_persisting_to_active_capture(
    unsigned long long stream_value, void* base, unsigned long long bytes,
    unsigned int* modified_kernel_nodes) {
    if (!base || !modified_kernel_nodes || bytes == 0 ||
        reinterpret_cast<std::uintptr_t>(base) % 128U != 0 || bytes % 128ULL != 0)
        return -1;
    cudaDeviceProp prop{};
    cudaError_t status = cudaGetDeviceProperties(&prop, 0);
    if (status != cudaSuccess) return static_cast<int>(status);
    if (bytes > static_cast<unsigned long long>(prop.accessPolicyMaxWindowSize)) return -2;
    cudaStream_t stream = reinterpret_cast<cudaStream_t>(stream_value);
    cudaStreamCaptureStatus capture_status{};
    unsigned long long capture_id = 0;
    cudaGraph_t graph = nullptr;
    status = cudaStreamGetCaptureInfo_v2(stream, &capture_status, &capture_id,
                                         &graph, nullptr, nullptr);
    if (status != cudaSuccess) return static_cast<int>(status);
    if (capture_status != cudaStreamCaptureStatusActive || !graph) return -3;
    std::size_t count = 0;
    status = cudaGraphGetNodes(graph, nullptr, &count);
    if (status != cudaSuccess) return static_cast<int>(status);
    std::vector<cudaGraphNode_t> nodes(count);
    status = cudaGraphGetNodes(graph, nodes.data(), &count);
    if (status != cudaSuccess) return static_cast<int>(status);
    cudaKernelNodeAttrValue attr{};
    attr.accessPolicyWindow.base_ptr = base;
    attr.accessPolicyWindow.num_bytes = static_cast<std::size_t>(bytes);
    attr.accessPolicyWindow.hitRatio = 1.0f;
    attr.accessPolicyWindow.hitProp = cudaAccessPropertyPersisting;
    attr.accessPolicyWindow.missProp = cudaAccessPropertyNormal;
    unsigned int applied = 0;
    for (cudaGraphNode_t node : nodes) {
        cudaGraphNodeType type{};
        status = cudaGraphNodeGetType(node, &type);
        if (status != cudaSuccess) return static_cast<int>(status);
        if (type != cudaGraphNodeTypeKernel) continue;
        status = cudaGraphKernelNodeSetAttribute(
            node, cudaKernelNodeAttributeAccessPolicyWindow, &attr);
        if (status != cudaSuccess) return static_cast<int>(status);
        cudaKernelNodeAttrValue observed{};
        status = cudaGraphKernelNodeGetAttribute(
            node, cudaKernelNodeAttributeAccessPolicyWindow, &observed);
        if (status != cudaSuccess) return static_cast<int>(status);
        if (observed.accessPolicyWindow.base_ptr != base ||
            observed.accessPolicyWindow.num_bytes != static_cast<std::size_t>(bytes) ||
            observed.accessPolicyWindow.hitRatio != 1.0f ||
            observed.accessPolicyWindow.hitProp != cudaAccessPropertyPersisting ||
            observed.accessPolicyWindow.missProp != cudaAccessPropertyNormal)
            return -5;
        ++applied;
    }
    *modified_kernel_nodes = applied;
    return applied > 0 ? 0 : -4;
}

extern "C" int r101r1_reset_persisting_lines() {
    return static_cast<int>(cudaCtxResetPersistingL2Cache());
}
