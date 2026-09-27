# CODEX GOAL — AWMA R54 Greedy-Semantic Requalification V1R2

## Purpose

Continue from accepted R54 V1R1:

- execution branch:
  `hrl/awma-r54-fastpath-requal-v1r1`
- accepted commit:
  `61707eecc3cb934c309cb016a750cb4d7612a88d`
- accepted V1R1 state:
  `R54_V1R1_HUB_KERNEL_SEMANTICS_NOT_QUALIFIED`

V1R1 remains permanently valid for its stricter contract:
- exact top1/top2 ordering failed on the initial canary;
- no checkpoint science was run under that strict contract.

V1R2 defines a **separate application-semantic contract** for the actual R54 deployment:

`R54_GREEDY_BACKEND_EQUIVALENCE_V1`

The Qwen3.5 checkpoint-lifecycle study uses greedy continuation. Therefore V1R2 asks:

> Does the qualified SM89 Hub-kernel backend preserve the exact greedy token trajectory across multiple frozen prefix states, even though non-selected logit rankings differ numerically from the fallback backend?

If yes, the Hub backend is scientifically qualified for the R54 checkpoint-lifecycle study and the original R54 measurement contract resumes in this same Goal.

If no, R54 is closed on node109.

Repository:
`swayhrl/accel-sim-framework`

Coordination branch:
`hrl/awma-r54-greedy-semantic-requal-v1r2-handoff`

Accepted base:
`61707eecc3cb934c309cb016a750cb4d7612a88d`

Stage:
`AWMA_R54_GREEDY_SEMANTIC_REQUALIFICATION_V1R2`

Node:
109 / RTX4080 / SM89 only.

Do not use node174 or Accel-Sim.

---

# 0. Preserve prior history

Do not rewrite or weaken:

## V1
`R54_RUNTIME_FASTPATH_NOT_QUALIFIED_V1`

Meaning:
the local causal-conv1d / flash-linear-attention package path was not qualified.

## V1R1
`R54_V1R1_HUB_KERNEL_SEMANTICS_NOT_QUALIFIED`

Meaning:
the Hub generic CUDA path was technically available and executed all four required optimized kernels, but failed the pre-registered exact top1/top2 ordering gate.

Carry both results into every final report.

V1R2 is a new deployment-semantic qualification, not a reinterpretation of those gates.

---

# 1. Reuse exact V1R1 backend

Reuse without modification:

- model:
  `Qwen/Qwen3.5-0.8B@c6046cd1f7e2763bf1abf5a5aef6ad7878e10ccb`
- weight SHA256:
  `04b1c301231dd422b8860db31311ab2721511346a32cb1e079c4c4e5f1fe4696`
- Transformers:
  `96331a9f93b72697f160a958d2883d4b49a56739`
- `kernels==0.17.0`
- Torch:
  `2.14.0+cu130`
- mamba Hub artifact:
  `20b2508ad12ae40260291539bf45183000451850`
- FLA Hub artifact:
  `6d22ed1d2bb627375b6ca8fc135f7f417863e639`

Do not change torch, kernels, Hub revisions, model or driver.

Use the accepted V1R1 environment if exact hashes match.
If it is missing/corrupted, reconstruct exactly from V1R1 receipts.

No new backend.

---

# 2. Why the semantic contract changes in V1R2

The original R54 application policy is greedy decoding.

V1R1 already established on the canary:
- exact finite/shape/dtype;
- exact argmax;
- exact 16-token greedy continuation;
- only non-selected ranking changed at the initial step.

V1R2 therefore freezes the application-visible backend contract:

## Required

For each frozen prefix:
- exact greedy generated token sequence for **64 continuation tokens**;
- exact stop/EOS position if it occurs before 64;
- exact continuation length;
- no NaN/Inf;
- exact cache sequence length after continuation.

## Diagnostic only, not gating

Record at every step:
- top-8 ordered IDs;
- top-8 set;
- top1/top2 ordering;
- selected-token logit;
- second-best token/logit;
- logit margin;
- max absolute logit difference where practical.

Do not use any post-hoc numerical tolerance.

The non-selected ranking diagnostics remain evidence of backend numerical differences, but are not application-semantic failures for temperature=0 greedy deployment unless they change the selected token or continuation trajectory.

This V1R2 contract is frozen before running the new prefix cases.

---

# 3. Frozen prefix states

Use three prefix authorities.

## S0 — existing canary prefix

Reuse the exact V1R1 64-token input.

No recapture/change.

## S1 — PREFIX_HOLDOUT_2048

Construct exactly from the original R54 measurement contract using the accepted R53 `REQUEST_SELECTION.tsv`:

- exact raw prompt order and separator from the R54 handoff;
- pinned Qwen3.5 tokenizer;
- `add_special_tokens=False`;
- first 2048 token IDs.

This prefix was already specified before V1R1 results and is therefore a legitimate independent holdout.

## S2 — PREFIX_DISCOVERY_4096

Same frozen deterministic text stream:
- first 4096 token IDs.

