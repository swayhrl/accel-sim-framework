# CODEX GOAL — AWMA R54 Long-Horizon Exact Recurrent Checkpoint Qualification V1

## Mission

Enter Goal mode and execute continuously to scientific closure.

This is one long unattended round combining:

`source/literature audit -> isolated runtime -> fast-path qualification -> prefix fixture -> exact state authority -> snapshot implementations -> production timing -> restore correctness/timing -> amortization -> conditional holdout/NCU -> R55 source-only audit -> publication closure`

Primary science:
`R54_EXACT_RECURRENT_CHECKPOINT_LIFECYCLE_V1`

Secondary source-only:
`R55_MICROSCALING_PLATFORM_AND_CLOSEST_WORK_AUDIT_V1`

Repository:
`swayhrl/accel-sim-framework`

Branch:
`hrl/awma-r54-long-horizon-handoff-v1`

Accepted execution base:
`843ad43ad33153bf73a0e51aed6d8ac309356cae`

Literature authority:
`hrl/awma-chatgpt-literature-notes-v1 @ 85ddfac657e6bf2ae99ddd0997d4311f210f341c`

Stage:
`AWMA_R54_EXACT_RECURRENT_CHECKPOINT_LIFECYCLE_V1`

Node:
109 / RTX4080 / SM89 only.

No node174.
No Accel-Sim.
No new hardware mechanism.
No second model.

The human intends to leave this run unattended for a long window. Do not stop for routine engineering questions. Solve ordinary build/package/parser/timing issues and continue. Scientific STOP rules remain strict.

The long horizon is not a requirement to consume time. If the science closes early, finish the evidence/publication closure and STOP.

---

# 0. Read before execution

Read completely:

1. `docs/vm_tlb/chatgpt_handoff/awma/r54_long_horizon_v1/R54_LONG_HORIZON_HANDOFF_CONTEXT_2026-09-27.md`
2. `docs/vm_tlb/chatgpt_handoff/awma/r54_long_horizon_v1/R54_MEASUREMENT_CONTRACT_V1.md`
3. literature Round07 at the exact literature authority commit.

Also read the accepted R53 review pack only as frozen prior state. Do not rerun R53.

Create a phase ledger before execution:
- phase
- admission gate
- start/end
- result
- scientific eligibility
- raw path
- next authorized phase

Continue automatically whenever the next phase is authorized by the written gates.

---

# 1. Parallel preparation

Before GPU science, safely parallelize independent CPU/network work:

Lane A:
- inventory node109;
- create isolated R54 environment;
- fetch/pin Qwen3.5 source/runtime requirements;
- download the one allowed model revision.

Lane B:
- parse accepted R53 `REQUEST_SELECTION.tsv`;
- build deterministic prefix/suffix fixture;
- hash all source text/tokens.

Lane C:
- closest-work/source audit for R54;
- R55 source-only audit.

Lane D:
- reuse/test existing C16 hash, publication, NSYS, lock helpers;
- write CPU unit tests for state-schema serialization and timing parsers.

Do not run concurrent formal GPU work.

---

# 2. Environment/model admission

Only model:

`Qwen/Qwen3.5-0.8B@c6046cd1f7e2763bf1abf5a5aef6ad7878e10ccb`

Use an isolated environment.

Resolve compatible package versions using official pinned model/runtime requirements.
Freeze versions before science.

At most two surgical runtime/dependency fixes.

Record:
- model files and hashes;
- revision proof;
- runtime package lock;
- source commits;
- CUDA/driver/GPU.

No offload.
No quantized substitute.
No second model.

If the model cannot execute:
final `R54_RUNTIME_FASTPATH_NOT_QUALIFIED_V1`
with runtime reason, then complete R55 audit and publication.

---

# 3. Fast GDN path qualification

Run a bounded text-only prefill/decode canary.

Audit source and NSYS.

Prove the GDN path uses a credible optimized CUDA recurrent/chunk implementation rather than a plainly slow PyTorch/reference fallback.

Record:
- source path/function;
- runtime condition selecting fast path;
- exact kernels/functions;
- shapes;
- GPU durations;
- fallback flags.

If fast-path qualification fails after two fixes:
`R54_RUNTIME_FASTPATH_NOT_QUALIFIED_V1`.

Do not use slow fallback timing to answer R54.

---

