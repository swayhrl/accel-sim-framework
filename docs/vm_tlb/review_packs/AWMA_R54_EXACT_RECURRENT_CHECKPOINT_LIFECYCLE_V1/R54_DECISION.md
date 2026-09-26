# R54 decision

`R54_RUNTIME_FASTPATH_NOT_QUALIFIED_V1`

The exact Qwen3.5 model loaded and executed, but the actual Gated-DeltaNet canary reported reference PyTorch fallback for both causal convolution and chunk gated-delta rule. Transformers source inspection confirms those are the fallback implementations. Two bounded repairs were exhausted: installing a source-pinned Transformers version enabled Qwen3.5 architecture support, while causal-conv1d build failed on a CUDA/toolchain mismatch. Flash-linear-attention remained unavailable. No slow fallback checkpoint timing is claimed.
