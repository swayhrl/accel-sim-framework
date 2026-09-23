# MATCHED HELD-OUT NATIVE AUTHORITY — 2026-09-23

Node109 repair authority:

`hrl/awma-109-rtx4080-heldout-scale-match-v1 @ 1e3286862a496ced4182e073739a5678100dd846`

Node164 bundle:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/rtx4080_heldout_scale_match_v1_20260923T121500Z`

Evidence class:

`RTX4080_HELDOUT_MATCHED_NATIVE_TIMING_V1`

Matched Native per-launch medians:

```text
H_CACHE   1024 elements = 1.754112 us
H_STREAM  4096 elements = 2.845696 us
H_COMPUTE 1024 elements = 2.845696 us
```

Each point:

- 5 independent processes;
- 1000 host repetitions/process;
- CUDA-event timing;
- exact trace problem size;
- same accepted heldout source identity;
- `MATCHED_PER_LAUNCH_COMPARISON_VALID`.

Canonical current platform bundle authority:

```text
member count = 108
manifest SHA256 =
5dca0e6b5629db48c0f457928573816188fcbb6ca6c81326bcaadaeef05ab074
```

The older 47-member bookkeeping state is preserved as historical and superseded.

For orientation only, using the previously published frozen simulator per-launch values:

```text
H_CACHE   sim 2.529341317 us → expected error ~44.19%
H_STREAM  sim 2.500998004 us → expected error ~12.11%
H_COMPUTE sim 2.498203593 us → expected error ~12.21%
```

Expected 3-point median error is ~12.21%, which would satisfy the predeclared <=25% PASS threshold.

This is NOT a substitute for node174 no-tuning replay. Node174 must:

1. recover frozen config SHA `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`;
2. replay the immutable H_CACHE/H_STREAM/H_COMPUTE traces;
3. recompute all three errors from fresh receipts;
4. apply the frozen PASS/scoped-PASS/FAIL gate;
5. continue to later science phases only if the gate passes.

No platform parameter change is authorized.
