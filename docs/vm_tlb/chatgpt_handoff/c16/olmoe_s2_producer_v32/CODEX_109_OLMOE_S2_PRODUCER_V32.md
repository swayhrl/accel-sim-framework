# C16 OLMoE S2 native BF16 producer — node109 V32

## Execution mode

Execute in **GOAL MODE** using the normal node109 Linux producer workflow.

This is the one-shot third-independent-MoE-lineage producer authorized by accepted V31. Do not create another planning-only round. Proceed through runtime/capacity precheck, exact S2 state, natural top-8 routing, semantic target qualification, formal capture, serial admission/ACK, review pack, commit/push and cleanup unless a genuine scientific/runtime contract blocker is encountered.

Suggested implementation branch:

`hrl/c16-olmoe-s2-producer-109-v32`

Use existing node109 Git transport/authentication. Do not install/configure `gh`; do not switch authentication; do not use a Windows mirror.

GPU campaign lock:

`/data/c16/locks/c16_gpu_campaign.lock`

`FORMAL_ADMISSION_CONCURRENCY=1`

---

# Accepted upstream authority

CPU authorization branch:

`hrl/c16-olmoe-third-moe-authorization-174new-v31`

Required HEAD:

`4013582e5cedef3e2ecaf7b7c74d9bb45a1af8ce`

Decision:

`C16_OLMOE_THIRD_MOE_AUTHORIZATION_174NEW_V31_PASS`

V31 explicitly authorizes one node109 native OLMoE producer subject to the gates below.

Model authority:

- model ID: `allenai/OLMoE-1B-7B-0125-Instruct`
- revision: `b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`
- canonical node164 root: `/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e/`
- receipt schema: `C16_MODEL_ASSET_RECEIPT_V1`
- receipt SHA256 from V31: `01319b411b07ccd7b53c4f653bd5986a51604d9c2c16be7412257e994ff49d13`
- total receipt-bound payload bytes: `13842592086`
- no symlinks in canonical asset
- native checkpoint: 3 BF16 safetensors shards + index/config/tokenizer support

Architecture authority:

- model class: `OlmoeForCausalLM`
- 16 decoder layers
- hidden size 2048
- 16 attention heads / 16 KV heads
- 64 experts
- natural top-8 experts per token
- `norm_topk_prob=false`
- expert intermediate size 1024
- expected expert MLP semantic structure: `gate_proj + up_proj -> SiLU -> down_proj`, subject to exact runtime receipt
- checkpoint dtype: BF16
- max positions: 4096

Do not reinterpret OLMoE as Qwen/DeepSeek implementation merely because some kernels may share cuBLAS/CUDA families.

---

# Stage 0 — fail-closed authority closure and asset transfer

## 0A. Resolve the V31 receipt-file-set wording

V31 review pack records `receipt_file_count=11` and an 11-entry payload manifest, while `receipt_file_set_matches=false` in `ASSET_AUTHORITY.json`.

Before GPU work, inspect the canonical directory and the actual `MODEL_ASSET_RECEIPT.json` semantics.

Required acceptable closure:

- the exact 11 model payload files named by the receipt/manifest are present and match the receipt-bound sizes/hashes;
- the only additional canonical-directory file not included in the payload file set may be the self-describing `MODEL_ASSET_RECEIPT.json` itself;
- no symlink;
- no unexpected unbound model/config/tokenizer/checkpoint file.

If `receipt_file_set_matches=false` is solely the self-referential receipt-file exclusion above, record this explicitly as `PASS_RECEIPT_SELF_EXCLUSION_SEMANTICS` and continue.

If any other unbound/extra/missing payload exists, fail closed before execution.

Do not mutate/finalize the node164 canonical asset.

## 0B. Runtime subset availability on node109

Use the exact receipt-bound runtime subset only.

If node109 does not directly mount node164, transfer the required subset to a deterministic node109 path under `/data/c16/models/olmoe-1b-7b-0125-instruct/<revision>/` using the existing approved C16 transfer method.

Do not redownload from Hugging Face unless the accepted node164 authority is genuinely unavailable.

After transfer, verify every transferred file's size/hash against the accepted receipt before runtime use. Do not copy unrelated assets.

---

# Stage 1 — native runtime and RTX4080 capacity gate

Pin and record the exact native OLMoE runtime on node109:

- Python
- torch/CUDA build
- transformers version
- exact `OlmoeForCausalLM` implementation source/code hash where practical
- attention backend
- MoE dispatch implementation
- BF16 policy
- code-object/backend identity used by the eventual target

Do not quantize, convert dtype, alter top-k, alter expert count, or replace OLMoE semantics merely to fit.

V31 capacity policy:

- native checkpoint bytes approximately `13,838,721,960`
- RTX4080 16GB
- preferred: full-resident native BF16 only if bounded precheck proves it fits
- fallback: exact layer-local/streaming replay only if BF16, natural top-8 and the target backend semantics are preserved

Perform a bounded full-resident precheck. Do not spend unbounded time forcing it.

