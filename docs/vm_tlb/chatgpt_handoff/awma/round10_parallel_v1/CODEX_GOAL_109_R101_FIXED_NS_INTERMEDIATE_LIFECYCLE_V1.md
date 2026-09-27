# CODEX GOAL — AWMA R101 Fixed Newton–Schulz Intermediate Lifecycle V1

## Mission

Execute one bounded native exploration on node109:

`AWMA_R101_FIXED_NS_INTERMEDIATE_LIFECYCLE_V1`

Scientific question:

> For the same fixed finite Newton–Schulz map and the same input tile, how much cost is created by materializing iteration intermediates through the normal multi-kernel path, and does that cost remain material for real Qwen-derived optimizer matrices after the author's strongest batching/compile/graph software organization?

This is not a HiMuon algorithm comparison and not a training-quality study.

Repository:
`swayhrl/accel-sim-framework`

Coordination branch:
`hrl/awma-round10-parallel-exploration-handoff-v1`

Execution branch:
`hrl/awma-r101-fixed-ns-intermediate-lifecycle-v1`

Accepted base:
`d6ef29505de75985181afc74dffc3cf1b652afc2`

Literature:
`hrl/awma-chatgpt-literature-notes-v1 @ 1dcf2cc9e4409010ec7f49d8afbefe0194ba0a8f`

Read:
- `docs/vm_tlb/chatgpt_handoff/awma/round10_parallel_v1/START_HERE.md`
- `docs/vm_tlb/literature_notes/awma/rounds/2026-09-27_ROUND_10_HORIZONTAL_REVIEW_AND_NEXT.md`

Node:
109 / RTX4080 / SM89.

All CUDA work must hold:
`/data/c16/locks/c16_gpu_campaign.lock`

Do not use node174 or Accel-Sim in this Goal.

---

# 1. Pin the closest software source

Fetch exactly:

- repo: `tang0389/himuon`
- commit: `af89eda9a0176effed99e1fe19cc1f8a1a2c9588`

Hash and record at least:

- `src/himuon/optimizers/himuon.py`
- `src/himuon/triton_kernels/ns5_smem.py`
- `microbench/experiments/exp_ns5_rect_bench.py`
- `tests/integration/test_himuon_dispatch.py`
- `tests/integration/test_himuon_self_consistency.py`

Important source facts to verify rather than assume:

- cross-layer bucket batching exists;
- bucket plan and concat buffers are cached;
- optimizer-step CUDA graph exists;
- small admitted tiles can use fused `ns5_smem`;
- the larger fixed finite map uses the compiled 3-kernel path;
- the author's microbench itself compares the fused path with an equivalent finite 3-kernel NS implementation.

Do not claim novelty from batching, persistent launch, CUDA graphs, or tile-local HiMuon.

Create:
`R101_SOURCE_RECEIPT.json`.

---

# 2. Reuse an accepted model; no new model download

Use only:

`Qwen/Qwen2.5-0.5B-Instruct`

Accepted revision:
`7ae557604adf67be50417f59c2c2f167def9a775`

Expected accepted model weight SHA256:
`fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe`

Locate an already accepted local/node164 asset from prior AWMA work and verify identity.

Do not redownload if an accepted exact-hash copy exists.
If no exact accepted asset is accessible, STOP:
`R101_INPUT_NOT_QUALIFIED_V1`.

---

# 3. Build a real gradient-derived optimizer microstate

Do not use random matrices as the primary scientific input.

Use raw prompt text from the accepted R53 request authority:

`docs/vm_tlb/review_packs/AWMA_R53_ONLINE_WORKSET_QUALIFICATION_V1/REQUEST_SELECTION.tsv`

Construct one deterministic text stream in its accepted row order using separator:

`\n\n---\n\n`

Tokenize with the accepted Qwen2.5 tokenizer:
- no chat-template mutation;
- `add_special_tokens=False`.

Freeze before GPU gradient generation:

- `TRAIN_DISCOVERY_256`: first 256 token IDs;
- `TRAIN_HOLDOUT_256`: token IDs [256:512], cycling the text stream only if required.

Record exact token hashes.

For each fixture independently:

1. load the unchanged accepted Qwen2.5 model in BF16;
2. run one standard next-token cross-entropy loss:
   - input = tokens[:-1]
   - labels = tokens[1:]
   - no label smoothing;
3. backward once;
4. do **not** update model parameters;
5. capture gradient tensors for the frozen parameter roles below;
6. construct the exact first-step HiMuon Nesterov input from zero momentum:
   - `buf = grad`
   - `G = grad + 0.95 * buf`
   - therefore `G = 1.95 * grad`
   following the pinned author's `_compute_momentum` semantics.

