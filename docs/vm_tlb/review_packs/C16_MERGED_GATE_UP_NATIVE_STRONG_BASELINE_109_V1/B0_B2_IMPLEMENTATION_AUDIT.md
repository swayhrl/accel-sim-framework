# B0/B2 implementation and STOP audit

- Comparison class: same checkpoint and logical AWQ semantics, cross-runtime strong baseline; **not** a merge-only strict A/B.
- B0 is the accepted AutoAWQ runtime with observational outer/FFN events and canary-only tensor snapshots.
- B2 is pinned vLLM `df8fd42116f172b7a53bc10c8a680b05232edbed`, `MergedColumnParallelLinear` + `SiluAndMul`, with `AutoAWQMarlinLinearMethod` selecting `MarlinLinearKernel`.
- CPU canonical unpack/loader identity passed all 28 layers; no requantization occurred.
- Both canaries generated `[23578, 11, 323, 3950]`; all compared tensors were finite and shape-correct.
- Frozen FP16 tolerance failed in 14/336 gate/up/down occurrences (gate=2, up=9, down=3); max absolute difference was 0.25.
- Formal ABBA timing was therefore not started. Canary wall values are retained only as excluded diagnostic values and support no speedup claim.
- The earlier two-stream correctness STOP remains frozen and is not an ancestor of this branch.