If full-resident fits safely, use it.

If full-resident is too tight/OOM, do **not** fail merely for capacity. Switch to an exact semantic layer-streaming/state-replay path analogous to accepted Q30/DeepSeek methodology, provided it preserves:

- exact token/state provenance
- native BF16 tensors
- natural routing
- same target semantic/backend
- exact replay equivalence

Fail only if no semantics-preserving path exists.

Record peak allocated/reserved memory for whichever mode is accepted.

---

# Stage 2 — exact canonical S2/T2048 input freeze

Primary scenario:

`S2_TEXT = B1 / T2048 / D32`

Upstream common semantic source authority from V31:

`docs/vm_tlb/review_packs/C16_QWEN3_30B_S2_T2048_STATE_REPLAY_109_V1/S2_INPUT_LOCAL_AUTHORITY.tsv`

Expected source SHA256:

`cdd532689295d9e934a1307e3c9c63b288b9f9a702d712cf6b516b24aaf1db80`

Use the exact canonical OLMoE tokenizer/template behavior from revision `b89a7...`.

V31 tokenizer hashes:

- tokenizer.json: `d1e645ebd850d79567e531a3c103ac575d8e9cf45fa941420afc584b293438ea`
- tokenizer_config.json: `67ac3cdae4e25e84d5d0f4faadb961dd36341cf04e02c7be90a8fd8e697617eb`
- special_tokens_map.json: `43ffdefa4e501eebdaaba8f34999ac1b5507dc836fab4a1d1529466de35101e0`

Freeze and persist:

- exact serialized token IDs
- shape/count exactly 2048
- deterministic token-matrix/token-sequence SHA256 with documented serialization
- source ref/SHA
- tokenizer/template hashes
- special-token policy
- proof producer consumes the frozen IDs directly thereafter

Do not silently pad/truncate and do not re-author the prompt.

If exact T2048 cannot be constructed under the established C16 exact-token procedure, fail closed before model execution.

---

# Stage 3 — exact S2 execution/state and natural routing

Build the exact S2 state sufficient for a representative OLMoE decode anchor.

Preferred anchor state for cross-lineage comparability:

`S2 decode step 3` if exact deterministic state generation is feasible under the accepted execution mode.

If Decode3 cannot be reproduced without changing semantics, select one deterministic S2 decode state and document it explicitly; do not force alignment by synthetic tokens.

For layer selection:

- prefer a non-special early/mid OLMoE layer whose native routing and target can be fully attributed;
- Layer1 is preferred if representative and stable;
- do not force the layer merely to mimic DeepSeek/Q30.

Record an exact natural-routing receipt containing:

- selected layer and decode step/state
- router input shape/hash
- router logits shape/hash
- natural top-8 expert IDs in order
- router weights
- `norm_topk_prob=false` behavior as actually executed
- selected-expert token/group mapping
- repeat-run stability

Do not force any expert ID.

---

# Stage 4 — runtime MoE dataflow and semantic target qualification

Observe the actual node109 runtime implementation rather than assuming V31's source-level shape.

Classify whether the selected expert path executes as:

- independent per-expert GEMV/GEMM kernels;
- grouped expert kernels;
- fused/grouped runtime path;
- another exact native path.

Preserve true dataflow:

`hidden -> router -> natural top-8 -> dispatch -> gate/up -> activation -> down path -> weighted combine`

Target hierarchy from V31:

1. `NATURAL_SELECTED_EXPERT_DOWN_PROJ`
   - only if dynamic evidence provides lossless expert-specific weight/input/output attribution;

2. `NATIVE_GROUPED_OR_FUSED_EXPERT_DOWN`
   - only with lossless selected-expert/group attribution;

3. `ROUTED_EXPERT_WEIGHT_CONSUMER`
   - explicitly narrower evidence class if clean down attribution is impossible.

Do not label a grouped/fused target as one expert's down projection without proof.

For the retained target persist:

- exact semantic role/evidence class
- selected expert/group identity
- input/output tensor shapes, strides, dtype, hashes
- target weight tensor/range and hash where practical
- same-process storage pointers/ranges
- code-object/kernel signature
- grid/block
- repeat stability

Only one formal MoE anchor is required in V32.

---

# Stage 5 — exact isolated replay/signature gate

If rank-1 selected-expert `down_proj` is available, construct an isolated exact replay from the real naturally routed input and exact BF16 expert weight.

Require output bitwise equality if deterministic backend semantics allow it; otherwise require a tightly typed exact-equivalence criterion justified by the backend.

The isolated replay must preserve the same semantic operation and target kernel/backend used by the accepted in-context target. Do not substitute another library/kernel simply because replay is easier.

If the runtime is grouped/fused and isolation would change the backend, do not force isolated single-expert replay; instead retain a grouped/fused in-context or group-exact replay with lossless attribution.

---

# Stage 6 — fresh SM89 static/address-path audit

For the final accepted target, perform fresh native SM89 static-path discovery.

