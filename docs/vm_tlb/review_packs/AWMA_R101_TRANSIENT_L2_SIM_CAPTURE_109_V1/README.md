
# AWMA R101 Transient-L2 simulator-native capture — node109 producer

Final state: **`R101_TRANSIENT_SIM_CAPTURE_PASS`**. Stable input identity: `SIM_INPUT_R101_L512_TRANSIENT_V1`; capture ID: `R101_L512_TRANSIENT_d809efb8e4227dc6`. This is the exact accepted R101 discovery L512 BF16 payload, captured anew as simulator-native trace; it is not an algorithm variant or simulator result.

Full-five-step scope was retained: 18 ordered kernel members = 3 normalization plus 5 consecutive XXT → BA → fused_bmm_add iterations on all 44 512×512 tiles. The first two iterations are available as contiguous context/ROI if the consumer preregisters them, but the producer did not shorten or select a favorable iteration. All four real device regions and kernel-boundary lifetime transitions are in `BUFFER_REGION_MAP.tsv` and `REGION_LIFETIME.tsv`.

Every native member is listed in `TRACE_MEMBER_MANIFEST.tsv`, `NATIVE_KERNEL_BINDING.tsv`, and `raw/formal_full5/raw/kernelslist.g`. All 18 terminal receipts are COMPLETE with drop=overflow=0; xz, the accepted traceg grammar validator, independent frozen trace-parser-only harness, output SHA and repeat hash checks passed. The compact review files are here. The original `.trace.xz`, native `.traceg.xz`, profiler-free launch census, canaries, tool binaries/JIT data and logs are under node164 durable root `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r101_transient_l2_sim_capture_20260927/`, indexed by `RAW_DATA_INDEX.tsv` and `SHA256SUMS`.

Read `EXECUTION_CONTEXT.md`, `TRACER_SOURCE_AND_BUILD_RECEIPT.md`, `TERMINAL_AND_COMPLETENESS.md`, and `CLAIM_BOUNDARY.md` for qualification and limits. No Accel-Sim run or architecture mechanism was performed on 109.
