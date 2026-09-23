# AWMA AI Translation Representative Suite Design V1 Report

Status: **PROVISIONAL_PRE_GATE**
Stage: AWMA_AI_TRANSLATION_REPRESENTATIVE_SUITE_DESIGN_V1

Window D publishes a deterministic selector and a V1 provisional suite at
docs/vm_tlb/review_packs/AWMA_AI_TRANSLATION_REPRESENTATIVE_SUITE_DESIGN_V1.

The exact V1 input is the accepted Qwen2.5 S2 per-launch inventory:
34,677 records; SHA-256
7825697aa23647daee6a38ac4436029c5746fe29a468d303520d3884f2b4abef.

The selector stratifies Prefill/Decode/UNKNOWN phase, normalized family, exact
implementation, grid/block shape, and measured Decode-step behavior. It selects
on accumulated Native GPU duration while preserving implementation/shape
diversity and force-including measured long/ordinary Decode GEMV, Flash, and
Prefill GEMM variant strata. It does not infer operator semantics from names.

The identity-only deterministic split reserves 6,902 records for validation;
the selector neither observes their duration nor uses them to tune selection.
Two exact re-runs produced identical selected-suite and holdout files.

The selection pool contains 126,743,918 ns; selected strata cover 68,482,853 ns
(54.03%). The nominal 24-member budget is exceeded by 52 forced material or
structural strata, and that conflict is intentionally review-visible.

This result remains provisional until Window A replaces V1 phase/context fields
with the corrected V2 census and Window C attaches simulator-native trace asset
status. V1 cannot source-support splitkv/combine tags, so those are retained as
uncovered low-confidence requirements. No new trace was captured or requested.
