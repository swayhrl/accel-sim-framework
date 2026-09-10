# C12 Operator-aware characterization — interim review pack

## Status

`C12_OPERATOR_AWARE_INTERIM_READY_WAITING_C12_FINAL`

This is a read-only, independently-worktreed analysis.  The C12 source was
fetched at `269c274712f4eeaee15d304033a9e6d61b5b3206`: 20 arms are terminal
`PASS`; `Prefill F1` and `Prefill F8-Lseg20` are still `PENDING`.  Decode1 is
complete (11/11) and has been fully analyzed.  No simulator replay was
started, and no C12 raw evidence, trace, config, registration, binary, Core,
worker, scheduler, or finalizer was modified.

## OA0--OA4 closure

- OA0: List SHA identity, manifest/NCCL filtering, embedded semantic header,
  marker index, and SimVA/`weight_layout` namespace checks all pass.  See
  `PROVENANCE.md`, `OBSERVABILITY_AUDIT.md`, and `INDEX_ALIGNMENT_AUDIT.tsv`.
- OA1: Every 692/740 compute trace is mapped in `KERNEL_OPERATOR_MAP.tsv`.
  Direct parameter-range evidence takes priority; direct semantic evidence is
  used only for explicit classes such as FlashAttention.  There are no
  heuristic assignments.
- OA2: F0 has exact per-kernel execution, selected translation deltas, and
  KERNEL-scoped cache transactions; trace-derived lane references/page sets
  are kept separately.  `FIXED_WINDOW_PARTIAL` cache observations and
  non-monotonic gauges are not attributed.
- OA3: All 20 terminal-PASS arms have operator cycle and Segment/Sub-entry
  attribution.  The Decode1 F1-vs-F2, F5-vs-F0, F7/F8 Lseg matrix, F8-vs-F7,
  and F8-L10-vs-F9 comparisons are present.  Prefill contains every permitted
  comparison except ones that require its two pending arms.
- OA4: The eight requested questions are explicitly answered with evidence
  tiers in `PAPER_FACING_FINDINGS.md`.

## Primary interim results

1. Exact trace-to-kernel attribution closes at 692/692 Prefill and 740/740
   Decode1.  Formal direct coverage is 99.86% of kernels for both ROIs; the
   remaining kernel per ROI is deliberately unresolved.
2. FFN dominates Attention Projection's direct Weight translation footprint
   in both ROIs (6,158 versus 1,294 unique 64 KiB pages); Embedding/Output is
   a distinct and larger 8,016-page direct range.
3. Decode Weight's zero-L2-hit signature occurs in direct Attention
   Projection, FFN, and Embedding/Output—not in one operator alone.  KV L2
   reuse occurs in Attention Core but also substantially in output, FFN, and
   generic compute classes.
4. Segment timing sensitivity is mainly FFN plus Embedding/Output.  Decode
   sub-entry records activity but no measured F8-over-F7 cycle delta; Prefill
   F8-over-F7 deltas are below 0.03% at the two terminal Lseg values.

The detailed sources are the typed TSVs in this directory.  Their additive
closure against immutable C12 F0 validation sidecars is documented in
`CONSERVATION_AUDIT.md`.

## OA5 handoff condition

Continue read-only polling of `origin/hrl/vm-m4b-speculative-v0`.  Once it
publishes final 22/22 terminal `PASS` and the final C12 review state, rerun
the same parser against that source commit and add only the two newly terminal
Prefill arms.  Until then, this interim result is complete for all available
formal evidence.
