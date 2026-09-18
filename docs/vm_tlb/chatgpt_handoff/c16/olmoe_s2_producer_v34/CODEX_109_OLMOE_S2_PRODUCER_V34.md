# C16 OLMoE S2 formal producer — node109 V34

## Execution mode

Execute in **GOAL MODE** on node109 using the normal Linux producer workflow.

This Goal supersedes only the over-constrained OLMoE input-binding assumption from V32/V33. It does not reopen accepted V31/V32 asset/runtime evidence.

Suggested implementation branch:

`hrl/c16-olmoe-s2-producer-109-v34`

## Read first

1. `docs/vm_tlb/chatgpt_handoff/c16/olmoe_s2_producer_v34/INPUT_POLICY_REPAIR.md`
2. this file
3. accepted V31/V32 review packs as needed

## Accepted upstream

OLMoE authorization:
- `hrl/c16-olmoe-third-moe-authorization-174new-v31`
- HEAD `4013582e5cedef3e2ecaf7b7c74d9bb45a1af8ce`
- decision `C16_OLMOE_THIRD_MOE_AUTHORIZATION_174NEW_V31_PASS`

OLMoE V32:
- `hrl/c16-olmoe-s2-producer-109-v32`
- HEAD `ed22d57255a52e492e332f3f8efa619e217c3cc6`
- decision `C16_OLMOE_S2_PRODUCER_109_V32_FAIL_CLOSED_EXACT_S2_TOKEN_FREEZE_UNPROVEN`

V32 accepted evidence to reuse as prior evidence:
- exact 11-file payload + receipt self-exclusion closure
- native BF16 runtime identity
- full-resident RTX4080 capacity PASS
- peak allocated 13,838,324,224 bytes
- peak reserved 13,843,300,352 bytes
- no S2 model execution/formal raw occurred

Do not repeat exploratory capacity work unless runtime identity materially changes. Actual V34 execution must still naturally fit.

## Stage 0 — exact prospective-common source recovery

Retrieve exact source authority:

- authority: `C16_PROSPECTIVE_COMMON_INPUT_V1`
- pinned branch/commit: `hrl/c16-prospective-common-input-174new-laneB-v8@ca683527323e26e3415a805c797c53c5edea322c`
- path: `docs/vm_tlb/assets/c16/prospective_common_input_v1/TEXT.txt`
- byte count: 976000
- SHA256: `52761ce278c0e4819f153036e2b93e2b921d7963dda6a1d67a8192503612fa9c`

Use normal Git transport. Do not rely on 174 local state.

Independently hash the exact bytes before tokenization. Fail closed if size/hash mismatch.

Do not use the V33 11664-byte Q30-local recovered payload for OLMoE S2.

## Stage 1 — exact OLMoE S2 token freeze

Canonical model:

`allenai/OLMoE-1B-7B-0125-Instruct@b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`

Canonical node164 root:

`/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e/`

Transfer only the exact runtime subset needed on node109 and verify against the accepted receipt. Do not copy or mutate the canonical asset.

Tokenize exact prospective-common TEXT bytes with:
- exact canonical OLMoE tokenizer
- `add_special_tokens=False`
- `chat_template=NOT_APPLIED`
- no normalization/rewriting
- require total IDs >= 2048
- freeze first exact 2048 IDs

Persist:
- source path/ref/size/SHA
- tokenizer identities
- total pre-truncation token count
- exact 2048 IDs
- defined serialization
- token-sequence/token-matrix SHA
- payload SHA
- `no_retokenization_after_freeze=true`

Consume those frozen IDs directly for all subsequent V34 execution.

## Stage 2 — runtime re-establishment

Re-establish the same native BF16 runtime family as V32 or document any exact delta.

Record:
- Python
- torch/CUDA
- transformers
- exact `modeling_olmoe.py` identity
- attention backend
- MoE dispatch implementation
- GPU UUID/CC/driver

Require native BF16 semantics, natural top-8 routing, no quantization/dtype/top-k changes.

Full resident is allowed/preferred because V32 proved capacity under its runtime. If current runtime differs or natural execution cannot fit, apply only the V31-approved exact BF16 fallback preserving target backend; otherwise fail closed.

## Stage 3 — exact S2 execution and natural routing

Scenario:

`S2_TEXT = B1/T2048/D32`

Execute exact native S2 with the frozen IDs.

Select a representative decode state that gives a defensible natural expert-down anchor while preserving the real runtime.

Record a natural-routing receipt:
- layer
- decode step
- router logits shape/hash
- exact natural top-8 expert IDs
- route weights
- router normalization behavior
- selected expert/group mapping
- hidden/input/output shape/hash where relevant

Do not force an expert ID.

Do not infer population routing statistics from one frozen state.

## Stage 4 — target hierarchy

Qualify in this order:

