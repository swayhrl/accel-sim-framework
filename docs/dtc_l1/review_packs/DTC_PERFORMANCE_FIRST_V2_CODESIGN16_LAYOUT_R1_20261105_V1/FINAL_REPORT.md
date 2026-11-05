# DTC-L1 V2 Physical x PIB16 R1 final evidence

This report is generated from the independently reverified fixed16 results. It does not select a different workload set or a best configuration per program.

Accepted: 16/16; archived negative: 0; unused safety HOLD: 0.

| Program | Profile | cycles | DH0/new | CH0/new | J |
|---|---|---:|---:|---:|---:|
| 2DCONV | PHYS768_OOPIB192_TAG64x8 | 470776 | 0.982930 | 3.290119 | 1.000000 |
| 2DCONV | PHYS1024_OOPIB192_TAG64x8 | 470776 | 0.982930 | 3.290119 | 1.000000 |
| GEMM | PHYS768_OOPIB192_TAG64x8 | 814235 | 1.014558 | 1.713530 | 1.000000 |
| GEMM | PHYS1024_OOPIB192_TAG64x8 | 814235 | 1.014558 | 1.713530 | 1.000000 |
| convolutionSeparable | PHYS768_OOPIB192_TAG64x8 | 818340 | 0.978288 | 1.008323 | 0.995376 |
| convolutionSeparable | PHYS1024_OOPIB192_TAG64x8 | 818340 | 0.978288 | 1.008323 | 0.995376 |
| scan | PHYS768_OOPIB192_TAG64x8 | 6680780 | 0.995242 | 1.004499 | missing |
| scan | PHYS1024_OOPIB192_TAG64x8 | 6651571 | 0.999612 | 1.008911 | missing |
| ATAX | PHYS768_OOPIB192_TAG64x8 | 30602022 | 1.041768 | 0.928986 | 1.000000 |
| ATAX | PHYS1024_OOPIB192_TAG64x8 | 30602022 | 1.041768 | 0.928986 | 1.000000 |
| MVT | PHYS768_OOPIB192_TAG64x8 | 30609855 | 1.133215 | 0.868386 | 1.000000 |
| MVT | PHYS1024_OOPIB192_TAG64x8 | 30609855 | 1.133215 | 0.868386 | 1.000000 |
| BICG | PHYS768_OOPIB192_TAG64x8 | 30892841 | 0.928559 | 0.851288 | 1.000000 |
| BICG | PHYS1024_OOPIB192_TAG64x8 | 30892841 | 0.928559 | 0.851288 | 1.000000 |
| vectorAdd | PHYS768_OOPIB192_TAG64x8 | 217305 | 1.000000 | 1.016097 | 1.000000 |
| vectorAdd | PHYS1024_OOPIB192_TAG64x8 | 217305 | 1.000000 | 1.016097 | 1.000000 |

## Statistics and evidence

The exact profile GMs, suite statistics, complete accepted intersections and complete-J intersections are preserved in B_SUMMARY.json and final_evidence/D_final/INDEPENDENT_STATISTICS.json. All missing terms remain missing; available-set GMs are not full-eight GMs. Scan J remains missing because the original scan physical and PIB runs were resource-cadence-stop negatives.

final_evidence/D_final/MATRIX_RESULTS.json records each kernel cycle change and measured counter values with original RESULT and P0 source identities. These establish measured timing differences and counter associations; they do not establish critical-path delay, dynamic cache locality from static addresses, or causal benefit from every reduced miss. Endpoint gauges, retries and mixed last-kernel/cumulative counters are not differenced as uniform totals.

J compares the measured combination to the actual accepted same-input single-factor product reference. A value above or below one describes departure from that reference; it is not proof of the resource bottleneck or a prediction substituted for measurement.

## Cost and scope

Tag remains 64 sets x8 ways (512). Declared 128-byte physical-line accounting changes 640 to768/1024, 80 to96/128KiB (+20%/+60%). OO PIB and its coupled lower-create depth change128 to192 (+50% each). This is nominal resource accounting, not a payload-SRAM, equal-area, port, timing or PPA result. Fixed DRAM850MHz,64SM,10MiBL2,Hash and finite services remain unchanged.

Core9eedb3131937748f0492fa83aad37d3691118d70; Framework02775fd795cde5aae1480d81cee6eb481d0a08f4. Actual binary/input/config/270-option identities and source paths are in the source index and independent proof packet. Whole declared trace-body certification is not complete-application capture or numerical correctness proof.

The previous16 launcher failures and V1 scan cadence negatives remain independent original records. The temporal association between V1 scan stops and the old registry self-lock is disclosed in the preparation packet; no prior identity is retried or promoted. English LaTeX v0.23 remains unchanged.

## Stop boundary

No additional simulation, Tag recovery, capture,109 task, extra combination or manuscript change is released. Useful next work is to review measured J and per-kernel changes, then separately authorize broader coverage or diagnostics where evidence remains insufficient. This source-derived report does not automatically certify visual figures or new causal claims.
