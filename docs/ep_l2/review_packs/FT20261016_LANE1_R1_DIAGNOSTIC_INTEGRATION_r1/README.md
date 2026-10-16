# Lane 1 R1 diagnostic integration, revision 1

Status: PRODUCER_INTEGRATION_READY_FOR_INDEPENDENT_VALIDATION. R0 primary implementation experiments are already released and are not gated on R1.

Consume R1_DIAGNOSTIC_CONTRACT_V1.json for exact source/binary/config identities; the separate baseline template is deliberately not runnable until Lane 5 binds independent qualification and complete workload/trace/epoch identity. Lane 4 derives its ideal overlays from the same R1 B16 spec after acceptance. R0 application results cannot provide a strictly matched R1 numerator.

Applied Lane 4 CORE_MINIMAL.patch from publication96fbcb61 to exact Core126394be; all16 reviewed file contents match b8b3d55b, with only four explicit excluded CMake qualification targets added. Producing Framework fb64d952 has no gpu-simulator source difference from R0 Framework37dec04d; it freezes only the new diagnostic config vectors. Build stamp is clean modified_0.0. Dependency and input manifests bind the existing read-only pybind11 vendor source.

Executed ten production test processes on immutable R1 test binaries: inherited finite-WB eight-group suite, four true partition modes, I_WB and I_WB_META pressure/versions/drain, I_META allocator and real 1640-request/200-line/800-sector path, and I_READ_HIT latency/backpressure/known-byte/version/RAW/WAR/shared-bank paths both old-static and B16. All passed. Five entire all-ideal-OFF production fixture logs are byte-identical to frozen R0 logs, including all native records where emitted. Six intended CLI illegal combinations reject before kernel execution.

These are producer integration checks, not Lane 5 acceptance or application numerical output checks. No R0 three-pair all-OFF application reruns, formal application runs or R1 speedup claims were made. Lane 5 must qualify the incremental source/binary and application OFF boundary separately before Lane 4 diagnostics.

Two harness preconditions were corrected without changing production source or repeating passed tests: partition fixtures emit no native stream, so full stdout/stderr bytes are compared; descriptor pool and per-line cap must both be zero to reach the intended ideal-mode guard. Initial rejection/logs remain preserved. First configure lacked ignored pybind11 linkage; it was repaired using R0's same vendor dependency and its failure log is retained.

patch/ files use zero context. Apply with git apply --unidiff-zero only at exact recorded parents (Core126394be; Framework2556909e). Reverse checks pass at their frozen producing children. SHA256SUMS covers this new pack; earlier packs remain unchanged.

At the final bounded read, Lane 5 publication221c7f65 independently qualified R0 B16/U_WB16 and two actual sad processes are registered/running. R0_INDEPENDENT_QUALIFICATION_CONSUMED.json binds the imported envelope/evidence and PID check. This does not qualify R1. Lane 4 new handoff be21c95d adds per-mode ideal gate binding; R1 contracts adopt it. Lane 2 f38632c2 has a real production candidate under test; no new adapter qualification is inferred.

Pack log copies use lossless gzip (deterministic mtime=0). This preserves native trailing whitespace exactly without normalizing evidence. RAW_LOG_INDEX binds original raw and compressed hashes; decompression was checked byte-for-byte. Original result logs remain unchanged.