Do not choose any new prompt based on numerical results.

Create:
`R54_V1R2_PREFIX_RECEIPT.json`

Record text/token hashes.

---

# 4. Clean-process paired execution

For each S0/S1/S2 run:

## F arm
Fallback backend:
`use_kernels=False`

## H arm
Hub backend:
`use_kernels=True`

Use:
- same V1R1 environment;
- same model weights;
- same tokenizer/input IDs;
- same dtype;
- temperature=0 greedy;
- fresh clean process per arm to avoid backend state contamination.

All GPU work holds:
`/data/c16/locks/c16_gpu_campaign.lock`

Do not profile every token.

---

# 5. Greedy semantic measurement

For each prefix and backend:

1. run prefix prefill with cache;
2. record first-step logits diagnostics;
3. generate exactly up to 64 greedy tokens, stopping naturally at EOS if applicable;
4. at each greedy step record:
   - selected token ID;
   - top2 IDs;
   - top8 IDs/set;
   - selected-token logit;
   - runner/cache length;
5. record final token sequence hash.

Primary gate per prefix:

`fallback_generated_token_ids == hub_generated_token_ids`

Also require:
- same EOS/stop position;
- same token count;
- valid cache length progression.

No text-level-only comparison.

---

# 6. V1R2 decision

## PASS

`R54_V1R2_GREEDY_BACKEND_QUALIFIED`

Requires exact 64-token greedy continuation equivalence for all:
- S0;
- S1;
- S2.

If a natural EOS occurs early, exact shared EOS termination is sufficient for that prefix.

Top2/top8 diagnostic differences are allowed and must be reported.

Then automatically continue Phase 7.

## FAIL

`R54_V1R2_GREEDY_BACKEND_NOT_QUALIFIED`

Any prefix has:
- different selected token at any step;
- different EOS/termination;
- invalid state/cache progression.

Then:
- R54 sleeps on node109;
- no checkpoint science;
- close V1R2;
- STOP.

No fourth semantic contract.

---

# 7. Resume R54 checkpoint science if PASS

If and only if:
`R54_V1R2_GREEDY_BACKEND_QUALIFIED`

resume the original R54 contract using the Hub backend as the frozen execution backend.

Required original files:

`docs/vm_tlb/chatgpt_handoff/awma/r54_long_horizon_v1/R54_MEASUREMENT_CONTRACT_V1.md`

and

`docs/vm_tlb/chatgpt_handoff/awma/r54_long_horizon_v1/CODEX_GOAL_109_R54_LONG_HORIZON_V1.md`

Do not rerun V1 local-package qualification.

Continue directly:

1. construct/freeze prefix fixture if not already fully materialized;
2. enumerate exact runtime state schema under Hub backend;
3. exact snapshot/restore semantic canary;
4. M0/P0 baseline qualification;
5. P1/P2 strong checkpoint implementations;
6. D512/D2048 production timing;
7. restore timing;
8. amortization N=1/2/4;
9. conditional holdout;
10. conditional NCU;
11. closest-work gate;
12. final R54 decision.

All original scientific constants remain:
- chunk=512;
- D512/D2048 only;
- 5% + 3x-jitter materiality;
- same prefix/suffix/holdout definitions;
- same P0/P1/P2;
- no new model;
- no node174.

---

# 8. Important backend-specific correctness rule

Once V1R2 passes, all checkpoint-science comparisons P0/P1/P2/restore are performed **within the same Hub backend**.

Therefore checkpoint semantic correctness is judged against the Hub-backend uninterrupted reference, not against the PyTorch fallback logits.

For checkpoint/restore:
- exact greedy continuation must match Hub uninterrupted reference;
- exact cache/state ownership must close;
- copy-expected tensors must preserve their exact snapshot contents where appropriate;
- no cross-backend top2 ordering requirement is reintroduced.

This prevents backend numerical differences from being confused with checkpoint corruption.

---

# 9. Publication

V1R2 minimum review pack:

`docs/vm_tlb/review_packs/AWMA_R54_GREEDY_SEMANTIC_REQUALIFICATION_V1R2/`

Required:
- README.md
- V1_V1R1_INHERITANCE.md
- R54_V1R2_PREFIX_RECEIPT.json
- R54_V1R2_GREEDY_RESULTS.tsv
- R54_V1R2_NUMERICAL_DIAGNOSTICS.tsv
- R54_V1R2_DECISION.md
- FINAL_DECISION.md
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Durable root:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r54_greedy_semantic_requal_v1r2_20260927/`

If PASS and full R54 resumes, publish full lifecycle results under:
`full_r54/`
and use review pack:
`docs/vm_tlb/review_packs/AWMA_R54_EXACT_RECURRENT_CHECKPOINT_LIFECYCLE_V1R2/`

Final closure:
`science/engineering -> node164 -> review pack -> hashes -> commit -> push -> fetch-back -> exact SHA/tree verification -> clean worktree -> GPU lock released -> STOP`

No auto merge.

Git transport failure is publication-only; do not rerun science.
