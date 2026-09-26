# Validation summary

- `VERIFIED_RUN`: 10/10 preregistered matrix points completed, each with exactly one cold run and one immediate repeat in-process.
- `VERIFIED_RUN`: all actual GPU work acquired `/data/c16/locks/c16_gpu_campaign.lock`.
- `VERIFIED_RUN`: maximum allocation was 18,790,481,920 bytes, below the 20 GiB cap; the host-headroom gate passed before every point.
- `VERIFIED_RUN`: NSYS SQLite exported for all 10 points; CUPTI migration memcpy activity and NVTX ranges were joined into event/step tables.
- `VERIFIED_RUN`: source and node164 copies both pass every entry in `RAW_DATA_INDEX.tsv`; compact authority hashes pass `SHA256SUMS`.
- `VERIFIED_RUN`: Python sources pass `py_compile`, CUDA harness compiles with CUDA 12.8, and `git diff --check` passes.
- `UNKNOWN`: dedicated GPU/CPU fault counters remain unavailable. No TLB, PPN, page-size, shootdown, or fault-count claim is made.
