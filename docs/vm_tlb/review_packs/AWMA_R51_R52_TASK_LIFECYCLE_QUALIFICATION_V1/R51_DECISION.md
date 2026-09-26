# R51 decision

`R51_NOT_QUALIFIED_SOFTWARE_SAFEPOINT_NUMERIC_CONTRACT_NOT_CLOSED`

The real lm_head background is qualified and long enough: B0 median is 412.544 us and its exact runtime identity is the historical 18992-grid GEMV. However, output-row decomposition changes library dispatch and breaks the required bitwise contract: B8 differs in 135 FP16 elements and B32 in 151, each with maximum absolute difference 0.0078125. All bounded second-attempt API equivalents select the same differing arithmetic. CUDA Graph liveness passes for the chunked algorithm itself, but restoring/recomputing the wrong contract does not qualify it.

The diagnostic B8/B32 medians are 456.416/482.016 us (10.635%/16.840% overhead), but these numbers cannot be used to claim a latency-throughput tradeoff because the outputs are not the same B0 contract. Formal overlap timing was therefore not launched.
