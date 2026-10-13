# Accepted R27R2 review snapshot for R27R3

Review: 2026-10-13 (Asia/Shanghai); R27R2 execution: 2026-10-03.

## Frozen authority

- Repository: `swayhrl/accel-sim-framework`.
- Closed execution branch: `hrl/awma-r27r2-varied-batch-capacity-109-v1`.
- Execution commit: `ba73fa0bacf3db09f44d8ad421a0a36f56645898`.
- Execution tree: `6988b03184c909123b6a8dfae082e07202cd808b`.
- Exact R27R2 handoff parent: `578615d953b9c286cbafada997b3ed09217140a6`, tree `777ffacbcc3dfd6cdad6f77acb591f5f3a041102`.
- Accepted review: `docs/vm_tlb/literature_notes/awma/empirical/R27R2_VARIED_BATCH_CAPACITY_REVIEW_2026-10-13.md` on `hrl/awma-chatgpt-literature-notes-v1`; review commit `83247d513df1f986b503b3b65d3f4019cc2ce0a2`, status commit `d554bbb543619868ece08b61060de312d217f401`.
- R27R2 review pack: `docs/vm_tlb/review_packs/AWMA_R27R2_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1/`.
- Git review pack: 18/18 entries independently SHA-checked; its `SHA256SUMS` SHA256 `b8ba543e8aa78c254e5780c12c9276cdd0049c9ec422d3f937a62d1b78b79e91`.

## Accepted results

`R27R2_NUMERIC_OR_STATE_NOT_QUALIFIED` — legal STOP before implementation freeze.

- Exact Salesforce WikiText-2 raw train parquet (6,357,543 bytes, SHA256 `e83889baabc497075506f91975be5fac0d45c5290b6b20582c8cd1e853d0c9f7`) was admitted to node164 unchanged.
- Physical parquet row count 36,718, total tokenizer tokens 2,435,023; first 540,672 token IDs form a CPU int64 `[33,128,128]` bank, 4,224/4,224 windows distinct, raw bank SHA256 `7ad359882a1a7153cd7c0d9321af53ac38fa17908cff1355a89696aec2c61387`.
- B1 C1 and S2 complete BF16 total-gradient versus B0 at step indices 1,2,3,4: **8/8 FAIL** under the unchanged elementwise `rtol=atol=1e-2` contract.
- C1 total-gradient max_abs: `0.09375 / 0.046875 / 0.03125 / 0.078125`.
- S2 total-gradient max_abs: `0.09375 / 0.0263671875 / 0.03125 / 0.05078125`.
- First C1 mismatch at trajectory index 1: gradient mean_abs `1.7996148938119564e-7`, cosine `0.999939425779327`, shape `[128256,2048]`, dtype BF16. These aggregate summaries do **not** establish numerical harmlessness.
- C1 step-4 FP32 `m` also FAIL, max_abs `0.014644771814346313`; most loss/dH/W/v and step/cursor checks passed.
- C1↔S2 checkpoint/switch at B1 passed; this is not a B0 equivalence certificate.
- No implementation freeze, capacity search, 32-step/resume, allocator diagnostic, formal timing, production, 174/Accel-Sim or hardware work was run.

## Source-based hypothesis, not a result

Frozen R26 B0 uses native `embedding_dense_backward` into dense `W.grad`, then adds CCE classifier gradient. C1/S2 share `R25CompactEmbedding.backward` with `torch.unique(sorted=True, return_inverse=True)`, compact `embedding_dense_backward`, then `index_add_` merge into full/tiled classifier gradient. Duplicate-token accumulation order / BF16 rounding, compact row remap, CCE classifier path and baseline nondeterminism are hypotheses to **distinguish**, not proven causes.

R27R2 `run_r27r2_campaign.py` saved diagnostic B0 tensors temporarily and deleted them after the numerical comparison. Therefore do not assume those full tensor elements survive on node164; check immutable raw/index first. Deriving failing coordinates from max/mean/cosine is not valid.

## Historical scope

R26 stays the latest accepted batch-capacity observation: one physical-batch distinction using repeated copies of a single input, tied-W-only training, C1 B70 PASS/B71 OOM, S2 B71 PASS/B72 OOM, 3/3 each. Its 32-step B1 numerical qualification used that older input. R27/R27R1 stopped for source availability. R27R2 established new input bank authority but failed B1 numerical comparison. **None supplies varied-input batch capacity evidence.**

R27R2's source and artifacts remain immutable. R27R3 may create a separate, explicitly identified **new correction candidate**, but cannot retrospectively relabel R27R2, alter R26's baseline, or silently relax the numerical contract.
