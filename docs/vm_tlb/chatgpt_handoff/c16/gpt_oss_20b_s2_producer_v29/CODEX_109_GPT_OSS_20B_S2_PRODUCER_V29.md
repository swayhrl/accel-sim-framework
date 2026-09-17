# C16 gpt-oss-20b native MXFP4 S2 MoE producer — node109 V29

## Execution mode

Execute in **GOAL MODE** using the normal node109 Linux producer workflow.

This Goal is the GPU producer continuation of the accepted CPU authorization:

- branch: `hrl/c16-gpt-oss-20b-third-moe-authorization-174new-v28`
- HEAD: `e88ad8a8dde09209b7919c30fe50958414718c1f`
- decision: `C16_GPT_OSS_20B_THIRD_MOE_AUTHORIZATION_174NEW_V28_PASS`

Suggested implementation branch:

`hrl/c16-gpt-oss-20b-s2-producer-109-v29`

Use node109's existing Linux Git workflow and authentication. Do not install/configure `gh`. Do not use a Windows repository mirror.

## GPU serialization

Before CUDA/profiler work, inspect `/data/c16/locks/c16_gpu_campaign.lock` and acquire it normally.

If another C16 GPU Goal (including DeepSeek V27) is active, wait/stop cleanly rather than bypassing or killing it.

`FORMAL_ADMISSION_CONCURRENCY=1`

---

# Accepted model / asset authority

Model:

`openai/gpt-oss-20b`

Revision:

`6cee5e81ee83917806bbde320786a8fb61efebee`

Canonical node164 root:

`/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/gpt-oss-20b/6cee5e81ee83917806bbde320786a8fb61efebee`

Accepted receipt:

- schema: `C16_MODEL_ASSET_RECEIPT_V1`
- receipt SHA256: `6afcde98128fa758ecefdcae5fb2c316e4f23a04dbb0ee2cbd0413e81ad81fc8`
- config SHA256: `3a2a26ded679375b7928ddeca59764df7cea83220c1961035f6d6e232659e9ce`

The canonical asset is already downloaded and finalized. **Do not run `hf download`, do not redownload shards, and do not re-finalize the node164 asset.**

The native HF runtime subset is exactly the files marked `runtime_subset=YES` in V28 `ASSET_FILE_MANIFEST.tsv`, including:

- `chat_template.jinja`
- `config.json`
- `generation_config.json`
- `model-00000-of-00002.safetensors`
- `model-00001-of-00002.safetensors`
- `model-00002-of-00002.safetensors`
- `model.safetensors.index.json`
- `special_tokens_map.json`
- `tokenizer.json`
- `tokenizer_config.json`

Do not copy the Metal alternate checkpoint or `original/` duplicate representation merely for execution.

If node109 cannot directly access the canonical node164 runtime subset, materialize/copy **only this exact runtime subset** using the existing approved C16 model-transfer mechanism, preserve relative names, verify receipt SHA256/size for every transferred file, and record the local execution root. Do not copy the full 41.3GB multi-representation asset tree.

Large-file identity may rely on the accepted V28 hash-bound receipt plus transfer verification; do not mechanically rehash tens of GB repeatedly unless evidence conflicts.

---

# Architecture / deployment authority

Accepted V28 architecture:

- model class: `GptOssForCausalLM`
- 24 decoder layers
- hidden size: 2880
- 64 attention heads
- 8 KV heads
- head dim: 64
- 32 local experts
- natural top-4 experts/token
- expert intermediate size: 2880
- expert MLP: packed `gate_up_proj` -> activation -> packed `down_proj`
- expert weights: native MXFP4 block tensors + UE8 scales
- attention/router/embedding/lm_head remain non-expert higher precision per local quantization config

Native expert storage includes:

- `experts.gate_up_proj_blocks` + `gate_up_proj_scales`
- `experts.down_proj_blocks` + `down_proj_scales`

Do not dequantize expert weights to BF16 merely for convenience or cross-lineage matching.

Do not requantize, change top-k, change expert count, replace kernels, or use a backend that changes the native packed/grouped expert semantics.

---

# Stage 0 — exact node109 runtime bring-up and capacity gate

V28 intentionally did not pin an unverified GPU runtime. V29 must establish it on node109.

Create/use a dedicated gpt-oss runtime environment rather than mutating successful Qwen/DeepSeek environments.

Record exactly:

- Python
- torch
- CUDA runtime and driver
- transformers / model implementation commit or package version
- Triton and any custom-kernel package versions
- exact `GptOssForCausalLM` implementation source identity
- attention backend actually selected
- MoE backend actually selected
- native MXFP4 execution path
- grouped/fused expert-kernel behavior
- GPU identity

Hard gate: prove that expert execution remains native MXFP4 block+scale semantics.

Capacity policy:

