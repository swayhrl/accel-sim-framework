# C12 operator-aware mechanism deep dive — latest handoff

## Final status

`C12_OPERATOR_AWARE_MECHANISM_DEEP_DIVE_COMPLETE_READY_FOR_REVIEW`

The deep dive is complete at review-pack commit
`484663a46b3810df24b31d8f97cd9cdb671ed91b`, based solely on final formal C12
source `a268aba0d01310294074ded5bb8017e2092394c0` (22/22 terminal PASS).

## Delivered analysis

- DD1: exact per-kernel rankings and Pareto curves for all 12 requested arm
  comparisons.
- DD2: exact operator/kernel counter decomposition, retaining KERNEL metrics
  separate from FULL_ROI_ONLY observations and treating associations as
  non-causal.
- DD3: only measured finite differences and in-range piecewise-linear
  break-even brackets: approximately Lseg 8.75--8.76 for Prefill and 10.83
  for Decode at full ROI.
- DD4: Sub-entry activity has no Decode cycle effect (F8/F7 is exactly equal
  at all 740 markers and all three Lseg values); Prefill F5/PWC regresses by
  733,075 cycles while PWC hits increase, with kernel 691 contributing
  700,253 cycles.
- DD5: direct-range layers 0--15 show broad FFN/Attention-Projection/Norm
  behavior rather than a single-layer artifact.

## Key evidence and limits

- Prefill F1/F2, F5/F0, and F7-L10/F0 are dominated by final
  Embedding/Output kernel 691; several other Segment comparisons, particularly
  Decode, are distributed across substantially more markers.
- No claim is made that a translation or cache association is a unique causal
  critical path. Unresolved outcomes, missing F7 Sub-entry fields, and
  KV-runtime-range semantics remain explicitly marked in the review pack.
- The parser performed only read-only parsing of the accepted immutable raw
  logs and cached trace-scan/operator-map artifacts. No simulator, replay, or
  trace scan was started, and no formal C12 asset was changed.

## Checks completed

- Python parser compilation passed.
- All 12 required comparison labels occur in each kernel ranking, Pareto, and
  cross-layer table.
- Segment interpolation/non-crossing evidence tags validated.
- Layer robustness rows are direct-parameter-range-only.
- Decode F8/F7 per-kernel cycle identity validated in the Sub-entry audit.

## Review entry point

Start with
`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_OPERATOR_AWARE_MECHANISM_DEEP_DIVE/FINAL_REPORT.md`.