This is explicitly:
`REAL_MODEL_FIRST_STEP_GRADIENT_DERIVED_MICROSTATE`.

It is not a claim about converged training or a multi-step natural momentum distribution.

Frozen discovery parameters:

- `model.layers.0.self_attn.q_proj.weight`
- `model.layers.0.mlp.up_proj.weight`
- `model.layers.0.mlp.down_proj.weight`

Frozen holdout parameters:

- same three roles at layer 12.

If exact names differ because of a wrapper prefix only, resolve the deterministic fully-qualified names and document the mapping.
Do not substitute different operators based on measured performance.

Create:
- `R101_INPUT_RECEIPT.json`
- `R101_GRADIENT_MICROSTATE_RECEIPT.json`

Store tensors on node164; do not commit large tensors to Git.

---

# 4. Freeze numerical contract before performance

The finite NS coefficients and step count come exactly from the pinned HiMuon source.

Use:
- BF16 input tiles;
- 5 Newton–Schulz iterations;
- same author coefficients;
- no step-count reduction;
- no alternate polynomial;
- no tile-local algorithm change after results.

Create FP32 eager reference using the author's microbench formula.

For an equivalent implementation pair on the same tile input:

Required gates:

1. same shape;
2. finite;
3. cosine similarity versus FP32 reference recorded;
4. fused and 3-kernel output comparison uses the author's already-declared self-consistency tolerance:
   - `rtol=1e-2`
   - `atol=1e-2`
5. max/mean absolute difference recorded.

Do not introduce a new tolerance after observing results.

---

# 5. Frozen tile populations

Use the author's exact tiling/padding semantics.

Do not compare different tile sizes as mathematically equivalent optimizer maps.

## S128 — same-map mechanism control

From all three discovery momentum matrices, tile with:

`128 x 128`

Collect **all** resulting padded tiles in deterministic parameter/tile order.

This tile shape is intended to be eligible for the author's fused `ns5_smem`.

Compare on the exact same S128 tile batch:

### F128
Pinned author `ns5_smem`.

### K128
Pinned author-equivalent compiled 3-kernel finite NS path from the microbench / optimizer implementation.

This is the primary mechanism-response comparison:
same input tiles, same finite NS formula, different intermediate-state realization.

## L256 — real large-tile characterization

Tile the same discovery matrices with:
`256 x 256`.

Use the author's strongest legal compiled 3-kernel path.

Do not compare its numerical result directly with S128 as an equivalent algorithm.

## L512 — real default-scale characterization

Tile the same discovery matrices with:
`512 x 512`.

Use the author's strongest legal compiled 3-kernel path.

Again, this is a separate fixed map.

Record:
- tile count;
- padding;
- bytes;
- shapes;
- author dispatch result.

No additional tile size may be added to rescue or amplify a result.

---

# 6. Correctness and source-path canaries

Before formal timing:

- prove F128 and K128 both execute the intended source paths;
- close their numerical contract;
- prove L256/L512 use the intended compiled 3-kernel path;
- record actual Triton/CUDA kernel identities;
- ensure no unexpected CPU fallback.

If S128 fused-vs-3kernel numerical contract fails:
`R101_MECHANISM_CONTROL_NOT_QUALIFIED_V1`
and do not use their timing as causal evidence.

L256/L512 may still be characterized only as source/runtime observations, not promoted.

---

# 7. Formal operator timing

For each qualified arm:

- 1 canary;
- 2 warmups;
- 7 formal repetitions;
- paired/interleaved F128/K128 ordering;
- keep input/output buffers stable where legal;
- no profiler in formal timing.

Measure:

- complete call GPU time;
- kernel count;
- host elapsed as secondary;
- peak allocation.

Material mechanism response on S128 requires:

- median improvement of F128 over K128 >=5%;
- improvement >3x the larger relative jitter/noise envelope;
- numerical contract passes.

Do not infer the large-tile speedup from this result.

---

# 8. Strong-software large-tile baseline

For L256 and L512, ensure the baseline includes the author's relevant software capabilities where applicable:

- cross-layer batching;
- cached bucket plan;
- reused concat buffers;
- `torch.compile`;
- CUDA graph when the measured scope legally supports it.

Do not compare only against an intentionally eager per-parameter implementation.

Create a fixed selected-parameter optimizer replay using the captured real gradients/microstate.

Purpose:
quantify whether the large-tile finite NS path is material inside the selected real optimizer work, not to simulate full training convergence.

