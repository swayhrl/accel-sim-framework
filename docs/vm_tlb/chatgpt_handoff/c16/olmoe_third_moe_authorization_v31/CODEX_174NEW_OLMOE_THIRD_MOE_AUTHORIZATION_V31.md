# C16 OLMoE third independent MoE lineage asset + authorization — 174-new V31

## Execution mode
Execute in GOAL MODE. CPU/network/storage task only. Do not run GPU. Do not modify accepted C16 raw/catalog.

Use:
- repo `/root/workspace/accel-sim-framework`
- durable node164 mount `/root/share/mnt164`
- asset root `/root/share/mnt164/huangrulin/c16_ai_workload/assets/models`
- existing 174-new HTTPS + gh credential integration
- existing Hugging Face authentication/tooling if download is needed

Do not use 174 local disk for large model payloads.

Suggested implementation branch:
`hrl/c16-olmoe-third-moe-authorization-174new-v31`

## Why this Goal exists
Accepted V25 establishes only a two-lineage MoE-family pattern from Qwen3-30B-A3B and DeepSeek-V2-Lite.

The attempted third lineage `openai/gpt-oss-20b` was correctly fail-closed on node109 because the authorized native MXFP4 path is unavailable on RTX4080 / SM89 and BF16 fallback would change deployment semantics.

Accepted blocker authority:
- branch `hrl/c16-gpt-oss-20b-s2-producer-109-v29`
- HEAD `82766d4ec1cf711e5c36d7f70afd1a395359126c`
- decision `C16_GPT_OSS_20B_S2_PRODUCER_109_V29_FAIL_CLOSED_NATIVE_MXFP4_SM89_UNSUPPORTED`

Do not reopen gpt-oss on SM89 in this Goal.

Candidate replacement third independent lineage:
`allenai/OLMoE-1B-7B-0125-Instruct`

Candidate expectations to verify from the exact immutable checkpoint/config, not assume:
- `OlmoeForCausalLM`
- 16 decoder layers
- hidden size 2048
- 64 experts
- natural top-8 experts/token
- per-expert intermediate size 1024
- BF16 checkpoint
- standard CUDA/PyTorch/Transformers path suitable for RTX4080 subject to producer precheck

The local downloaded checkpoint/config become authority, not this handoff's expectations.

---

# Stage 0 — check for an existing canonical asset first
Before downloading anything, search the existing C16 model asset catalog/root for an exact OLMoE-1B-7B-0125-Instruct asset and receipt.

If an exact hash-bound canonical asset already exists:
- verify and reuse it
- do not redownload
- do not duplicate it

If it does not exist, proceed to Stage 1.

---

# Stage 1 — resolve immutable upstream identity and download directly to node164
Resolve the current intended `allenai/OLMoE-1B-7B-0125-Instruct` checkpoint to an immutable Hugging Face revision/commit SHA before large download.

Persist the resolved model ID/revision and metadata.

Download directly into a node164 staging/cache location under the C16 asset namespace. Do not stage ~14GB on 174 local disk.

Use resumable `hf download`/huggingface_hub behavior with the exact immutable revision.

Download the complete canonical runtime asset required for the Hugging Face model, including:
- config
- generation config
- tokenizer files
- model safetensor shards
- safetensors index
- chat template/support files if present

Do not download third-party quantized derivatives.

If transfer is interrupted, resume; do not create a second competing copy.

---

# Stage 2 — canonical asset finalize / receipt
After download, verify:
- exact relative file set
- per-file sizes
- per-file SHA256
- config/tokenizer/index identities
- complete safetensor shard closure
- model ID/revision

Create a deterministic `MODEL_ASSET_RECEIPT.json` using the established C16 asset-receipt schema/pattern.

Finalize atomically into:
`/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/olmoe-1b-7b-0125-instruct/<immutable_revision>/`

Do not overwrite a conflicting existing finalized asset.

Distinguish hard identity fields from aggregate total-byte metadata according to C16 identity policy.

---

# Stage 3 — exact architecture/runtime contract
From the finalized local config/index and the exact Transformers implementation, reconstruct:
- architecture/model class
- layer count
- hidden size
- attention heads/KV heads
- max position length
- number of experts
- experts per token
- router implementation and normalization
- expert intermediate size
- expert projection structure (`gate_proj`, `up_proj`, `down_proj` or actual local names)
- checkpoint tensor dtype by family
- whether runtime dispatch is per-expert Python/module execution, grouped GEMM, or fused kernel under the intended runtime

Do not simplify the implementation into a generic MoE diagram where code evidence is available.

