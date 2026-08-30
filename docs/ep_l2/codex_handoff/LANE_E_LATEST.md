# Lane E — Line-MSHR Causality Probe

Status: `LINE_MSHR_CAUSALITY_PROBE_COMPLETE` locally; D512 descendants remain
`SPECULATIVE_PENDING_GATE` on `D512_PREFLIGHT_PASS`.

The Line-MSHR256 audit found no telemetry clipping: the Line-MSHR allocator is
already capacity-parameterized and its 1025-bin occupancy histogram, p95, delta
state, parser, and output fields cover 256. Directed 256-entry boundary tests
passed, including exact full reason and drain/reuse. MSHR128 D512 equivalence is
byte-identical for both vectorAdd_4M and convolutionSeparable.

Convolution D512 removes `931,416` Line-MSHR-full events at MSHR256 but improves
cycles only `292,211 -> 291,108` (0.38%). D256 is unchanged at 290,308 cycles;
the spmv negative control is unchanged at 23,560 cycles. Classification:
`MSHR_ADMISSION_THROTTLE_DOWNSTREAM_LIMITED`, not a new primary baseline.

Review pack: `docs/ep_l2/review_packs/LINE_MSHR_CAUSALITY_r1/`.