1. Prefer native full-resident execution only if an explicit memory precheck and bounded S0 load prove it fits RTX4080 16GB without semantic/backend change.
2. If full-resident is unsafe/OOM, use exact layer-local/streaming execution only if it preserves the same native MXFP4 expert storage and target backend.
3. Do not fall back to BF16/FP16 dequantized experts, CPU-offload execution that changes target kernel, replacement GEMMs, altered top-k, or synthetic target hidden state.

If no native MXFP4 semantics-preserving path exists on RTX4080, fail closed with a typed runtime blocker before formal capture.

---

# Stage 1 — freeze exact Harmony S2 input on node109

V28 bound the common semantic source but intentionally left the model-specific Harmony token freeze to node109.

Accepted common source authority:

`docs/vm_tlb/review_packs/C16_QWEN3_30B_S2_T2048_STATE_REPLAY_109_V1/S2_INPUT_LOCAL_AUTHORITY.tsv`

Common source SHA256:

`cdd532689295d9e934a1307e3c9c63b288b9f9a702d712cf6b516b24aaf1db80`

Canonical tokenizer/template hashes from V28:

- `tokenizer.json`: `0614fe83cadab421296e664e1f48f4261fa8fef6e03e63bb75c20f38e37d07d3`
- `tokenizer_config.json`: `9279e942392b742d633c7adbb89ebe002c98399db8926a7af5125c726f404070`
- `chat_template.jinja`: `a4c9919cbbd4acdd51ccffe22da049264b1b73e59055fa58811a99efbd7c8146`
- `special_tokens_map.json`: `dd5e191d20c12d2fee1da5bae14ca1db0f5f4215300af691f23cdee97120a293`

Required scenario:

`S2_TEXT = B1 / T2048 / D32`

Using the exact native Harmony/chat-template + canonical tokenizer revision, derive and freeze the model-specific serialized input / token IDs from the common semantic source.

Persist:

- exact source path/ref/SHA
- exact Harmony/chat-template identity
- tokenizer hashes
- serialized formatted-input SHA
- exact token IDs or deterministic token-matrix representation
- exact token count
- token-sequence/matrix SHA with defined serialization
- special-token policy

After freezing, all later producer stages must consume the frozen representation. Do not re-author raw prose and do not silently pad/truncate.

If the canonical source cannot produce the required S2/T2048 authority under native gpt-oss input semantics, fail closed with a typed input-authority blocker.

S0/T128 bring-up may be used only if it materially reduces runtime bring-up risk; it is diagnostic and does not replace S2 authority.

---

# Stage 2 — exact S2 semantic execution and natural routing

Execute the exact S2 semantic path using the capacity-safe native MXFP4 strategy established in Stage 0.

Requirements:

- no synthetic hidden state at the target layer
- true upstream state propagation
- true position/attention semantics
- true natural router logits
- true native expert dispatch/grouping
- true route-weighted combine

Choose an early practical MoE layer only after confirming it actually executes under the runtime.

For the S2 first decode state, persist a router receipt with:

- exact layer/decode token/state identity
- router-logits shape/dtype/hash
- natural top-4 expert IDs
- route weights
- expert/group dispatch mapping
- any sorting/indexing buffer semantics

Natural routing is mandatory. Never force an expert ID to simplify tracing.

---

# Stage 3 — native MoE target qualification

Do not assume the native runtime exposes a BF16-style per-expert `down_proj` kernel.

Use the V28 target hierarchy:

1. natural selected-expert true down path, only if clean dynamic expert-specific weight/input/output attribution is proven;
2. native grouped/fused expert-down target with lossless selected-expert/group attribution;
3. broader routed-expert weight-consumption target with explicitly narrower evidence class.

The accepted packed checkpoint representation is not itself evidence of a single-expert runtime kernel.

For each candidate, observe actual runtime dataflow:

`hidden -> router -> top-4 -> dispatch/sort/group -> packed gate/up -> activation -> packed down -> route-weighted combine`

Record:

- actual function/kernel names
- grid/block
- fused/grouped dimensions
- native MXFP4 blocks/scales consumed
- activation/input/output ranges
- expert/group indexing metadata
- same-process storage ranges

Select exactly one primary formal anchor for this Goal, maximizing semantic comparability without inventing attribution.

Required target classification must be explicit, e.g. one of:

- `NATURAL_SELECTED_EXPERT_DOWN_MXFP4`
- `NATIVE_GROUPED_FUSED_EXPERT_DOWN_MXFP4`
- `ROUTED_EXPERT_PACKED_WEIGHT_CONSUMER_MXFP4`

or a more precise evidence class justified by runtime facts.

---

# Stage 4 — exact replay / signature gate

Create an isolated or bounded replay only if it preserves the same native MXFP4 target backend.

Require:

