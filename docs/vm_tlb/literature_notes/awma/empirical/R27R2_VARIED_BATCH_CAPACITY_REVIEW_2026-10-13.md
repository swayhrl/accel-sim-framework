# R27R2 varied-batch tied-W capacity: independent scientific review

Review date: 2026-10-13 (Asia/Shanghai)
Execution date: 2026-10-03 (Asia/Shanghai)

Execution branch: `hrl/awma-r27r2-varied-batch-capacity-109-v1`

Execution commit: [`ba73fa0bacf3db09f44d8ad421a0a36f56645898`](https://github.com/swayhrl/accel-sim-framework/commit/ba73fa0bacf3db09f44d8ad421a0a36f56645898), tree `6988b03184c909123b6a8dfae082e07202cd808b`.

Handoff parent: `578615d953b9c286cbafada997b3ed09217140a6`, tree `777ffacbcc3dfd6cdad6f77acb591f5f3a041102`.

Review pack: [AWMA_R27R2_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1](https://github.com/swayhrl/accel-sim-framework/tree/ba73fa0bacf3db09f44d8ad421a0a36f56645898/docs/vm_tlb/review_packs/AWMA_R27R2_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1).

## Decision

**Accept the STOP classification** `R27R2_NUMERIC_OR_STATE_NOT_QUALIFIED`.

The exact external WikiText-2 train file and immutable token bank passed source/identity checks. B1's prescribed, pre-freeze, same-start comparison against B0 **did not** pass the unchanged `rtol=atol=1e-2` complete-total-gradient contract for either C1 or S2 on any of the four varied steps. At C1 step 4, FP32 first moment `m` also fails the prescribed per-element criterion. These failures are sufficient to STOP before implementation freeze or capacity trials. Fresh-process checkpoint load and a C1-to-S2 switch passing cannot override the B0-comparison failures.

R27R2 establishes **no varied-input batch-capacity result**. It is not a capacity regression/negative; it neither strengthens nor invalidates R26's separate repeated-input one-physical-batch observation.

## Git, lineage, and evidence

I independently checked GitHub Git-commit/tree/ref and compare metadata. The execution commit is the **single direct child** of the frozen handoff HEAD; `hrl/awma-r27r2-varied-batch-capacity-109-v1` points at this exact commit/tree. R27/R27R1 are not rewritten in the execution diff.

I independently recomputed SHA256 over the **18 Git review-pack files** listed in the committed `SHA256SUMS`: **18/18 match**. I also recomputed the SHA of the `SHA256SUMS` file itself:

`b8ba543e8aa78c254e5780c12c9276cdd0049c9ec422d3f937a62d1b78b79e91`

This matches the Lane G receipt.

I independently parsed `B1_NUMERICAL_QUALIFICATION.json`, `B1_NUMERICAL_QUALIFICATION.tsv`, `FIRST_MISMATCH.json`, `B1_CHECKPOINT_SWITCH_QUALIFICATION.json`, the frozen numerical comparator, and R26/R25 compact-embedding source. TSV has 72 data rows corresponding to two policies × four steps × nine observables, and agrees with the JSON-level qualification flags. I did **not** independently read node164's raw bytes or replay GPU tensor computations in this review; the node164 95-item readback and GPU-lock/process/worktree cleanliness remain **execution-side receipts**.

## Exact input and bank

`EXACT_INPUT_ADMISSION.json` reports:

- public source: `Salesforce/wikitext@8aaa8b27d493dba10b8553290236799e6dc57829`;
- raw train parquet: 6,357,543 bytes;
- SHA256: `e83889baabc497075506f91975be5fac0d45c5290b6b20582c8cd1e853d0c9f7`;
- no byte transformation/Parquet reserialization; node164 readback PASS;
- no network retries in R27R2.

`BANK_AUTHORITY.json` reports 36,718 physical parquet rows, joined-text SHA256 `c58d555a94ada0882d1e8c0b3dc7ba68e1c269da5ad9e7a057300245d130c4e8`, 2,435,023 tokens, first 540,672 IDs, CPU int64 bank `[33,128,128]` and all 4,224 windows distinct. Raw bank SHA256:

`7ad359882a1a7153cd7c0d9321af53ac38fa17908cff1355a89696aec2c61387`.

The frozen tokenizer identity is inherited from accepted Llama assets. These input/bank assets are now reusable under a future **newly reviewed** contract; their use does not restore authority to the terminated R27R2 experiment.

## B1 numerical evidence

The comparator's elementwise condition is:

`abs(candidate-reference) <= 0.01 + 0.01 * abs(reference)`.

This is not a global max-absolute-error-only test. The following values are recomputed from the published per-step JSON, not from a capacity run:

| Trajectory index | C1 total grad max abs | S2 total grad max abs | C1 vs B0 gradient | S2 vs B0 gradient |
| --- | ---: | ---: | --- | --- |
| 1 | 0.09375 | 0.09375 | FAIL | FAIL |
| 2 | 0.046875 | 0.0263671875 | FAIL | FAIL |
| 3 | 0.03125 | 0.03125 | FAIL | FAIL |
| 4 | 0.078125 | 0.05078125 | FAIL | FAIL |

The first mismatch is C1, trajectory index 1, total BF16 W gradient, shape `[128256,2048]` (262,668,288 elements), max_abs `0.09375`, mean_abs `1.7996148938119564e-7`, cosine `0.999939425779327`. Allclose is false. The extremely large `max_rel` values arise from dividing by `abs(reference).clamp_min(1e-30)`; they must not be presented as a global relative-error magnitude.

C1's step-4 FP32 moment `m` has max_abs `0.014644771814346313` and also fails allclose. Other reported loss, dH, W, v, counter/cursor and most state checks pass. The same-source fresh checkpoint load and C1↔S2 switch comparison pass, but that is a **C1/S2 pair**, not a B0 equivalence certificate.

The global mean absolute error across a mostly sparse `128256×2048` gradient and high cosine do not negate individual tolerance failures. No reported raw evidence yet gives the *number, coordinates, token identities, or decomposition* of failing elements. Thus neither numerical harmlessness nor a specific bug is proven.

## Source-based hypothesis, explicitly not a finding

Source inspection gives one useful place to look first:

- B0: native dense embedding backward directly into `W.grad`, then adds the CCE classifier gradient.
- C1/S2: shared `R25CompactEmbedding.backward` uses sorted unique token IDs and inverse remapping, runs `aten.embedding_dense_backward` over the compact domain, then merges the compact lookup gradient into full/tiled classifier gradient via `index_add_`.
- C1 and S2 first-step total gradients both show max_abs `0.09375` relative to B0; at an already-shared checkpoint C1↔S2 switch the reported gradient comparison passes.

That makes the common compact lookup reduction/merge a **priority hypothesis**, potentially involving BF16 accumulation order or duplicate-token row semantics. It does **not** prove the cause. The split/full/tiled CCE gradient implementations and same-input baseline numerical repeatability are other possibilities.

R26 repeated-sequence B1 qualification passing does not prove that the compact path matches B0 at every varied input. Nor does R27R2 failure prove a general numerical problem in all inputs or models.

## Engineering and closure

The execution records two ordinary engineering events:

1. the external exact-byte file was already on node109 under a neutral authority path and was copied/reflinked to the contract staging path, then rehashed and durably admitted;
2. an initial Python module-name collision prevented import before CUDA. The runner subsequently used a unique exact-R26 module name and completed B1.

The B1 qualification process's non-zero exit did not propagate through a shell pipeline using `tee`, so the already-authorized fresh-load/switch subgate ran and passed. The source records this rather than disguising it. No freeze/capacity/Gate D or Gate E was opened. In a next task, require `set -o pipefail` and fail-closed gate dispatcher, while preserving the independently useful switch result as a bounded diagnostic rather than promotion evidence.

The node164 publication receipt reports 95/95 readbacks, archive SHA256 `e05be636c97cafa4191b1995ca4ae6e77b9d786211d3ae622f49d73a9b8a9ce0`, manifest SHA256 `2a5dcb809f38182012c8f997f78c7364826e616231c40c1dd8e2fed8277c5e9a`. It explicitly records both input and bank admitted. The GPU lock receipt covers the B1 attempts, reports zero capacity GPU campaigns, and states the lock and campaign process are closed. These remain execution-side attestations in this reviewer environment.

## Next decision — not yet authorized

Do **not** restart capacity, retry downloads, re-tokenize, swap corpus, or relax the 1e-2 tolerance to force success.

A justified next Goal would combine the following *conditional* gates to minimize round trips:

1. **Read-only prediagnosis.** Reuse the immutable R27R2 bank, R26 start and existing numerical receipts. Check whether exact failing tensor indices / component-wise gradients survived in immutable raw; do not reconstruct them from mean/cosine or invent locations.
2. **Small B1 native diagnostic only if needed.** Under the GPU flock, compare same-seed B0-vs-B0 repeatability and controlled B0/C1/S2 on one fixed B1 bank step. Record the number and actual coordinates/values of tolerance failures and affected token frequencies; separate classifier total gradient and embedding lookup gradient, including a shared-dH control. A high-precision or deterministic reducer may be used as a *diagnostic reference* without changing production semantics.
3. **One evidence-driven correction only if a correctable implementation defect is localized.** Do not blindly scan kernels, tiles, seeds, precision or tolerances; check that the change preserves intended tied-W mathematics, data and optimizer, and account for any new storage/performance cost. Treat changed numerical implementation as a new experimental candidate, not an implicit rewrite of R26.
4. **Continue in the same new Goal only after the unchanged four-step `1e-2` B0/C1/S2 gradient/state requirement passes.** Then implementation freeze → bounded natural capacity → 3/3 endpoints → positive-only 32-step/resume → publication. If the mismatch is inherent and cannot be remedied under a defensible contract, STOP with the bounded negative/qualification outcome, without exploratory capacity probing.

A future change to the numerical equivalence *definition* would require a separate justified, predeclared scientific contract and a fresh evaluation, not a post-hoc reinterpretation of R27R2.

## Current research boundary

R26 stays the latest accepted tied-W batch-capacity observation, limited to one repeated physical input sequence. R27/R27R1 were input availability STOPs. R27R2 qualified the varied source/bank but failed pre-freeze B1 numerical equivalence. None supplies a varied-input capacity boundary.

No new AWMA GPU Goal is authorized by this review. C16 Stage A and DTC-L1 remain independent.
