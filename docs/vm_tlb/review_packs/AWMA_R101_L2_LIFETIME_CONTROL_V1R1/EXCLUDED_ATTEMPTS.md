# Excluded and diagnostic-only attempts

All are retained under node164 `raw/` and excluded from formal medians/traffic gates.

1. Capability build attempt0 had a C `printf` `%zu` type warning in the property-reporting path. It was corrected before scientific execution; the PTX discard instruction and CUDA kernel semantics did not change.
2. Initial NSYS graph-path invocation used a local file named `profile.py`, shadowing Python's standard `profile` module and failing during PyTorch import. It collected no qualifying graph data. Renamed `profile_graph.py` before the qualified run.
3. Isolated K128 NCU B0/D1 applications autotuned author XXT to block 128 versus 256. One matching B0 recollection still selected 128. Both B0 attempts and the D1 raw profile remain available, but no K128 write-reduction ratio is used. The same-process NSYS graph path did have equal K128 arithmetic strata.
4. First D2 canary wrapper assumed 35 graph nodes were visible during active capture. CUDA exposed 33; the remaining two are terminal discard-only nodes. Numeric/liveness gates passed; the overstrict assertion and diagnostic are retained. A non-compute event boundary was tried once and did not change the 33-node snapshot, then removed before formal timing.
5. An early arena profiling/timing script passed a temporary preallocated arena Tensor into capture and failed to retain its lifetime. Those NSYS/timing artifacts are explicitly `OBSOLETE_ARENA_TEMPORARY_LIFETIME`; they are not scientific evidence. Final code retains arena ownership, confirms output bitwise on every formal replay, reruns NSYS path qualification and all 1+2+7 paired timing.
6. Arena NCU attempt0 selected a broad parent NVTX range and instrumented output-comparison kernels; attempt1 found the freed external-arena issue before producing a report. The final same-process A0/D2 report selects only the two exact child graph ranges, verifies outputs and arithmetic strata, and is the sole valid D2 NCU profile.
