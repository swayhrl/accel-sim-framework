import os
from setuptools import setup
import torch
from torch.utils.cpp_extension import BuildExtension, CUDAExtension

source_root = os.path.dirname(os.path.abspath(__file__))
generator_flag = []
if os.path.exists(os.path.join(torch.__path__[0], "include", "ATen", "CUDAGeneratorImpl.h")):
    generator_flag = ["-DOLD_GENERATOR_PATH"]

common_flags = [
    "-O3",
    "-std=c++17",
    "-DENABLE_BF16",
    "-U__CUDA_NO_HALF_OPERATORS__",
    "-U__CUDA_NO_HALF_CONVERSIONS__",
    "-U__CUDA_NO_BFLOAT16_OPERATORS__",
    "-U__CUDA_NO_BFLOAT16_CONVERSIONS__",
    "-U__CUDA_NO_BFLOAT162_OPERATORS__",
    "-U__CUDA_NO_BFLOAT162_CONVERSIONS__",
    "--expt-relaxed-constexpr",
    "--expt-extended-lambda",
    "--use_fast_math",
    "-gencode",
    "arch=compute_89,code=sm_89",
] + generator_flag

setup(
    name="c16_awq_crossm_replica",
    version="0.0.9+c16crossmreplica",
    ext_modules=[
        CUDAExtension(
            "awq_crossm_replica_ext",
            [
                "awq_ext/pybind_awq.cpp",
                "awq_ext/quantization/gemm_cuda_gen.cu",
                "awq_ext/layernorm/layernorm.cu",
                "awq_ext/position_embedding/pos_encoding_kernels.cu",
                "awq_ext/quantization/gemv_cuda.cu",
                "awq_ext/vllm/moe_alig_block.cu",
                "awq_ext/vllm/activation.cu",
                "awq_ext/vllm/topk_softmax_kernels.cu",
            ],
            include_dirs=[source_root],
            extra_compile_args={
                "cxx": ["-g", "-O3", "-fopenmp", "-lgomp", "-std=c++17", "-DENABLE_BF16"],
                "nvcc": common_flags,
            },
        )
    ],
    cmdclass={"build_ext": BuildExtension},
)
