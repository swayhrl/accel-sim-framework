# Historical wallclock and existing original performance — first8 only

All32 historical references are source-SHA checked originals. CH/DH P0 for ATAX/MVT/BICG are the already-ratified exact P0 aliases from downstream18; this is existing Stage-I P0 reuse, not import of PQ/PS or another configuration. No new result is used here.

| Program | CH P0 wall h | Old DH P0/F128/F256 wall h | Max observed RSS GiB | CH P0 cycles | DH P0/F128/F256 cycles |
|---|---:|---|---:|---:|---|
| convolutionSeparable | 1.524 | 2.816 / 2.472 / 1.556 | 1.281 | 825151 | 800572 / 674364 / 562886 |
| scan | 8.318 | 9.723 / 9.008 / 7.977 | 0.848 | 6710840 | 6648993 / 5748280 / 5179817 |
| 2DCONV | 2.262 | 1.868 / 1.430 / 1.473 | 0.570 | 1548909 | 462740 / 437573 / 429253 |
| ATAX | 2.751 | 4.249 / 4.080 / 3.343 | 2.266 | 28428842 | 31880220 / 31894637 / 31321955 |
| MVT | 2.693 | 3.974 / 3.454 / 3.314 | 2.266 | 26581175 | 34687540 / 35332620 / 35093446 |
| BICG | 2.376 | 3.927 / 2.918 / 2.822 | 2.309 | 26298698 | 28685812 / 29210480 / 28883488 |
| vectorAdd | 0.361 | 0.453 / 0.445 / 0.459 | 0.602 | 220803 | 217305 / 213053 / 236217 |
| GEMM | 2.069 | 2.085 / 1.943 / 2.885 | 4.781 | 1395216 | 826089 / 826089 / 826089 |

If both CH F points merely matched each program's historical CH P0 elapsed, the16 points would total about44.71 model-hours serially. This is a historical reference, not a predicted future wall time. With16 simultaneous single-core models, the critical historical case is scan (CH P08.32h; old DH variants7.98–9.72h). Current host CPU contention, affinity, trace IO, instrumentation, memory pressure and changed scheduler behavior must calibrate any real ETA. Queue expansion is not a wall-time prediction.

Historical RSS is observed, not a hard upper bound or a grant. No fixed new global4GiB/16GiB policy is proposed by this analysis agent. Root independently owns resource admission.

Exact paths/SHA/UUID, exit return/stop status, elapsed seconds and observed peak RSS appear in HISTORICAL_WALLCLOCK.json. All32 have receipts; none was selected by speedup or runtime.

## Existing phase-cycle detail newly consumed here

Existing original strict RESULT proof.kernels contains cycle rows for some inputs; those were not in the previous whole-input L counter projection. This new read-only consumption leaves that frozen report unchanged. Each conv/scan grouped cycle sum equals its program total.

| DH phase group | P0 cycles | F128 cycles | F256 cycles |
|---|---:|---:|---:|
| convolutionSeparable / rows | 365625 | 311113 | 269306 |
| convolutionSeparable / columns | 434947 | 363251 | 293580 |
| scan / short_scan | 2321049 | 1991981 | 1823733 |
| scan / long_firstpass | 2205820 | 1894833 | 1664383 |
| scan / chunk_totals | 248231 | 248235 | 247109 |
| scan / uniform_update | 1873893 | 1613231 | 1444592 |

Both convolution directions improve. For scan, the sparse chunk-total group changes little; most total savings are in the bulk short/firstpass/uniform groups. This localizes existing runtime improvement, while queue, credit, MSHR, cache-hit and critical-path mechanisms remain unproven without relevant counters. These are existing recorded cycle values, not fresh measurements.