- exact target input/state
- native packed weight blocks/scales
- same route/expert/group identity where semantically required
- equivalent or bitwise-identical output as appropriate
- in-context vs replay function/grid/block signature equivalence or explicitly documented backend delta

Do not dequantize to make replay easier.

If a clean isolated replay would change native grouped/fused semantics, retain an in-context bounded target instead and state that clearly.

---

# Stage 5 — fresh SM89 static/address-path audit

For the selected primary target:

- enumerate every direct GLOBAL MREF in the exact code object
- independently audit LDGSTS / global-to-shared / other address-bearing paths
- distinguish load sources and store destinations
- derive address register pairs from actual SASS when necessary
- freeze the full static address-bearing set

Do not inherit register assumptions from Qwen/DeepSeek.

Use one or more positive canaries before full sharding.

---

# Stage 6 — formal capture

Use the known-good C16 V20/V23R1/Q30-V3 warp-regsource lifecycle where compatible.

For every static address-bearing shard:

- fresh process/output directory
- clear inherited `C16_*` and `CUDA_INJECTION64_PATH`
- exact function/static selector
- exact occurrence selector if needed
- sufficient capacity
- same-process ADDRESS_CONTEXT
- terminal closure
- drop=0
- overflow=0
- explicit `EXECUTED_SHARD` / `ZERO_EXECUTION_PROVEN`

If the selected target is grouped/fused, object membership must preserve selected expert/group identity rather than collapsing all packed expert addresses into one fake single-expert object.

Before admission independently decode all shards and verify:

- expected shard set complete
- full target scope
- no accidental CTA slicing
- no wrong occurrence
- lossless typed object membership at the level authorized by the evidence class

Create exactly one formal run for the primary gpt-oss MoE anchor.

Transfer to node164, verify destination/hash closure, perform one formal admission, and wait for positive ACK.

`FORMAL_ADMISSION_CONCURRENCY=1`

Do not admit diagnostic/rejected captures.

---

# Stage 7 — bounded profiling and scientific interpretation

Preserve bounded NSYS/NCU evidence where practical.

NCU numeric claims require explicit native values and units. If unavailable or backend-specific, mark typed `NOT_COMPARABLE` rather than inventing conversions.

Produce a scoped comparison-ready summary containing:

- natural top-4 routing receipt
- selected evidence class
- native MXFP4 deployment details
- static address-path counts
- executed/zero partition
- active-lane event totals
- per-shard 128B-line and 4K/64K/2M page distributions
- typed object-membership distribution
- NCU typed status

Do not yet declare a universal three-lineage common result. This producer creates the third formal anchor; an independent 174-new consumer must adjudicate the three-lineage comparison afterward.

Forbidden constructs:

- cross-process absolute VA comparison
- cross-replay VA union
- cross-shard chronology
- reconstructed reuse distance
- cache/TLB causality from this capture
- population routing claims from one frozen decode state

---

# Stage 8 — next-step authorization

If the formal gpt-oss anchor is accepted, recommend:

`PROMOTE_TO_THREE_LINEAGE_MOE_INDEPENDENT_CONSUMER`

Do not automatically capture additional gpt-oss operators/scenarios merely for density.

---

# Required review pack

Create:

`docs/vm_tlb/review_packs/C16_GPT_OSS_20B_S2_PRODUCER_109_V29/`

Include at least:

- `UPSTREAM_AUTHORITY.tsv`
- `MODEL_RUNTIME_AUTHORITY.json`
- `NATIVE_MXFP4_CAPACITY_RECEIPT.json`
- `S2_INPUT_AUTHORITY.json`
- `S2_STATE_RECEIPT.json`
- `NATURAL_ROUTING_RECEIPT.json`
- `MOE_RUNTIME_DATAFLOW.json`
- `MOE_TARGET_QUALIFICATION.json`
- `REPLAY_SIGNATURE.json`
- `STATIC_PATH_AUDIT.json`
- `FORMAL_SUMMARY.json`
- `ADMISSION_ACK.json`
- `NCU_TYPED_EVIDENCE.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `NEXT_STEP_AUTHORIZATION.json`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Full PASS only if native MXFP4 semantics, natural routing, target attribution, complete formal capture, and positive ACK all close.

Preferred decision:

`C16_GPT_OSS_20B_S2_PRODUCER_109_V29_PASS_WITH_NATIVE_MOE_ANCHOR`

Fail closed with a typed blocker if the native MXFP4 runtime or defensible target attribution cannot be established.

---

# Git closure / cleanup

Complete:

`review pack -> SHA256SUMS -> commit -> push -> canonical git ls-remote verification -> clean worktree`

Do not ask the user to perform routine Git closure.

At end:

- release `/data/c16/locks/c16_gpu_campaign.lock`
- verify no gpt-oss/profiler CUDA processes remain
- confirm GPU returns to expected baseline
- STOP

Do not stop after runtime/input/target qualification if downstream formal stages remain executable.