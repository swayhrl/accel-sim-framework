# Provisional research findings — 22/26 only

All classifications below are `INTERIM_22_OF_26`, based only on completed
rows. They are not causal proof and do not cover the four live rows.

1. **Descriptor relief is real, but not yet a performance win.** In completed
   descriptor-heavy pairs, D256 descriptor-pool full blocks fall to zero at
   D512: vectorAdd 2,176,663→0, spmv 361,635→0, convolution 3,373,327→0,
   FWT_7_21 1,189,823→0, and FWT_11_19 119,765→0. D512 descriptor maxima rise
   naturally to 368, 403, 427, 383, and 326 respectively. Yet cycle ratios
   (D256/D512) are 0.993, 0.995, 0.993, 0.995, and 0.999: a slight slowdown or
   near tie, not a material speedup. Classification:
   `DESCRIPTOR_PRESSURE_LOW_PERF_SENSITIVITY` for this completed set.

2. **Line-MSHR pressure emerges naturally after relief without proving it is
   causal.** D512 raises Line-MSHR maxima in those same cases: vectorAdd
   92→110, spmv 99→125, convolution 126→128, FWT_7_21 102→117, and FWT_11_19
   96→108. Convolution reaches the 128 limit, but the exact Line-MSHR full
   blocker remains zero in this snapshot. This supports the
   `DESCRIPTOR_THROTTLE_MOVES_DOWNSTREAM` hypothesis only provisionally; it is
   not a warrant to tune MSHR capacity.

3. **The bottleneck appears distributed, not simply transferred to one L1 or
   per-address limiter.** Per-address cap=32 remains unchanged, while its
   block count is unchanged for most completed rows; `spmv` rises 8,598→20,040
   despite no cycle gain, so it is a candidate follow-up rather than an
   established cause. L1 line-allocation and miss-queue values are mostly
   unchanged or only modestly moved. WAD/payload capacity remain at their
   existing high-water marks (often 1024 payload p95), without a new D512-only
   capacity denial signal.

4. **Lower path remains material.** For vectorAdd, spmv, convolution, and
   FWT_7_21, L2→DRAM full blocks and scheduler-full cycles remain substantial
   after descriptor relief (for example vectorAdd: 1,724,003 and 486,133 at
   D512; convolution: 2,455,970 and 1,243,887). Native application DRAM bus
   utilization changes little (vectorAdd 0.796→0.790; spmv 0.666→0.663;
   convolution 0.651→0.647). Thus `DESCRIPTOR_THROTTLE_MOVES_DOWNSTREAM` is
   plausible for the traffic-heavy cases, but causality needs completed full
   mirror analysis and controlled factorial evidence.

5. **Temporal evidence is bursty rather than a sustained proof.** D512
   five-thousand-cycle window descriptor averages peak at 326 (vectorAdd), 353
   (spmv), and 321 (convolution), with p95 321, 351, and 303 respectively;
   Line-MSHR window averages peak 84, 104, and 127. See
   `D512_INTERIM_TEMPORAL.csv`. The zero minima show these are not uniformly
   saturated applications.

6. **RO no-MSHR motivation.** The results weaken a claim that merely doubling
   descriptor capacity yields performance. They support continuing an
   MSHR-centric RO opportunity study only as a hypothesis: descriptor relief
   exposes higher natural Line-MSHR occupancy and persistent lower-path
   pressure, but no completed row demonstrates Line-MSHR full blocking as the
   performance cause. The conservative classification is
   `INSUFFICIENT_EVIDENCE` for an MSHR-centric functional decision.

7. **Hardware plausibility.** This snapshot changes no timing or structure
   other than persistent descriptor capacity. It is compatible with the prior
   reviewed 256→512 metadata-cost estimate, but does not independently revise
   that estimate.