Record:
- full selected optimizer replay time;
- NS-related kernel time/launches;
- L256/L512 intermediate storage/accounting;
- relative fraction.

If graph timing changes values across repeated replay, that is acceptable only when shapes/control path remain identical; correctness is established on the first frozen-state canary.

---

# 9. Intermediate-state accounting

For the 3-kernel path, derive from exact source and tensor shapes:

per iteration:
- X;
- A = X X^T;
- B;
- C/new X;

and the actual read/write reuse across the pinned implementation.

Separate:
- logical intermediate bytes;
- allocated bytes;
- theoretical compulsory bytes;
- measured DRAM/L2 traffic when available.

Do not simply multiply tensor sizes and call it measured HBM traffic.

If the source reuses buffers, account for it exactly.

---

# 10. Conditional NCU

NCU is authorized only after formal timing if:

- S128 shows a qualified >=5% mechanism response, or
- L256/L512 3-kernel path is a material fraction of the selected optimizer replay.

Maximum 2 profiles.

Before collection create:
`NCU_PREREGISTRATION.md`

Resolve exact supported metric names, targeting:
- DRAM read/write bytes;
- L2 bytes where source-correct;
- active cycles;
- occupancy/register/shared only as explanatory data.

Profile:
- one K128 or F128 pair representative arm;
- one L512 3-kernel arm.

Do not use NCU replay time as primary timing.

---

# 11. Holdout

Only if the discovery evidence is strong enough to consider architecture review.

Use:
- `TRAIN_HOLDOUT_256`;
- layer12 q/up/down first-step gradient-derived microstate;
- same S128/L512 configurations selected before holdout.

No tuning on holdout.

Required:
- S128 same-map mechanism response direction survives;
- L512 cost/materiality interpretation survives;
- numerical contract remains valid.

---

# 12. Interpretation states

Choose exactly one final state:

### `R101_INPUT_NOT_QUALIFIED_V1`
accepted model/gradient microstate cannot be established.

### `R101_MECHANISM_CONTROL_NOT_QUALIFIED_V1`
same-map fused/3-kernel correctness cannot close.

### `R101_FIXED_MAP_INTERMEDIATE_COST_LOW_V1`
S128 same-map response and/or real L256/L512 cost is too small to justify further work.

### `R101_AUTHOR_SOFTWARE_SUFFICIENT_V1`
author batching/compile/graph already closes the relevant cost.

### `R101_MECHANISM_PROXY_ONLY_V1`
S128 proves on-chip intermediate retention is beneficial, but the real large-tile path is not material enough or cannot be causally tied to a surviving workload-level cost.

### `R101_HOST_RUNTIME_COST_NOT_ARCH_LOCALIZED_V1`
remaining material difference is dominated by launch/host/software organization rather than GPU intermediate traffic.

### `R101_INTERMEDIATE_RETENTION_READY_FOR_ARCH_REVIEW_V1`
Allowed only if all hold:
1. real Qwen-derived gradient/momentum input;
2. strong author software baseline;
3. S128 same-map fused-vs-3kernel material stable mechanism response;
4. real large-tile L256/L512 3-kernel path has material cost;
5. evidence localizes that cost to inter-iteration GPU intermediate materialization, not host launch;
6. independent layer12 holdout supports the interpretation;
7. closest-work audit does not reveal an already-equivalent capability.

READY does not authorize a simulator or hardware implementation.

---

# 13. Publication

Durable root:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r101_fixed_ns_intermediate_lifecycle_20260927/`

Review pack:

`docs/vm_tlb/review_packs/AWMA_R101_FIXED_NS_INTERMEDIATE_LIFECYCLE_V1/`

Minimum:
- README.md
- SOURCE_AND_CLOSEST_WORK_AUDIT.md
- ENVIRONMENT_RECEIPT.json
- MODEL_IDENTITY_RECEIPT.json
- R101_INPUT_RECEIPT.json
- R101_GRADIENT_MICROSTATE_RECEIPT.json
- PREREGISTRATION.json
- TILE_POPULATIONS.tsv
- NUMERICAL_QUALIFICATION.tsv
- OPERATOR_TIMING.tsv
- LARGE_TILE_ACCOUNTING.tsv
- OPTIMIZER_REPLAY_RESULTS.tsv
- conditional NCU_DIAGNOSTIC.tsv
- conditional HOLDOUT_RESULTS.tsv
- R101_DECISION.md
- FINAL_DECISION.md
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Closure:
`science/engineering -> node164 -> review pack -> hashes -> commit -> push -> fetch-back -> exact remote SHA/tree -> clean -> GPU released -> STOP`.

No auto merge.
