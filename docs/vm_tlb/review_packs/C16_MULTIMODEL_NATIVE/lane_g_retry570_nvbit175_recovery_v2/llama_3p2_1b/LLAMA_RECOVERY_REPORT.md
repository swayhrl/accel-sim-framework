# Llama NVBit 1.7.5 recovery capture

`LLAMA_FULL_TARGET_TRACE_COMPLETE`. The frozen Llama S0/B1/T128/decode4 contract is unchanged.

- `LARGE_INDEX_PREFILL_TARGET`: exact `indexSelectLargeIndex`, direct NVBit static range `[101,102)`, `LDG.E.U16`. Historical 34 is forbidden and historical 348 was not reused.
- `DECODE_INDEX_TARGET`: independently observed shape-dependent exact `indexSelectSmallIndex`, direct NVBit-native static range `[17,18)`, `LDG.E`. It was mapped from the current model/runtime, not copied from LargeIndex.

LargeIndex emitted 8,192 address-bearing records in each S3/S4 prefill run and in S5 Prefill. Its S5 logical Decode1--4 counts are zero because that exact function did not launch during decode: `STRUCTURAL_ZERO_TARGET_NOT_LAUNCHED`, not a claim that decode had no memory access. The profiler census observed SmallIndex in all three actual cache-correct decode forwards; the SmallIndex S5 capture produced 64 address-bearing records in each of logical Decode2--4. Logical Decode1 remains the prefill-derived greedy token under the immutable four-token workload, with no separate CUDA forward.

All raw traces are remote-to-local SHA closed and remain outside Git.
