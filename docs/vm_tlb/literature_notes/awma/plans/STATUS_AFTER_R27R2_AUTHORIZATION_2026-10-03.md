# Status after R27R2 seeded continuation authorization

Date: 2026-10-03 (Asia/Shanghai)

This supersedes `STATUS_AFTER_R27R1_REVIEW_2026-10-03.md` only for current AWMA task authorization. R26 remains the latest accepted capacity result until R27R2 is independently reviewed.

## Current authorized AWMA task

Lane G / node109:

`AWMA_R27R2_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1`

Handoff branch:

`hrl/awma-r27r2-varied-batch-capacity-seeded-continuation-handoff-v1`

Exact handoff HEAD:

`578615d953b9c286cbafada997b3ed09217140a6`

Exact handoff tree:

`777ffacbcc3dfd6cdad6f77acb591f5f3a041102`

Fresh execution branch:

`hrl/awma-r27r2-varied-batch-capacity-109-v1`

Handoff directory:

`docs/vm_tlb/chatgpt_handoff/awma/r27r2_varied_batch_capacity_seeded_continuation_v1/`

Start at `START_HERE.md`.

R27 and R27R1 remain closed historical STOPs and must not be resumed/amended.

## Why R27R2 is one merged Goal

The user requested fewer execution rounds and higher efficiency. R27R2 therefore combines all mutually dependent work that can safely proceed under one frozen scientific contract:

1. bounded parent identity recheck;
2. externally staged exact-byte seed validation and node164 admission;
3. token-bank construction and durable bank authority;
4. B1 B0/C1/S2 numerical, checkpoint/resume and policy-switch qualification;
5. implementation freeze;
6. bounded natural capacity search and 3/3 adjacent endpoint closure;
7. positive-only common-B/witness-B 32-step trajectory, fresh-process resume and policy switch;
8. at most one positive-only allocator diagnostic pair if genuinely necessary;
9. one publication/closure.

Passing gates continue automatically in the same execution branch. Ordinary pre-freeze engineering defects are solved in the same Goal and only affected prerequisites are rerun. Scientific identity/source/numerical/resource failures, or post-freeze scientific changes, STOP for review.

This reduces operational round trips without weakening the evidence contract.

## External seed authority

Preferred staging path:

`/data/c16/awma/r27_input_seed/train-00000-of-00001.parquet`

Required identity:

- Salesforce/wikitext
- revision `8aaa8b27d493dba10b8553290236799e6dc57829`
- `wikitext-2-raw-v1/train-00000-of-00001.parquet`
- 6,357,543 bytes
- SHA256 `e83889baabc497075506f91975be5fac0d45c5290b6b20582c8cd1e853d0c9f7`

R27R2 performs **no network download retry**. It accepts only the already staged byte-exact seed, or an exact-size/hash candidate found under the bounded staging root. It must durably admit/read back the raw bytes on node164 before tokenization.

## Boundaries

- No tokenization before exact raw-seed admission.
- No capacity observation before B1 numerical qualification and implementation freeze.
- All CUDA/JIT holds the node109 campaign flock.
- No formal timing campaign, NSYS/NCU/NVBit/SASS, node174/Accel-Sim, hardware/PPA, second model/corpus, all-parameter training, production/default change or deployment.
- C16 Stage A and DTC-L1 remain separate.
- After one final execution commit/review pack/node164 closure, R27R2 STOPs for ChatGPT review.