Enumerate all address-bearing paths relevant to formal capture:

- direct GLOBAL MREF
- LDGSTS/global-source paths if present
- relevant loads/stores and operand semantics

Do not inherit Q30/DeepSeek static sets or counts.

Record exact static map and SHA256.

Use actual SASS/source-address registers when required by the warp-regsource tracer.

---

# Stage 7 — bounded tracer canary

Use the known-good C16 V20/V23R1/V26/V27 warp-regsource lifecycle where applicable.

Before full sharding, demonstrate at least:

- one positive weight/source or grouped-expert memory canary that dynamically joins the intended target object;
- one second independent canary for input/output/another target object when applicable;
- terminal closure;
- drop=0 / overflow=0.

If the exact OLMoE kernel requires a tracer engineering adaptation, solve bounded engineering issues within this Goal while keeping semantic identity frozen.

Do not change expert/layer/target merely to make the tracer easier unless the existing target is scientifically untraceable; if target class must change, document the typed reason and stay within the V31 hierarchy.

---

# Stage 8 — complete formal capture

Create exactly one OLMoE S2 formal raw run for the accepted natural MoE anchor.

Formal capture rules:

- one independently replayed shard per independently captured static address-bearing instruction/path under existing C16 policy;
- fresh process/output root per shard where required;
- same-process ADDRESS_CONTEXT;
- complete executed/zero partition;
- terminal closure;
- drop=0;
- overflow=0;
- no partial formalization;
- no stale canary/test shard in the formal bundle.

If initial tracer capacity overflows on high-volume shards, recapture those shards in a fresh recovery root with sufficient capacity and formalize only the clean replacement, following V27 precedent.

Independently audit the completed bundle before transfer/admission.

Typed object membership should preserve the accepted evidence class and at minimum distinguish target weight/input/output or grouped/fused equivalents from `OTHER_OR_UNCLASSIFIED`.

Do not construct cross-shard chronology, cross-shard reuse distance, or cross-replay VA union.

---

# Stage 9 — serial transfer/admission/ACK

Transfer the completed formal bundle using the existing C16 Pipeline path.

Require:

- source manifest hash
- destination verification
- one formal admission
- positive ACK
- catalog SHA

`FORMAL_ADMISSION_CONCURRENCY=1`

Do not begin another formal admission concurrently.

---

# Stage 10 — bounded profiling and third-lineage handoff

Preserve bounded NCU/NSYS evidence only where metrics are explicit and units resolved.

Do not invent comparability against Q30/DeepSeek if profiling metrics differ or are unavailable.

After positive ACK, emit a third-lineage handoff for 174-new containing:

- exact formal run ID
- evidence class
- model/layer/decode state
- natural top-8 receipt
- selected expert/group identity
- static/executed/zero partition
- active-lane events
- typed object-membership summary
- per-shard 128B-line and 4K/64K/2M-page descriptive distributions
- known implementation/deployment differences versus Q30/DeepSeek

Do **not** itself declare the three-lineage common pattern. That is a future independent consumer/synthesis task.

---

# Required review pack

Create:

`docs/vm_tlb/review_packs/C16_OLMOE_S2_PRODUCER_109_V32/`

Include at least:

- `UPSTREAM_AUTHORITY.tsv`
- `ASSET_RUNTIME_RECEIPT.json`
- `RECEIPT_FILESET_CLOSURE.json`
- `RUNTIME_CAPACITY_RECEIPT.json`
- `S2_INPUT_AUTHORITY.json`
- `S2_STATE_RECEIPT.json`
- `NATURAL_TOP8_ROUTING.json`
- `MOE_RUNTIME_DATAFLOW.json`
- `MOE_TARGET_QUALIFICATION.json`
- `REPLAY_SIGNATURE.json`
- `STATIC_PATH_AUDIT.json`
- `TRACER_CANARY_AUDIT.json`
- `FORMAL_SUMMARY.json`
- `ADMISSION_ACK.json`
- `NCU_TYPED_EVIDENCE.json`
- `THIRD_LINEAGE_HANDOFF.json`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Preferred full-PASS decision:

`C16_OLMOE_S2_PRODUCER_109_V32_PASS_WITH_NATIVE_MOE_ANCHOR`

Use this only if native BF16 semantics, natural routing, target attribution, complete formal capture and positive ACK all close.

Typed fail-closed outcomes are valid for genuine contract blockers such as:

- no semantics-preserving BF16 capacity mode;
- no exact token freeze;
- no lossless MoE target attribution under any V31-authorized hierarchy rank;
- unrecoverable trace closure failure.

Routine engineering/Git/worktree/cwd/stdout issues are not scientific blockers; solve and continue.

---

# Git and cleanup

At the end:

`review pack -> SHA256SUMS -> commit -> push -> canonical git ls-remote verification -> clean worktree`

Release `/data/c16/locks/c16_gpu_campaign.lock`.

Verify no OLMoE/profiler/NVBit process remains and GPU returns to baseline.

Then STOP.