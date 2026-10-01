#include <torch/extension.h>

void launch_fused_current_scale(
    const torch::Tensor& input,
    const torch::Tensor& output_bytes,
    const torch::Tensor& inverse_scale,
    const torch::Tensor& amax_workspace,
    int64_t cooperative_blocks);

void fused_current_scale_(
    const torch::Tensor& input,
    const torch::Tensor& output_bytes,
    const torch::Tensor& inverse_scale,
    const torch::Tensor& amax_workspace,
    int64_t cooperative_blocks) {
  TORCH_CHECK(input.is_cuda() && input.is_contiguous(), "input must be contiguous CUDA");
  TORCH_CHECK(input.scalar_type() == at::kBFloat16, "input must be BF16");
  TORCH_CHECK(output_bytes.is_cuda() && output_bytes.is_contiguous(), "output must be contiguous CUDA");
  TORCH_CHECK(output_bytes.scalar_type() == at::kByte, "output must be uint8 FP8 storage");
  TORCH_CHECK(output_bytes.numel() == input.numel(), "output size differs from input");
  TORCH_CHECK(inverse_scale.is_cuda() && inverse_scale.scalar_type() == at::kFloat && inverse_scale.numel() == 1,
              "inverse scale must be CUDA float32 scalar");
  TORCH_CHECK(amax_workspace.is_cuda() && amax_workspace.scalar_type() == at::kFloat && amax_workspace.numel() == 1,
              "amax workspace must be CUDA float32 scalar");
  TORCH_CHECK(input.get_device() == output_bytes.get_device() &&
                  input.get_device() == inverse_scale.get_device() &&
                  input.get_device() == amax_workspace.get_device(),
              "tensors must share one device");
  TORCH_CHECK(cooperative_blocks > 0, "cooperative grid size must be positive");
  launch_fused_current_scale(input, output_bytes, inverse_scale, amax_workspace, cooperative_blocks);
}

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
  m.def("fused_current_scale_", &fused_current_scale_, "Exact cooperative per-tensor BF16-to-E4M3 current scaling");
}
