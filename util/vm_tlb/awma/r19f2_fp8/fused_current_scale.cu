#include <ATen/cuda/CUDAContext.h>
#include <c10/cuda/CUDAException.h>
#include <cooperative_groups.h>
#include <cuda_bf16.h>
#include <cuda_fp8.h>
#include <cuda_runtime.h>
#include <torch/extension.h>

#include <cfloat>
#include <cstdint>

namespace cg = cooperative_groups;

// Deliberately one cooperative launch for the frozen R19F2 per-tensor E4M3
// contract. The two grid barriers make the global amax available before any
// scale/cast. No GEMM or downstream arithmetic is implemented here.
__global__ void fused_current_scale_kernel(
    const __nv_bfloat16* input,
    uint8_t* output_bytes,
    float* inverse_scale,
    float* amax_workspace,
    int64_t n) {
  cg::grid_group whole_grid = cg::this_grid();
  const int tid = threadIdx.x;
  const int64_t global_tid = static_cast<int64_t>(blockIdx.x) * blockDim.x + tid;
  const int64_t stride = static_cast<int64_t>(gridDim.x) * blockDim.x;

  if (global_tid == 0) {
    *amax_workspace = 0.0f;
  }
  whole_grid.sync();

  float local_amax = 0.0f;
  for (int64_t i = global_tid; i < n; i += stride) {
    const float value = __bfloat162float(input[i]);
    local_amax = fmaxf(local_amax, fabsf(value));
  }
  __shared__ float block_amax[256];
  block_amax[tid] = local_amax;
  __syncthreads();
  for (int offset = 128; offset > 0; offset >>= 1) {
    if (tid < offset) {
      block_amax[tid] = fmaxf(block_amax[tid], block_amax[tid + offset]);
    }
    __syncthreads();
  }
  if (tid == 0) {
    atomicMax(reinterpret_cast<int*>(amax_workspace), __float_as_int(block_amax[0]));
  }
  whole_grid.sync();

  const float amax = *amax_workspace;
  float scale = 1.0f;
  if (amax != 0.0f && !isinf(amax) && !isnan(amax)) {
    scale = __fdiv_rn(448.0f, amax);
    if (isinf(scale)) {
      scale = FLT_MAX;
    }
  }
  if (global_tid == 0) {
    *inverse_scale = __frcp_rn(scale);
  }
  for (int64_t i = global_tid; i < n; i += stride) {
    const float value = __bfloat162float(input[i]);
    const __nv_fp8_e4m3 quantized = static_cast<__nv_fp8_e4m3>(value * scale);
    output_bytes[i] = quantized.__x;
  }
}

void launch_fused_current_scale(
    const torch::Tensor& input,
    const torch::Tensor& output_bytes,
    const torch::Tensor& inverse_scale,
    const torch::Tensor& amax_workspace,
    int64_t cooperative_blocks) {
  const __nv_bfloat16* x = reinterpret_cast<const __nv_bfloat16*>(input.data_ptr<at::BFloat16>());
  uint8_t* q = output_bytes.data_ptr<uint8_t>();
  float* inv = inverse_scale.data_ptr<float>();
  float* amax = amax_workspace.data_ptr<float>();
  int64_t n = input.numel();
  const int blocks = static_cast<int>(cooperative_blocks);
  void* args[] = {&x, &q, &inv, &amax, &n};
  auto stream = at::cuda::getCurrentCUDAStream(input.get_device());
  C10_CUDA_CHECK(cudaLaunchCooperativeKernel(
      reinterpret_cast<void*>(fused_current_scale_kernel), dim3(blocks), dim3(256), args, 0, stream.stream()));
}
