# Status after R27R2 numerical review

Review date: 2026-10-13 (Asia/Shanghai)
Execution date: 2026-10-03 (Asia/Shanghai)

This supersedes `STATUS_AFTER_R27R2_AUTHORIZATION_2026-10-03.md` **only for current AWMA activity**. Do not rewrite the R26/R27/R27R1/R27R2 historical Goal or result branches.

## Current activity

- Lane G / node109 R27R2: **COMPLETE / STOP**.
- Accepted classification: `R27R2_NUMERIC_OR_STATE_NOT_QUALIFIED`.
- Exact seed and node164 admission: PASS (execution readback).
- Immutable fixed 33×128×128 token bank: PASS (execution readback).
- B1 B0/C1/S2 four-step numerical qualification: **FAIL**. Both C1 and S2 violate the unchanged elementwise complete-total-gradient contract on all four varied steps. C1 FP32 first moment also fails at step 4.
- Fresh-process checkpoint load and C1↔S2 switch: PASS within its narrower scope, does not override B0 failures.
- `IMPLEMENTATION_FREEZE`: NOT CREATED.
- Gate C / capacity, Gate D / 32-step, Gate E / diagnostic: NOT RUN.
- No formal timing/profiling, node174/Accel-Sim, hardware/PPA or production change.
- GPU lock released; no campaign CUDA processes per execution receipt.
- **No current AWMA GPU Goal authorized by this review**.

## Exact execution authority

Branch: `hrl/awma-r27r2-varied-batch-capacity-109-v1`

Commit: `ba73fa0bacf3db09f44d8ad421a0a36f56645898`

Tree: `6988b03184c909123b6a8dfae082e07202cd808b`

Direct handoff parent: `578615d953b9c286cbafada997b3ed09217140a6`

Accepted scientific review:
[`R27R2_VARIED_BATCH_CAPACITY_REVIEW_2026-10-13.md`](../empirical/R27R2_VARIED_BATCH_CAPACITY_REVIEW_2026-10-13.md)

Execution review pack:
https://github.com/swayhrl/accel-sim-framework/tree/ba73fa0bacf3db09f44d8ad421a0a36f56645898/docs/vm_tlb/review_packs/AWMA_R27R2_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1

## Reusable exact data authority

Required source:
- `Salesforce/wikitext@8aaa8b27d493dba10b8553290236799e6dc57829`
- `wikitext-2-raw-v1/train-00000-of-00001.parquet`
- 6,357,543 bytes, SHA256 `e83889baabc497075506f91975be5fac0d45c5290b6b20582c8cd1e853d0c9f7`

Frozen input bank:
- 36,718 parquet rows, 2,435,023 tokens total;
- first 540,672 IDs → `[33,128,128]` CPU int64;
- 4,224 / 4,224 distinct windows;
- raw tensor SHA256 `7ad359882a1a7153cd7c0d9321af53ac38fa17908cff1355a89696aec2c61387`.

The node164 input/bank admission and 95-item publication manifest were reported PASS. ChatGPT independently verified the Git review pack 18/18 SHA entries, but did not SSH-read node164's bytes.

These identities are now available for re-use **under a new reviewed contract**. They are not an authorization to restart R27R2.

## Present scientific decision

R26 remains the latest accepted capacity observation: one physical-batch extension on a repeated sequence with tied-W-only training. R27/R27R1 did not reach varied-input execution. R27R2 does not provide a varied-input batch capacity boundary because B1 comparison failed before freeze.

The remaining question is **why the common compact C1/S2 numerical paths disagree with B0 in the sparse BF16 full-gradient comparison on varied B1 steps**, and whether the discrepancy is a correctable semantic/implementation defect, repeatability effect, or inherent floating-point order effect. No root cause has been accepted.

Prioritize the native dense-lookup versus sorted-unique compact embedding-backward/merge and CCE classifier gradient paths, but keep these as hypotheses until controlled component-level observations are recorded. Do not infer numerical harmlessness from cosine/mean error or change the preset tolerance after seeing failures.

## Conditional follow-up, not authorized yet

Prepare at most one compact Goal: read-only evidence first; if needed one bounded B1 native repeatability/component-attribution diagnostic under node109 flock; one defensible semantic-preserving fix if localized; only after the original `1e-2` four-step qualification passes may the same new Goal continue to freeze, bounded capacity, 3/3 endpoint confirmation and positive-only 32-step/resume. Otherwise STOP and preserve negative/uncertainty. Fail-closed shell pipeline (`pipefail`) is mandatory.

Do not create a third source-acquisition attempt, reset the frozen bank, blindly tune tolerances/precision, or automatically launch capacity after a numerical failure.

C16 Stage A and DTC-L1 remain separate, with no borrowed authorization.
