# Window C — SPECULATIVE M4B DEVELOPMENT current handoff

Status: `C12_C5_FULL_ROI_FAIR_PERFORMANCE_AUTHORIZED` / `SPECULATIVE_CANDIDATE` / `REFERENCE_APPROX_SUBENTRY_16`.

C11 has passed review and closed the full-ROI prefill/decode1 provenance gate. C5 full-ROI execution is now authorized under C12, subject to the frozen preflight and acceptance rules below.

## Frozen C11 execution identity

- C11 evidence closeout: `a082f73ad752bbf9beb630ede036d80ecf266f35`
- Runtime/config functional anchor: `d64408a97d76a320a6d49468653d416e33677af8`
- Core: `57bb71ecd015b6ec0ab32e45b0815e5beaf69172`
- Linked binary SHA-256: `2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a`
- Prefill trace-list: `a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f` (692 entries)
- Decode1 trace-list: `b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc` (740 entries)
- PA contract: `C5_MODELED_PA_HIGH_UNUSED_BIT_V1`, explicit `MODELED_DRIVER_PA`, common across fair arms for each ROI.

## Current authorized Goal

`C12_C5_FULL_ROI_FAIR_PERFORMANCE_REPLAY`

Read and execute:

- `docs/vm_tlb/codex_handoff/spec_m4b/C12_C5_FULL_ROI_FAIR_PERFORMANCE_GOAL.md`
- `docs/vm_tlb/codex_handoff/spec_m4b/C12_ACCEPTANCE_MATRIX.md`
- `docs/vm_tlb/codex_handoff/spec_m4b/C12_RESULT_SCHEMA.tsv`
- C11 review pack, especially `C5_ARM_MATRIX.tsv`, `C5_COMMAND_MANIFEST.tsv`, `C5_ACCEPTANCE_MATRIX.md`, and `COMMON_PA_FAIRNESS_VALIDATION.tsv`.

Primary matrix: 22 points = F0/F1/F2/F5/F9 plus F7/F8 at Lseg 5/10/20, for both prefill and decode1.

Execution priority:

1. P0: both F0 baselines and resource calibration;
2. P1: F2/F5/F7-L10/F8-L10/F9 for both ROIs;
3. P2: F7/F8 Lseg 5/20 sensitivity;
4. P3: both F1 points.

The Goal must continue through 22/22 terminal PASS unless a genuine architecture/provenance/correctness blocker is proven. Resource waits, ordinary engineering failures and individual arm crashes are diagnose/retry conditions, not final stop states.

Do not run F6, F3, F4, H0, KV segmentation, 12K or M5. Do not modify Window A/B.

Final Goal state is one of:

- `C12_C5_FULL_ROI_COMPLETE_READY_FOR_REVIEW`
- `C12_C5_HARD_BLOCKER_WITH_EVIDENCE`
