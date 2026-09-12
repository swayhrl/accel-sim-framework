# C16 Lane G — Wave-1 Llama native early checkpoint

Status: `C16_G_WAVE1_LLAMA_NATIVE_G1_CENSUS_EARLY_CHECKPOINT`.

This is a real RTX 3090 checkpoint, not a CPU, mock, fixture, simulator, or synthetic result. It covers only the immutable A P0 Llama3.2-1B package (`20fb38e6ca629f1a93db7939248bd1a03790724c`; manifest SHA256 `ac59f0d2aca95021c686948d7244ce50375530bbe983c8508ca5f6954e80230f`). Qwen P1/P2/P3 are explicit gaps and have not been transferred.

Formal GPU operations bind runtime commit `12e9f16d1e503d3b4bfeba0fa08e0d350669f0e2`. The runtime-only parent-lease contract gives the profiler wrapper the sole shared-budget lease; its child runner must prove a token-bound immutable parent receipt, exact identity, and a concurrently held ledger lock. The independent export validator is `d17f9bc94bc9ebe0c3d245061532c5c4df350a93`.

The clean S0 G0 sanity matched the prior native canary exactly for output checksum, FP16 dtype, `TRANSFORMERS_CONFIG:sdpa` attention backend, and peak allocated/reserved VRAM. Formal G1 then independently validated 13,700 CUDA kernels, one stream, 13,700 CUDA-runtime correlation joins, and five each of full-forward/prefill/decode NVTX ranges. The formal S1/CODE and S2/TEXT census exports independently validate 56,720 and 113,200 CUDA kernels respectively, with the same identity/correlation/NVTX closure.

`KERNEL_CATALOG.tsv.gz` is a lossless gzip of all 169,920 catalog launch rows. The 131,025,442-byte expanded TSV is retained locally at the path and SHA in `KERNEL_CATALOG_COMPRESSION_RECEIPT.json`; no sampling or aggregation was used. Raw `.nsys-rep` and SQLite exports are returned locally and not committed.

Three pre-gate nsys attempts remain in `EXECUTION_BUDGET_LEDGER.json` with their original resource accounting and `NON_SCIENTIFIC_DIAGNOSTIC` status: the non-materializing NVTX capture-range attempt, the profile before parent-lease proof, and the pre-gate census. They are excluded from the catalog. G2/NCU and G3/NVBit have not started and do not block this G1 census checkpoint.

Semantic limitation: the catalog has actual launch, stream, correlation, name, grid/block, duration, and NVTX phase facts. It deliberately leaves operator/layer as `UNKNOWN` unless direct runtime evidence exists; the current 0 operator/layer mapped-time fraction cannot be read as absence of useful operator/layer features.

For Lane C schema sanity, consume this checkpoint's final `PUBLISH_MANIFEST.json`, decompress `KERNEL_CATALOG.tsv.gz` when launch-level rows are required, and use `WAVE1_PUBLISH_MANIFEST.json` for the four-deployment partial/gap declaration. The runtime commit is a code anchor, not the final checkpoint commit.
