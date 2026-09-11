# Sub-entry effectiveness audit

## Measured activity versus measured timing

Decode F7/F8 is exact per-kernel identity at all three Lseg settings: every
one of 740 cycle values is equal at Lseg=5, 10, and 20. Nevertheless F8 emits
25,407 / 25,411 / 25,197 Sub-entry hits (and 2,044 / 1,989 / 2,217 misses).
Its formal L2-TLB misses, walks, PTE counts, requester latency, and cycles are
also equal to F7 at each same-Lseg pair. This is direct negative evidence that
the observed F8 activity produced a measurable timing advantage in these
Decode arms; it is not evidence that Sub-entry is universally ineffective.

Prefill F8 emits 891,094 / 893,925 / 894,486 hits at Lseg=5/10/20, dominated
by the direct Embedding/Output final GEMM (153,209 / 157,301 / 157,516 hits)
and then small Other-Compute kernels. Relative to F7, full-ROI cycle changes
are only -16,864, +4,615, and +13,085. The comparison is deliberately marked
`UNATTRIBUTED` for an exact Sub-entry delta because F7 does not emit the
Sub-entry checkpoint fields; F8 candidate activity cannot be subtracted from
an absent baseline field.

## F1/F2 audit

Prefill F1 has 971,478 Sub-entry hits / 116,385 misses and is 455,615 cycles
slower than F2, which has no emitted Sub-entry field. It also has more L2
misses (+31,576), walks (+8,321), PTE-DRAM (+6,640), and requester latency
(+11.95M). Decode F1 has 36,692 hits / 16,485 misses and is 24,139 cycles
faster than F2, while its walks are +26 rather than reduced. Thus neither
phase supplies a consistent activity-to-critical-path relationship.

## Supported conclusion and unresolved boundary

High hit count alone does not establish critical-path benefit. The measured
Decode identity and the small/non-monotonic Prefill F8/F7 deltas support the
signal that the observed Sub-entry work is not exposed as a timing win in this
campaign. Because baseline fields are absent in several pairs and no causal
critical-path telemetry is available, the reason remains `UNRESOLVED`.
`SUBENTRY_EFFECTIVENESS.tsv` retains top candidate-hit kernels and all exact
observable counter rows without converting an absent field to zero.
