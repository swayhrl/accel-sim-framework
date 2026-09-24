# Open issues / limits

No blocking issue remains for this reclassification.

- `AUXILIARY` only means a correlated CPU kernel-launch API started outside all
  C16 model NVTX ranges. It is deliberately not labeled argmax, sampling, or
  another specific operator without explicit source evidence.
- This authority happened to provide a unique runtime correlation and same-TID
  phase context for every model-phase kernel. Future exports may retain
  `UNKNOWN` when the chain is missing, duplicate, or thread-mismatched.
- Family labels are implementation-name normalization only; GEMM/GEMV remain
  semantic `UNKNOWN` unless separately evidenced.
