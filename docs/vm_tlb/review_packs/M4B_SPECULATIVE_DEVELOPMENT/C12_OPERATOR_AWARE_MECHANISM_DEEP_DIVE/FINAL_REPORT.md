# C12 operator-aware mechanism deep dive — final report

## Status

`C12_OPERATOR_AWARE_MECHANISM_DEEP_DIVE_COMPLETE_READY_FOR_REVIEW`

This review pack is a read-only offline analysis of final C12 source
`a268aba0d01310294074ded5bb8017e2092394c0` (22/22 terminal PASS). It reuses
the accepted 692/740 operator map and cached trace scan, then reads the same
immutable raw logs. No simulator, replay, or trace scanner was launched; no
formal C12 asset was modified.

## MEASURED_DEEP_DIVE_FACT

1. Performance differences have two shapes. Prefill F1/F2, F5/F0, and
   F7-L10/F0 contain a single final Embedding/Output GEMM hotspot (kernel 691)
   that supplies at least half of absolute delta; F7-L5, F7-L20, and Decode
   Segment comparisons are broader. `KERNEL_DELTA_PARETO.tsv` makes the
   distinction explicit rather than treating every change as uniformly spread.
2. Direct FFN and Attention Projection do not show a layer-hotspot artifact.
   Their 16 direct layers move in the same direction at F7-L5 and F7-L20 in
   both phases, with no >=35% single-layer absolute-share outlier.
3. Decode Segment reduces walks from 15,691 to 170 and PTE-DRAM from 4,134 to
   104 at all Lseg settings, yet cycles go from -605,597 at L5 to +1,471,105
   at L20. FFN (-493,157 to +870,760) and Embedding/Output (-33,281 to
   +594,778) account for much of that phase reversal.
4. Prefill records roughly 48–50M Segment hits/L2 suppressions, but does not
   show a corresponding reduction in global traditional walks/PTE-DRAM versus
   F0. Its L5 gain is FFN/Attention-Projection-led while its L20 regression is
   FFN (+7.44M), Embedding/Output (+4.16M), and Attention Projection (+1.72M).
5. The measured full-ROI Segment break-even is bracketed near Lseg 8.75–8.76
   for Prefill and 10.83 for Decode. These are strictly
   `EMPIRICAL_INTERPOLATION_ONLY` values inside observed 5–10 or 10–20
   intervals, not extrapolated hardware claims.
6. Decode F8/F7 has exact cycle identity for all 740 kernels at every Lseg,
   even though F8 emits about 25k Sub-entry hits. Prefill F8 emits about 0.89M
   hits but changes F7 timing by only -16,864 / +4,615 / +13,085 cycles.
7. Prefill F5/PWC is +733,075 cycles, +69,793 L2 misses, +18,355 walks, and
   +15,891 PTE-DRAM while PWC hits rise +55,060. Kernel 691 contributes
   +700,253 cycles. Decode F5 is instead -5,780 cycles with near-zero walk
   change.
8. The deep dive preserves KERNEL cache outcomes, TLB/PTW/PTE counters, and
   requester latency as separate exact observations. It does not conflate lane
   references with cache transactions or cache transactions with TLB accesses.

## SUPPORTED_MECHANISM_SIGNAL

- Segment's low-Lseg benefits and high-Lseg regressions are localized to broad
  direct FFN/Attention Projection layer responses plus a phase-specific
  Embedding/Output contribution. The co-occurring requester-latency growth at
  L20 makes lookup latency a high-value hypothesis, but does not prove a
  unique downstream critical path.
- In Prefill, the F5 capacity/PWC tradeoff is consistent with capacity pressure
  overwhelming any observable PWC-hit benefit. This is a supported signal, not
  a causal counterfactual, because capacity and PWC cannot be separated in the
  existing arm.
- Sub-entry activity without a Decode timing difference supports the signal
  that its observed work is not exposed as a critical-path win in these arms.

## EMPIRICAL_INTERPOLATION_ONLY

All break-even values in `SEGMENT_BREAK_EVEN.tsv` are limited to adjacent
observed Lseg points. Prefill Embedding/Output has no measured positive point;
Decode Norm has no measured crossing. Neither is extrapolated beyond 5–20.

## UNRESOLVED

- Why the same Segment suppression accounting has opposite aggregate PTW/PTE
  behavior in Prefill and Decode cannot be resolved from these counters alone.
- KERNEL-scope cache outcomes do not expose a unique queue/native-memory or
  critical-path explanation for residual cycle movement; those summaries are
  not kernel-exact and are not apportioned.
- F7's absent Sub-entry fields prevent an exact baseline-to-F8 Sub-entry delta
  for several comparisons. `UNATTRIBUTED` is retained rather than replaced by
  zero.
- KV-runtime-range / KV-class observations remain non-semantic address/cache
  observations; they do not establish FFN/Embedding KV use or fusion.

## Next simulator hypotheses

1. Sweep Segment lookup latency tightly around the separate observed full-ROI
   brackets: roughly 8–9 for Prefill and 10–11 for Decode, while holding all
   other state fixed.
2. Instrument or perturb direct FFN/Attention Projection kernels across layers
   0–15, plus final Embedding/Output kernel 691, to test whether the observed
   translation/requester-latency association lies on the critical path.
3. Factor F5 into independent L2-TLB-capacity and physical-PWC toggles to test
   whether the Prefill regression is capacity cost, insufficient PWC benefit,
   or their interaction.

## Review entry points

- `KERNEL_CRITICALITY_FINDINGS.md` — hotspot versus broad Pareto evidence.
- `CROSS_LAYER_DEEP_DIVE.md` — exact counter chain and its causal limits.
- `SEGMENT_BREAK_EVEN_FINDINGS.md` — measured finite differences and brackets.
- `SUBENTRY_EFFECTIVENESS_AUDIT.md`, `PWC_TRADEOFF_AUDIT.md`, and
  `LAYER_ROBUSTNESS_FINDINGS.md` — negative-result and robustness audits.
