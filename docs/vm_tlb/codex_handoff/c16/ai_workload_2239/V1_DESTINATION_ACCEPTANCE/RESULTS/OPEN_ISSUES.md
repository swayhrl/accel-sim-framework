# V1 open issues

1. **Frozen-input identity is not closed (blocking).** Locate the existing
   Llama S0 frozen bundle containing `TEXT.txt`, exact `TEXT_T128.json`,
   `LLAMA_S0_TEXT_TOKEN_IDS.json`,
   `LLAMA_S0_TEXT_BINDING_RECEIPT.json`, and
   `C16_FIND_AND_TRANSFER_LLAMA_S5_FROZEN_INPUT_BINDING_RECEIPT.json`.
   Verify all four expected hashes using
   `util/vm_tlb/c16/host_4080/c16_frozen_input_admission.py`; do not regenerate
   any token IDs with a tokenizer.
2. **Destination GPU runtime is absent/non-visible.** The container has no
   NVIDIA device visibility, CUDA toolkit, PyTorch, or transformers. A later
   authorized runtime setup must produce a fresh destination receipt; it must
   not claim historical R5 equivalence.
3. **NVBit closure is missing.** Acquire or rebuild NVBit 1.7.5 only in a
   later authorized phase, then hash-close the release archive, core library,
   tracer source, and tracer binary. No tracing occurred in V1.
4. **NCU closure is missing.** `ncu` is not installed/found. A later phase
   must record its binary/version and permission state before any bounded
   fixture or profiling.
5. **RTX4080 receipt-bound artifacts have not arrived.** The N1 report/CSV
   and U8 `FINAL_SHA256SUMS` manifest were not visible in the bounded C16
   destination roots. Later transfer must be copy-not-move and SHA-close each
   object.
6. **R5 U5/U6/U9 payload provenance remains unknown.** No path + size + SHA256
   + authority binding was located. Do not promote it from filenames or review
   summaries.

No 3090 recovery-root copy, storage import, bulk workload run, profiler
attachment, process control, tokenizer regeneration, or model download is
authorized by this V1 result.
