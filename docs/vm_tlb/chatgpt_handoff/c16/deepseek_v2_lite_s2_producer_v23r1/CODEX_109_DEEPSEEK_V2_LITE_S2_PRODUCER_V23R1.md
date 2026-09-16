# C16 DeepSeek-V2-Lite S2 Producer V23R1 — authority repair + resume

## Execution mode

Execute in **GOAL MODE** on node109. This is a continuation of V23, not a fresh scientific redesign.

Base scientific evidence:

- V22 authorization: `hrl/c16-deepseek-v2-lite-authorization-174new-v22`
- V23 blocked implementation: `hrl/c16-deepseek-v2-lite-s2-producer-109-v23@f9eba10255eba0b55881663f31d73a9d3a45d127`

Read first:

1. `docs/vm_tlb/chatgpt_handoff/c16/deepseek_v2_lite_s2_producer_v23r1/C16_IDENTITY_GATE_POLICY_V1.md`
2. V23 review pack `docs/vm_tlb/review_packs/C16_DEEPSEEK_V2_LITE_S2_PRODUCER_109_V23/`
3. the original V23 Goal and Q30 engineering-reuse addendum.

Suggested implementation branch:

`hrl/c16-deepseek-v2-lite-s2-producer-109-v23r1`

Use a fresh worktree based on this coordination branch. Reuse valid V23 Stage-0 artifacts; do not recopy or redownload assets unnecessarily.

## Stage 0R — repair authority semantics, do not weaken integrity

### Asset authority

V23 established:

- model `deepseek-ai/DeepSeek-V2-Lite`
- revision `604d5664dddd88a0433dbae533b7fe9472482de0`
- config SHA256 `f346286b0f1c8b044252fd54cb4fa78b9fab6472a6e8bebb9edfe03d414ea03d`
- exact 15-file local inventory
- source/destination per-file SHA256 equality
- actual aggregate file sum `31418838087`
- stale V22 scalar `31418842074`

Do not use the 3987-byte scalar difference as a hard blocker by itself.

Instead create a **superseding hash-bound model asset receipt** that contains:

- canonical source root and local destination root
- exact relative path set
- per-file size + SHA256
- deterministic manifest SHA256
- exact file count
- aggregate repository payload bytes
- separate weight-shard file bytes
- if available, safetensors index tensor payload/metadata total size under a separately named field
- config/modeling/configuration/tokenizer hashes
- source == destination result

Require exact path-set + per-file SHA equality. If any required file is missing or any per-file SHA differs, STOP.

Preserve the V22 scalar discrepancy in the receipt as historical metadata drift.

### Input authority

Reuse V23 canonical DeepSeek S2 input evidence:

- payload SHA256 `2ca11cff95f13bcdd0efcb3f5b2d6c0b8f7e30c9e67492d6b291362c09ff6935`
- token count `2048`
- canonical token-matrix SHA256 `14009279ed85b3de1f2510df84a3a8b2ba7a0d35f00c79d250d8e0e47cff63df`
- no retokenization
- exact source ref from V23 `S2_INPUT_AUTHORITY.json`

Do not compare a differently serialized `token_sequence_sha256` to the canonical token-matrix hash as if they were the same hash definition. Rename/record serialization-specific hashes explicitly.

V22's generic `C16_PROSPECTIVE_COMMON_INPUT_V2` label must not override the exact V23 source ref + payload hash. Record this as metadata-version drift. For future cross-model matched-input claims, preserve a typed note that V1/V2 semantic equivalence must be separately established if needed.

### Audit all other Stage-0 checks

Classify every V23 preflight check as Tier A/B/C according to `C16_IDENTITY_GATE_POLICY_V1.md`.

- Tier A mismatches remain fail-closed.
- Tier B deployment changes require explicit new-deployment typing; do not silently change runtime/backend.
- Tier C mismatches are recorded but do not block when Tier A closes.

Create `STAGE0_GATE_AUDIT.tsv` and `SUPERSEDING_ASSET_AUTHORITY.json`.

If Tier A closes, final Stage-0R decision must be:

`DEEPSEEK_V23R1_STAGE0_AUTHORITY_REPAIRED_PASS`

Then continue automatically. Do not stop merely because V23 previously blocked.

## Continue original V23 scientific Goal

After Stage-0R PASS, resume the original V23 Goal from the first unexecuted scientific stage:

1. exact S2 semantic layer-streaming state
2. MLA runtime dataflow qualification
3. one defensible MLA semantic target
4. replay/signature gate
5. fresh static/address-path audit
6. complete MLA formal capture
7. serial admission + positive ACK
8. natural-routing MoE qualification
9. one defensible routed-expert or explicitly grouped/fused MoE semantic target
10. replay/signature gate
11. fresh static/address-path audit
12. complete MoE formal capture
13. serial admission + positive ACK
14. bounded NSYS/NCU evidence
15. S2 MLA-vs-MoE interpretation
16. typed next-step authorization
17. hash-closed review pack
18. commit/push/canonical remote verification
19. cleanup + release GPU lock
20. STOP

All original V23 evidence boundaries remain in force.

## No weakening of real gates

Still fail closed for:

- model revision/config/custom-code mismatch
- missing/changed required model file
- canonical input payload/token-matrix mismatch
- retokenization/substitution
- runtime/backend semantic substitution
- semantic state/replay mismatch
- natural routing not preserved
- MLA object/evidence-class mismatch
- expert-specific label without lossless expert attribution
- static/path closure failure
- drop/overflow/terminal failure
- formal Pipeline rejection / negative ACK

## Required V23R1 review pack

Create:

`docs/vm_tlb/review_packs/C16_DEEPSEEK_V2_LITE_S2_PRODUCER_109_V23R1/`

Include all original V23 required artifacts, plus:

- `C16_IDENTITY_GATE_POLICY_SNAPSHOT.md`
- `STAGE0_GATE_AUDIT.tsv`
- `SUPERSEDING_ASSET_AUTHORITY.json`
- `V23_BLOCKER_REASSESSMENT.json`

Full PASS only if both MLA and MoE anchors close and both receive positive ACK:

`C16_DEEPSEEK_V2_LITE_S2_PRODUCER_109_V23R1_PASS_WITH_MLA_AND_MOE_ANCHORS`

If a real Tier-A/scientific blocker occurs, emit a typed partial/blocker decision and preserve all valid evidence.

## Node109 / Git / GPU rules

Use normal node109 Linux Git workflow. Do not install `gh`. Do not use Windows mirror.

Before CUDA/profiler work:

- inspect `nvidia-smi`
- inspect/acquire `/data/c16/locks/c16_gpu_campaign.lock`
- never kill/bypass another workload

Formal admission concurrency remains exactly 1.

After completion:

- release GPU lock
- verify no profiler/DeepSeek CUDA process remains
- verify GPU baseline
- commit Goal-owned changes
- push actual HEAD
- verify canonical `git ls-remote`
- require local HEAD == remote HEAD
- clean working tree

Then report branch, HEAD, final decision, review pack, repaired asset authority manifest SHA, MLA anchor/run/ACK, MoE routing/anchor/run/ACK, NCU typed status, next-step authorization, and STOP.
