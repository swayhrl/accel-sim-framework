# Qwen2.5 S2 kernel census — node109

Decision: `AWMA_QWEN25_S2_KERNEL_CENSUS_V1_COMPLETE_WITH_SCOPE`.

One lightweight NSYS CUDA/NVTX census ran the exact frozen B1/T2048/Decode32 FP16/SDPA workload. It recorded 34,677 total CUDA kernel activities, with 34,072 inside the explicit inference NVTX ranges: 408 Prefill and 33,664 Decode (1,052 each for 32 steps). Full launch inventory SHA256 is `7825697aa23647daee6a38ac4436029c5746fe29a468d303520d3884f2b4abef` and resides at `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/qwen25_s2_kernel_census_20260917T101100Z/analysis/ALL_KERNEL_LAUNCHES.tsv`; node164 hash verification passed.

Q05 occurrence 0: 159,969 ns, grid 16,1,14 / block 128,1,1. Prefill has 10 same-shape flash_fwd launches, duration median 154,112.5 ns. FlashAttention family consumes 14.31% of Prefill GPU duration; the single Q05 launch is 1.50%. Decode has 1,536 flash_fwd launches using distinct shapes. Q05 is representative within its same Prefill FlashAttention family, partially representative for broader Attention, and a special case for the whole run. Layer/operator mapping beyond explicit implementation labels is not proven.

No NCU/NVBit/C16WARP1/simulator-native additional trace was run.