# 4. Freeze prefix fixture and preregistration

Construct the fixture exactly as handoff/contract specify from accepted R53 raw prompts.

Create:
`PREFIX_FIXTURE_RECEIPT.json`

Before any formal production timing, write:
`PREREGISTRATION.json`

It must bind:
- model revision/files;
- runtime package/source identity;
- prefix/suffix hashes;
- 512-token execution chunk;
- D512/D2048 only;
- P0/P1/P2 definitions;
- one canary + 2 warmup + 7 repetitions;
- >=5% and >3x-jitter materiality;
- restore conditions;
- holdout rule;
- N=1,2,4 amortization;
- no parameter sweep.

No modification after formal timing begins except documented deterministic repair of an engineering bug.

---

# 5. Exact state authority

Instrument the real runtime cache/state after a short qualified prefix.

Build:
`R54_EXACT_STATE_SCHEMA.tsv`

Every relevant state field must be classified.

Then implement:
- state extraction;
- preallocated checkpoint buffers;
- exact state restore;
- state/metadata validation.

CPU unit tests:
- schema roundtrip;
- buffer shape/dtype;
- no aliasing;
- all required state fields included.

GPU canary:
- snapshot exact state;
- mutate by legal continuation;
- restore;
- prove the frozen continuation semantics.

At most two bounded state-authority/restore engineering fixes.

If state ownership remains ambiguous:
`R54_STATE_AUTHORITY_NOT_QUALIFIED_V1`.

If exact restore semantics fail:
`R54_RESTORE_SEMANTICS_NOT_QUALIFIED_V1`.

Do not move to performance until this gate passes.

---

# 6. M0/P0 semantic gate

Run:
- M0 monolithic identity diagnostic where supported;
- P0 8x512 chunked, no checkpoint.

Prove P0 is a scientifically valid baseline for the checkpoint arms.

Record:
- final cache length;
- state schema;
- greedy/top8/top1-top2;
- bounded continuation tokens;
- numerical differences.

If P0 changes discrete continuation semantics relative to M0, do not repair by changing the checkpoint density.
Diagnose whether the runtime's supported chunked prefill semantics are invalid for this model.

If no valid 512-chunk baseline exists:
state authority/runtime not qualified; close appropriately.

---

# 7. Implement P1 and P2

## P1

Preallocated synchronous exact D2D recurrent checkpoint.

No timed allocation or clone.

## P2

Source-correct async/layer-staggered checkpoint.

Use a dedicated stream/events and overlap only legal immutable state windows.

One implementation may start from a boundary-async design and improve to layer-staggered within the two engineering-attempt envelope if source audit supports it.

Do not change model arithmetic or checkpoint contents.

Run graph/liveness/state-corruption canaries before timing.

---

# 8. Formal production matrix

Run exactly:

- P0
- P1-D512
- P2-D512
- P1-D2048
- P2-D2048

All formal GPU work holds:
`/data/c16/locks/c16_gpu_campaign.lock`

For each:
- canary;
- 2 warmups;
- 7 formal reps.

Use interleaved order when possible.

Collect:
- primary total elapsed;
- compute completion;
- checkpoint-ready completion;
- checkpoint bytes;
- D2D copy GPU time;
- copy-compute overlap;
- host orchestration;
- peak memory;
- one NSYS canary.

Do not run NCU.

Analyze immediately.

If P2 is <5% overhead at both densities:
R54 likely software/low-cost; still complete restore because exact restore is a separate lifecycle component.

If P2 >=5% stable:
mark production residual provisional only; continue restore.

---

# 9. Restore semantic/timing matrix

Prepare exact token-4096 recurrent checkpoint and separate full-attention prefix-KV authority.

Run semantic canaries first for suffix A and B.

Then formal conditions defined in measurement contract:
- R0
- R1A/R1B
- L1A/L1B
- full recompute controls as needed.

Each:
- canary;
- 2 warmups;
- 7 repetitions.

Primary incremental restore:
`restore+suffix - live suffix`.

Qualify cost relative to avoided prefix recompute.

If restore semantic gate fails after one repair:
`R54_RESTORE_SEMANTICS_NOT_QUALIFIED_V1`.

---

# 10. Amortization

Using measured terms only, compute N=1,2,4.

Report separately:
- D512
- D2048

