# P1 decision

`P1_SOFTWARE_BASELINE_CLOSES_GAP`

Stock Flash SDPA changes the target output across B1/B4: 11 FP16 elements differ, maximum absolute difference is 0.000244140625, and maximum ordered-code distance is 6. This establishes the numerical phenomenon.

Two contract-preserving software baselines close it:

- fixed physical B4 padding is bitwise invariant but costs 79.704% over stock B1;
- the parallel Triton fixed-split-256 producer plus fixed-order per-head combine is bitwise invariant and costs only 0.887% over stock B1. Its B1/B4 timing delta is 5.566%, but the larger CV is 8.442%, so it fails the pre-registered `>3x CV` materiality gate.

The Triton baseline remains parallel (126/504 producer programs and 14/56 combine programs for B1/B4), has no global lock or single-thread reduction, and is closer to the FP32 reference than stock in the recorded maximum-error check. No material residual remains to localize to completion/commit rather than arithmetic organization. Conditional NCU was therefore not authorized.
