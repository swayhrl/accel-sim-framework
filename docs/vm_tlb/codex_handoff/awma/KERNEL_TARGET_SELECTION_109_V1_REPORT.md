# AWMA kernel target selection — node109

Decision: `AWMA_KERNEL_TARGET_SELECTION_V1_COMPLETE_WITH_SCOPE`.

Offline-only selection from the accepted exact census. No NSYS/NCU/NVBit/C16WARP1/simulator-native capture ran in this stage.

Selected candidates (all `CANDIDATE_ONLY_NOT_CAPTURED`):

- Prefill GEMM: CUTLASS Kernel2 `grid=128,3,1`, `block=256,1,1`, reference global launch 285, occurrence 12; 20 recurrences and 57.31% of Prefill GEMM family time (38.10% Prefill GPU time).
- Decode GEMV: `internal::gemvx` int6 `grid=1216,1,1`, `block=16,4,1`, reference launch 1244, occurrence 10; 1,536 occurrences across all 32 steps, 40.64% GEMV-family time (20.22% Decode GPU time).
- Decode Flash splitkv: `grid=1,9,14`, `block=128,1,1`, reference launch 1748, occurrence 17; 768 occurrences across all steps, 82.10% Decode Flash time.
- Decode Flash splitkv-combine: `grid=2,1,1`, `block=128,1,1`, reference launch 1018, occurrence 0; 768 occurrences across all steps, 17.90% Decode Flash time.

Q05 clarification: the 10 Prefill FlashAttention occurrences all use Q05's grid/block. Q05 is representative within that same family, but Decode uses distinct Flash shapes. `LAYER_MAPPING_NOT_PROVEN`; existing Native Prefill Heavy GEMM exact alignment is `NATIVE_TARGET_MATCH_NOT_PROVEN`.

Full inventory remains on node164 and its hash was reverified. No candidate was captured.
