# V29 scientific interpretation

The accepted checkpoint stores MoE experts as native MXFP4 blocks plus UE8 scales. The installed Transformers MXFP4 quantizer requires Triton >= 3.4 plus triton_kernels for the native path; otherwise a pre-quantized model defaults to BF16 dequantization. That substitution is forbidden. Independently, its native path hard-requires GPU compute capability >= 9.0, while node109 is RTX4080 SM89 (8.9). Therefore V29 fails closed before S2 execution: no router result, capture, cache/TLB claim, or cross-lineage claim was produced.
