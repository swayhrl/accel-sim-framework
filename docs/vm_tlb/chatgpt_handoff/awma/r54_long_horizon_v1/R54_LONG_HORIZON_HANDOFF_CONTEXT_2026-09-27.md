# AWMA R54 Long-Horizon Handoff Context — 2026-09-27

## Scope

Primary stage:
`R54_EXACT_RECURRENT_CHECKPOINT_LIFECYCLE_V1`

Question:
For exact recurrent-state prefix checkpoints in a real hybrid Gated-DeltaNet LLM, after strong preallocated asynchronous software snapshot/restore, does checkpoint production or restore remain a material GPU-local cost?

Secondary lane:
`R55_MICROSCALING_PLATFORM_AND_CLOSEST_WORK_AUDIT_V1`
Source-only; no RTX4080 NVFP4 performance claims.

This is designed for a long unattended Codex run. It is not a requirement to consume ten hours: finish and STOP once a valid scientific closure is reached.

## Frozen prior results

R53 accepted:
- branch `hrl/awma-r53-online-legal-workset-native-qualification-v1`
- commit `843ad43ad33153bf73a0e51aed6d8ac309356cae`
- final `R53_ALGORITHM_CHANGE_NOT_MAPPING_GAIN_V1`

Do not reopen R53.

Literature authority:
- `hrl/awma-chatgpt-literature-notes-v1 @ 85ddfac657e6bf2ae99ddd0997d4311f210f341c`
- Round07: `docs/vm_tlb/literature_notes/awma/rounds/2026-09-27_ROUND_07_R54_LONG_HORIZON_SELECTION.md`

## Closest-work boundary

Treat as already-covered:
- Marconi: hybrid/SSM prefix-cache admission/eviction and joint state/KV management.
- Sparse Prefix Caching: exact sparse recurrent checkpoints and suffix recomputation.
- Tail-Replay: approximate state reconstruction without checkpoints.
- TreeWY: snapshot elimination for Gated-DeltaNet speculative verification.
- Persistent-state accelerator / DAMP: active recurrent-state HBM traffic and quantization.

The only candidate here is the lifecycle cost of producing/restoring multiple exact reusable recurrent checkpoints after a credible software implementation.

## Model

Only allowed new model:
`Qwen/Qwen3.5-0.8B`

Required revision:
`c6046cd1f7e2763bf1abf5a5aef6ad7878e10ccb`

Scope is this model on RTX4080/SM89 only.

No second model, offload, driver change, or node174 execution.

## Runtime requirement

Use an isolated environment. Do not mutate accepted C16/R53 environments.

The Gated-DeltaNet path must use a credible optimized CUDA path. Audit actual dispatch/kernels. If only an obvious slow reference fallback remains after two bounded fixes, classify runtime not qualified and do not benchmark checkpoint cost.

## Prefix fixture

Reuse exact raw prompts from accepted R53:
`docs/vm_tlb/review_packs/AWMA_R53_ONLINE_WORKSET_QUALIFICATION_V1/REQUEST_SELECTION.tsv`

Order:
GSM8K discovery0..3, GSM8K holdout4..7, HumanEval discovery0..3, HumanEval holdout4..7.

Join with fixed separator `\n\n---\n\n`, repeat cyclically, tokenize with pinned Qwen3.5 tokenizer and no chat template.

Freeze:
- discovery prefix: first 4096 tokens
- holdout prefix: first 2048 tokens
- suffix A: stream tokens 4096..4607
- suffix B: first 512 tokens from the same prompt list rotated left by 5

This is a prefix-cache micro-workload, not an online cache-hit distribution.

## Exact state authority

Enumerate the real runtime cache/state object. Record every layer field, shape, dtype, bytes, mutation behavior and continuation requirement.

Recurrent checkpoint bundle includes only the GDN recurrent/conv state and required metadata. Full-attention KV is retained separately as existing token-addressable prefix state and is not redundantly copied into every recurrent checkpoint.

Do not infer state fields from paper formulas.

## Primary experiment

All checkpoint-production arms use 512-token prefill chunks.

- P0: chunked512, no checkpoint.
- P1: preallocated synchronous exact recurrent checkpoint.
- P2: preallocated source-correct asynchronous/layer-staggered exact checkpoint.

Fixed checkpoint densities:
- every 512 tokens
- every 2048 tokens

No other density.

P2 may overlap a layer's snapshot copy only after that layer has produced the checkpoint-boundary state, and the source must not be updated before its copy is complete.

Formal discovery on prefix4096:
P0; P1-D512; P2-D512; P1-D2048; P2-D2048.

Each point: one canary, 2 warmups, 7 measured repetitions, GPU lock held.

## Restore

Use the exact token-4096 recurrent checkpoint from P2 plus separately resident full-attention prefix KV.

Measure:
- restore-only;
- restore + suffix A/B;
- live-state suffix A/B controls;
- full-prefix recompute controls.

Restore must preserve exact discrete continuation semantics: cache length/metadata, greedy token sequence, top-8 token set and top1/top2 ordering at the boundary. No post-hoc numeric tolerance.

## Materiality

A cost is material only when >=5% and exceeds 3x run-to-run noise/jitter.

Snapshot production residual is evaluated versus P0.

Restore residual is evaluated relative to the prefix recompute that checkpoint reuse avoids, not merely relative to the short suffix.

Derive amortization for N=1,2,4 prefix reuses from measured terms.

Conditional holdout uses prefix2048 only if a strong-software residual survives discovery.

Conditional NCU: at most two standalone profiles after all semantic/holdout gates.

## R55 side lane

Audit Transformer Engine NVFP4, transposition-invariant FP4, NVIDIA NVFP4 pretraining, Quartet II and MOSS.

Do not run R55 GPU timing on RTX4080.

## Nodes

109: all R54 native work.
164: durable large authority.
174: unused.

Suggested node164 root:
`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r54_checkpoint_lifecycle_20260927/`

## Allowed primary final states

- `R54_RUNTIME_FASTPATH_NOT_QUALIFIED_V1`
- `R54_STATE_AUTHORITY_NOT_QUALIFIED_V1`
- `R54_RESTORE_SEMANTICS_NOT_QUALIFIED_V1`
- `R54_SNAPSHOT_LIFECYCLE_COST_LOW_V1`
- `R54_SOFTWARE_BASELINE_SUFFICIENT_V1`
- `R54_HOST_RUNTIME_COST_NOT_ARCH_LOCALIZED_V1`
- `R54_RESIDUAL_READY_FOR_ARCH_REVIEW_V1`

Only the last state may request later architecture review. It does not authorize simulator changes.