Include:
- production cost;
- restore cost;
- suffix;
- full prefix recompute;
- bytes/checkpoint;
- total checkpoint storage;
- break-even N.

No claim about real cache-hit probability.

---

# 11. Conditional holdout

Trigger only if strong P2 production or restore has stable >=5% residual.

Use PREFIX_HOLDOUT_2048.

Density rule:
larger P2 production residual; tie D512.

Run only the minimum required P0/P2/restore/live controls.

No tuning.

If residual does not survive:
close negative/software.

---

# 12. Conditional NCU

Only if residual survives holdout.

At most 2 profiles.

Write `NCU_PREREGISTRATION.md` before collection.

Use NCU only to separate:
- GPU copy/memory traffic;
- SM snapshot kernels if any;
- host orchestration.

No replay timing as primary evidence.

---

# 13. Closest-work gate

Before `READY_FOR_ARCH_REVIEW`, write a concrete capability comparison:

- Marconi
- Sparse Prefix Caching
- Tail-Replay
- TreeWY
- persistent-state GDN accelerator
- DAMP

For each:
- what it solves;
- semantics;
- state it stores/eliminates;
- whether it addresses snapshot production;
- whether it addresses restore;
- remaining concrete capability.

If the observed residual is merely:
- checkpoint placement;
- active-state HBM traffic;
- approximate replay;
- speculative snapshot explosion;
then reject architecture novelty.

---

# 14. R55 source-only lane

Complete in parallel whenever CPU time is available.

Read primary sources and official docs:
- Transformer Engine NVFP4;
- transposition-invariant FP4;
- NVIDIA NVFP4 pretraining;
- Quartet II;
- MOSS.

Produce:
`R55_PLATFORM_AND_CLOSEST_WORK_AUDIT.md`

Do not benchmark R55.

Do not install a large training stack solely for R55.

---

# 15. Final decision

Choose exactly one:

- `R54_RUNTIME_FASTPATH_NOT_QUALIFIED_V1`
- `R54_STATE_AUTHORITY_NOT_QUALIFIED_V1`
- `R54_RESTORE_SEMANTICS_NOT_QUALIFIED_V1`
- `R54_SNAPSHOT_LIFECYCLE_COST_LOW_V1`
- `R54_SOFTWARE_BASELINE_SUFFICIENT_V1`
- `R54_HOST_RUNTIME_COST_NOT_ARCH_LOCALIZED_V1`
- `R54_RESIDUAL_READY_FOR_ARCH_REVIEW_V1`

READY_FOR_ARCH_REVIEW does not authorize node174 work.
If reached, emit one bounded next-stage architecture-review manifest only.

Do not start R55 GPU experiments.
Do not invent R56.

---

# 16. Review pack and durable closure

node164 root:
`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r54_checkpoint_lifecycle_20260927/`

Review pack:
`docs/vm_tlb/review_packs/AWMA_R54_EXACT_RECURRENT_CHECKPOINT_LIFECYCLE_V1/`

Required:
- README.md
- PRE_EXECUTION_INVENTORY.md
- R54_SOURCE_AND_CLOSEST_WORK_AUDIT.md
- R55_PLATFORM_AND_CLOSEST_WORK_AUDIT.md
- MODEL_ADMISSION_RECEIPT.json
- RUNTIME_FASTPATH_RECEIPT.json
- PREFIX_FIXTURE_RECEIPT.json
- R54_EXACT_STATE_SCHEMA.tsv
- PREREGISTRATION.json
- SEMANTIC_QUALIFICATION.tsv
- SNAPSHOT_PRODUCTION_TIMING.tsv
- SNAPSHOT_COPY_ACCOUNTING.tsv
- RESTORE_SEMANTIC_RESULTS.tsv
- RESTORE_TIMING.tsv
- AMORTIZATION_RESULTS.tsv
- conditional HOLDOUT_RESULTS.tsv
- conditional NCU_DIAGNOSTIC.tsv
- R54_DECISION.md
- FINAL_DECISION.md
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Large raw/model files stay out of Git.

Close:
`science/engineering -> node164 -> review pack -> hashes -> commit -> push -> fetch-back -> exact SHA/tree verification -> clean worktree -> GPU lock released -> STOP`

Git transport failure is publication failure only.
Do not rerun science because push fails.
Use the configured HTTPS -> HTTP/1.1 -> SSH -> gh/API fallback.

No auto merge.
