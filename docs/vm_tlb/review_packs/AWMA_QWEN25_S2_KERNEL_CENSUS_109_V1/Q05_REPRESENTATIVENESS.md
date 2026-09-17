Q05 occurrence 0 is one of 10 Prefill PYTORCH_FLASH_FWD launches. All share grid/block 16,1,14 / 128,1,1. Q05 duration 159969 ns is the family maximum, versus mean 152528.5 and median 154112.5 ns; it remains within a narrow 146,976–159,969 ns same-shape distribution.

Classification: REPRESENTATIVE_WITHIN_SAME_FLASH_FAMILY, with an upper-tail duration caveat. It is PARTIALLY_REPRESENTATIVE for broader Attention: identified FlashAttention accounts for 14.31% of Prefill GPU duration, while GEMM/GEMV role attribution is UNKNOWN. It is SPECIAL_CASE for the whole run: Q05 alone is 1.50% of Prefill GPU time and does not represent all model kernels.

Decode uses the same normalized flash family but different shapes (1,9,14 and 2,1,1), so Prefill Q05 must not be assumed representative of Decode. LAYER_MAPPING_NOT_PROVEN.