Runtime policy for node109:
- prefer a pinned Transformers/PyTorch CUDA runtime with exact OLMoE support
- BF16 checkpoint semantics must be preserved
- full resident is preferred only if actual RTX4080 precheck fits
- if full resident is too tight, authorize exact layer-local/streaming replay using the proven Q30/DeepSeek materialization pattern while preserving original BF16 target backend and natural routing
- no quantization solely to fit memory
- no forced expert/top-k changes

Produce an explicit node109 capacity/runtime contract; do not mutate node109 from this CPU Goal.

---

# Stage 4 — canonical C16 S2 input authority
Primary scenario:
`S2_TEXT = B1 / T2048 / D32`

Bind to the existing common semantic source already used by accepted Q30/DeepSeek C16 work.

Using the exact finalized OLMoE tokenizer/chat template, create and freeze model-specific S2 input authority.

Persist:
- exact common source artifact/ref + SHA
- tokenizer revision/files + hashes
- chat-template identity if used
- exact serialized input/token IDs
- exact token count 2048
- payload SHA256
- token-matrix/token-sequence SHA with documented serialization
- special-token policy
- proof no later re-authoring/retokenization is required on producer

Do not silently pad/truncate to hit 2048. If the C16 canonical input-construction procedure has an existing exact-token method, use that method and record it. Fail closed if exact T2048 cannot be constructed without violating source semantics.

Store prospective input authority in the existing C16 provenance/input namespace, not accepted raw/catalog.

---

# Stage 5 — MoE dataflow and target hierarchy
Reconstruct the true OLMoE routing/expert dataflow from exact source/runtime:
`hidden -> router logits -> natural top-k -> token/expert dispatch -> selected expert MLP -> route-weighted combine`

The future node109 producer must record a natural-routing receipt at the chosen S2 decode state:
- layer/decode state
- router-logit shape/hash
- natural top-k expert IDs
- router weights
- exact selected-expert activations

Primary target hierarchy:
1. natural selected expert `down_proj` with clean expert-specific weight/input/output binding
2. grouped/fused down-projection target with lossless selected-expert/group binding
3. broader selected-expert MLP weight-consumer path with explicitly narrower evidence class

Do not force an expert ID.

Do not choose a target merely because it resembles Q30/DeepSeek; preserve OLMoE runtime semantics.

---

# Stage 6 — three-lineage comparability contract
Construct a contract comparing planned OLMoE evidence with accepted Q30 and DeepSeek natural expert-down anchors.

Include:
- model/vendor/lineage
- scenario/decode-state relation
- hidden / down-proj input / output dimensions
- expert count
- active experts per token
- routing normalization/topology
- checkpoint precision
- per-expert vs grouped/fused execution
- semantic target class
- directly descriptive-comparable metrics
- normalized metrics
- deployment-specific differences

Do not declare a three-lineage common result yet.

Broad common may be evaluated only after OLMoE formal raw has been captured and independently consumed.

---

# Stage 7 — one-shot node109 producer contract
Generate a complete executable producer contract for a single future node109 Goal:
`asset-subset availability -> runtime/capacity precheck -> frozen S2 input -> exact S2 execution -> natural routing -> target qualification -> exact replay/signature -> static/path audit -> warp-regsource canary -> complete formal capture -> serial admission/ACK -> review pack`

The contract must prevent a new planning-only round unless a genuine scientific/runtime blocker exists.

`FORMAL_ADMISSION_CONCURRENCY=1` remains mandatory.

---

# Required review pack
Create:
`docs/vm_tlb/review_packs/C16_OLMOE_THIRD_MOE_AUTHORIZATION_174NEW_V31/`

Include at least:
- `ASSET_AUTHORITY.json`
- `ASSET_FILE_MANIFEST.tsv`
- `ARCHITECTURE_AND_RUNTIME.json`
- `CAPACITY_POLICY.json`
- `S2_INPUT_AUTHORITY.json`
- `MOE_RUNTIME_DATAFLOW.json`
- `MOE_TARGET_PLAN.json`
- `THREE_LINEAGE_COMPARABILITY_CONTRACT.json`
- `NODE109_PRODUCER_EXECUTION_CONTRACT.json`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Preferred PASS:
`C16_OLMOE_THIRD_MOE_AUTHORIZATION_174NEW_V31_PASS`

Only PASS if canonical asset + exact input authority + runtime/capacity policy + producer target contract are sufficiently closed for node109 execution.

---

# Git closure
Complete:
`review pack -> SHA256SUMS -> commit -> push -> LOCAL == git ls-remote == authenticated gh api -> clean worktree -> STOP`

If stdout capture is unexpectedly empty, redirect decisive output to `/tmp` and read it rather than declaring missing evidence.