1. `NATURAL_SELECTED_EXPERT_DOWN_PROJ`
   - only with lossless expert-specific weight/input/output attribution

2. `NATIVE_GROUPED_OR_FUSED_EXPERT_DOWN`
   - only with lossless selected expert/group attribution

3. `ROUTED_EXPERT_WEIGHT_CONSUMER`
   - explicitly narrower semantic class

Do not stop merely because rank 1 is unavailable. Continue down the hierarchy automatically if scientific attribution remains exact.

If no losslessly attributable target exists at any level, fail closed with a typed target-attribution blocker.

## Stage 5 — exact replay/signature

For the selected target:
- construct the smallest exact semantic replay preserving the frozen natural routing/state required by the target
- preserve BF16 target backend
- prove output equivalence/bitwise equality where achievable and required
- prove target function/occurrence identity
- establish same-process ADDRESS_CONTEXT for relevant weight/input/output/group buffers

No synthetic microkernel or mathematically equivalent substitute.

## Stage 6 — fresh SM89 static/path audit

Perform fresh static/path analysis of the actual selected kernel:
- direct GLOBAL MREF
- LDGSTS/global-source paths if present
- other address-bearing paths
- load/store semantics
- actual source-address register mapping from SASS

Do not inherit static counts from Q30/DeepSeek.

## Stage 7 — dynamic canary and formal capture

Use the already validated C16 warp-regsource lifecycle from successful V20/V23R1/Q30 paths.

For every selected static shard:
- fresh process/output
- clear inherited `C16_*` and `CUDA_INJECTION64_PATH`
- explicit function/static selector
- sufficient tracer capacity
- terminal closure
- drop=0
- overflow=0
- executed/zero partition
- same-process typed object attribution

If capacity is insufficient for some shards, re-capture those shards in a fresh recovery root with larger capacity and exclude overflowed attempts from formalization.

Complete one formal OLMoE anchor run.

## Stage 8 — serial transfer/admission

Mandatory:

`FORMAL_ADMISSION_CONCURRENCY=1`

Do:
- source manifest
- transfer to node164
- destination verification
- catalog admission
- positive ACK

No second target is required for V34 unless rank transition requires replacing a failed non-formal candidate before admission.

## Stage 9 — bounded profiler evidence

Run only bounded NCU/NSYS evidence if it can be typed cleanly and does not perturb formal raw semantics.

Preserve raw units. If numbers/units are not comparable to Q30/DeepSeek, mark `NOT_COMPARABLE`.

## Stage 10 — third-lineage handoff

Prepare the exact fields needed for a later 174-new three-lineage consumer:
- model/revision
- scenario/layer/decode step
- natural top-8 IDs/weights
- target semantic class
- expert/group attribution
- dimensions
- kernel/function/grid/block
- static address-bearing set counts
- executed/zero partition
- active-lane events
- per-shard 128B line and 4K/64K/2M page distributions
- typed weight/input/output/group fractions
- manifest/verification/catalog/ACK hashes
- NCU status

Claim boundary:

This producer alone must NOT declare a Q30+DeepSeek+OLMoE common result.

A later independent consumer may evaluate a three-independent-lineage MoE-family pattern. That synthesis is **not** a matched-input causal comparison across all lineages.

## Required review pack

Create:

`docs/vm_tlb/review_packs/C16_OLMOE_S2_PRODUCER_109_V34/`

Include at least:
- `INPUT_POLICY_AUTHORITY.json`
- `S2_INPUT_AUTHORITY.json`
- `ASSET_RUNTIME_RECEIPT.json`
- `RUNTIME_CAPACITY_RECEIPT.json`
- `S2_STATE_RECEIPT.json`
- `NATURAL_TOP8_ROUTING.json`
- `MOE_RUNTIME_DATAFLOW.json`
- `MOE_TARGET_QUALIFICATION.json`
- `REPLAY_SIGNATURE.json`
- `STATIC_PATH_AUDIT.json`
- `DYNAMIC_CANARY_AUDIT.json`
- `FORMAL_SUMMARY.json`
- `ADMISSION_ACK.json`
- `NCU_TYPED_EVIDENCE.json`
- `THIRD_LINEAGE_HANDOFF.json`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Preferred full PASS:

`C16_OLMOE_S2_PRODUCER_109_V34_PASS_WITH_FORMAL_MOE_ANCHOR`

Only use full PASS after formal capture and positive ACK.

## Git / cleanup

Use node109 existing Git transport. Do not install/configure `gh`.

Complete:
`review pack -> SHA close -> commit -> push -> canonical git ls-remote verify -> clean worktree`

Acquire/release:
`/data/c16/locks/c16_gpu_campaign.lock`

At end verify no stale CUDA/profiler process and GPU baseline.

Routine engineering problems should be solved and execution continued. Stop only on a genuine scientific/identity/input/target/formal-evidence blocker.
