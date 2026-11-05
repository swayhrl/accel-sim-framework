# Closed metadata performance report candidate

Status: ALL_SIX_CLOSED_QUALIFIED

Only CLOSED_ACCEPTED results with exact Source/input/Spec/full drain, full-SHA archive and two distinct same-SHA native restores receive cycles. Missing results remain UNKNOWN.

| Group | Cohort | Mode | Cycles | Qualification |
|---|---|---|---:|---|
| A1 | EP_PERF_PFV4_A1_STENCIL_S_G64W8_V1 | S | 4299729 | QUALIFIED_CLOSED_METADATA |
| A1 | EP_PERF_PFV4_A1_STENCIL_WV_ZERO_RO_G64W8_V1 | WV_ZERO_RO | 4282418 | QUALIFIED_CLOSED_METADATA |
| B | EP_PERF_PFV4_VECTOR4M_WV_ZERO_RO_1700_V1 | WV_ZERO_RO | 45425 | QUALIFIED_CLOSED_METADATA |
| B | EP_PERF_PFV4_VECTOR4M_W_ONLY_1700_V1 | W_ONLY | 45446 | QUALIFIED_CLOSED_METADATA |
| A3 | EP_PERF_PFV4_A3_TRANSPOSE_S_G64W8_V1 | S | 200330 | QUALIFIED_CLOSED_METADATA |
| A3 | EP_PERF_PFV4_A3_TRANSPOSE_WV_ZERO_RO_G64W8_V1 | WV_ZERO_RO | 200972 | QUALIFIED_CLOSED_METADATA |

Delta is candidate minus baseline; reduction percent is 100*(baseline-candidate)/baseline. Both signs are retained.

| Comparison | Signed cycle delta | Reduction percent | Status |
|---|---:|---:|---|
| A1 S G64W8 minus exact same-mode REF | -943210 | +17.990101% | QUALIFIED_CLOSED_METADATA_COMPARISON |
| A1 WV_ZERO_RO G64W8 minus exact same-mode REF | -486475 | +10.201005% | QUALIFIED_CLOSED_METADATA_COMPARISON |
| A3 S G64W8 minus exact same-mode REF | +0 | +0.000000% | QUALIFIED_CLOSED_METADATA_COMPARISON |
| A3 WV_ZERO_RO G64W8 minus exact same-mode REF | +0 | +0.000000% | QUALIFIED_CLOSED_METADATA_COMPARISON |
| B W minus S | -528 | +1.148475% | QUALIFIED_CLOSED_METADATA_COMPARISON |
| B WV minus W | -21 | +0.046209% | QUALIFIED_CLOSED_METADATA_COMPARISON |
| B F minus WV | +10500 | -23.115025% | QUALIFIED_CLOSED_METADATA_COMPARISON |
| V3 FWT S G64W8 minus G32W16 | +332 | -0.195370% | QUALIFIED_CLOSED_METADATA_COMPARISON |
| V3 FWT WV_ZERO_RO G64W8 minus G32W16 | -120 | +0.070495% | QUALIFIED_CLOSED_METADATA_COMPARISON |
| V3 GEMM S G64W8 minus G32W16 | +0 | +0.000000% | QUALIFIED_CLOSED_METADATA_COMPARISON |
| V3 GEMM WV_ZERO_RO G64W8 minus G32W16 | +0 | +0.000000% | QUALIFIED_CLOSED_METADATA_COMPARISON |

Original V3 eight accepted cells (each independently requalified from closed metadata):

| Cohort | Mode | Cycles | Qualification |
|---|---|---:|---|
| EP_PERF_PFV3_MIDTAG_FWT_S_G32W16_V1 | S | 169934 | QUALIFIED_CLOSED_METADATA |
| EP_PERF_PFV3_MIDTAG_FWT_S_G64W8_V1 | S | 170266 | QUALIFIED_CLOSED_METADATA |
| EP_PERF_PFV3_MIDTAG_FWT_WV_ZERO_RO_G32W16_V1 | WV_ZERO_RO | 170225 | QUALIFIED_CLOSED_METADATA |
| EP_PERF_PFV3_MIDTAG_FWT_WV_ZERO_RO_G64W8_V1 | WV_ZERO_RO | 170105 | QUALIFIED_CLOSED_METADATA |
| EP_PERF_PFV3_MIDTAG_GEMM_S_G32W16_V1 | S | 548988 | QUALIFIED_CLOSED_METADATA |
| EP_PERF_PFV3_MIDTAG_GEMM_S_G64W8_V1 | S | 548988 | QUALIFIED_CLOSED_METADATA |
| EP_PERF_PFV3_MIDTAG_GEMM_WV_ZERO_RO_G32W16_V1 | WV_ZERO_RO | 548988 | QUALIFIED_CLOSED_METADATA |
| EP_PERF_PFV3_MIDTAG_GEMM_WV_ZERO_RO_G64W8_V1 | WV_ZERO_RO | 548988 | QUALIFIED_CLOSED_METADATA |

A1/A3 references come from each final FAMILY_SCOPE accepted_same_mode_ref. B reuses S45974/F55925; W is not a same-mode REF. F minus WV does not identify an independent causal T effect. Geometry changes resources; no equal-area, cross-workload aggregate, geometric mean or PPA claim.

This foreground tool reads only JSON metadata and emits stdout. It never starts a model/background actor, writes authority/controller state, imports native/dispatcher code, reads raw logs/Trace/archive bodies, copies Trace or publishes Git.
