# R55 platform and closest-work audit

Source-only audit based on Round07: Transformer Engine NVFP4 requires rowwise/columnwise quantized layouts and scales; transposition-invariant FP4 directly addresses transpose-scale inconsistency; NVIDIA NVFP4 pretraining and Quartet II cover stable low-precision training; MOSS covers online scaling/dequantization overhead. RTX4080 lacks NVFP4-native hardware behavior, so no R55 GPU performance experiment was run and no platform throughput claim is made.
