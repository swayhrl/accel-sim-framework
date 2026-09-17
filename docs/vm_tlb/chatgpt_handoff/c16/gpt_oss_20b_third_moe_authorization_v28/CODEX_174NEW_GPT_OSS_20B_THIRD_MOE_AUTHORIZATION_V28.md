# C16 gpt-oss-20b third independent MoE lineage authorization — 174-new V28

## Execution mode

Execute in **GOAL MODE**. This is a CPU-only authorization, canonical-input, architecture/dataflow, and node109 producer-contract Goal.

Do not run GPU. Do not modify accepted C16 raw/catalog. Do not stop after asset inspection if downstream CPU-only stages remain executable.

Use:

- repo: `/root/workspace/accel-sim-framework`
- durable storage: `/root/share/mnt164`
- existing 174-new `gh auth` + HTTPS credential integration

Do not switch Git to SSH.

Suggested implementation branch:

`hrl/c16-gpt-oss-20b-third-moe-authorization-174new-v28`

## Scientific motivation / upstream authority

The accepted two-lineage MoE comparison is:

- Qwen3-30B-A3B natural-routed expert down projection
- DeepSeek-V2-Lite natural-routed expert down projection
- accepted V25 decision: `C16_Q30_DEEPSEEK_TWO_LINEAGE_MOE_FAMILY_COMPARISON_174NEW_V25_PASS`

V25 explicitly requires a **third independent MoE lineage** before any broad cross-model common claim.

Candidate third lineage:

`openai/gpt-oss-20b`

Known canonical asset candidate on node164, to be independently verified in this Goal:

`/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/gpt-oss-20b/6cee5e81ee83917806bbde320786a8fb61efebee`

Expected revision candidate:

`6cee5e81ee83917806bbde320786a8fb61efebee`

Do not trust the path/revision merely because this handoff names them. Verify the canonical receipt/inventory and exact model metadata.

External architecture expectation for local verification, not authority by itself:

- ~20.9B total parameters
- ~3.6B active parameters/token
- 24 layers
- 32 experts
- top-4 active experts/token
- native MoE checkpoint weights use MXFP4
- attention alternates local/banded and dense patterns

The local canonical config/model source and executable runtime contract are authoritative for C16.

---

# Stage 0 — canonical asset authority

Audit the node164 gpt-oss-20b asset without changing it.

Required outputs:

- exact model ID
- exact revision
- exact canonical root
- exact relative file set
- per-file sizes and SHA256 or canonical receipt hashes
- config SHA256
- tokenizer/config hashes
- safetensors/index/original-format inventory
- deterministic inventory/manifest SHA256
- total repository payload bytes
- separately named executable checkpoint payload bytes for each supported format

Important: the canonical directory may contain more than one checkpoint/runtime representation. Do not confuse repository total bytes with the exact file subset loaded by the chosen runtime.

Apply C16 identity policy:

- exact file set + per-file hashes + revision/config = hard identity
- aggregate totals = derived metadata

Fail closed on real revision/config/file integrity mismatch.

---

# Stage 1 — exact architecture and native quantization contract

Reconstruct the actual gpt-oss-20b architecture from local config/model source.

Record at least:

- architecture class
- number of decoder layers
- hidden/residual width
- attention head/KV-head structure
- attention pattern by layer if alternating
- number of experts
- experts selected per token
- router implementation
- expert intermediate dimensions
- expert MLP projection structure
- expert activation function
- exact checkpoint dtype/quantization format by tensor family
- MXFP4 layout/scale representation where applicable
- embedding/lm_head precision

Do not convert native MXFP4 expert weights to BF16 merely to make comparison easier.

This third lineage is allowed to represent a different deployment/precision regime. Any later cross-lineage comparison must keep that deployment difference explicit.

---

# Stage 2 — runtime selection and node109 execution feasibility

Determine the exact runtime needed on node109 RTX4080.

Do not reuse an older transformers/runtime merely because it is installed if it cannot execute the exact gpt-oss architecture/quantization semantics.

Produce a dedicated-runtime contract containing:

- Python version
- torch version constraint
- transformers/model implementation version
- Triton/custom-kernel requirements
- CUDA compatibility requirements
- exact model class
- exact attention backend
- exact MoE backend
- exact MXFP4 execution path
- whether expert kernels are grouped/fused
- whether full-resident native checkpoint is expected to fit 16GB

Prefer **native full-resident execution** if the exact checkpoint/runtime is designed to fit and node109 producer precheck proves it fits without changing semantics.

If full-resident does not fit, authorize exact layer-local/streaming replay only if it preserves native MXFP4 expert execution and the same target backend. Do not dequantize, requantize, lower/raise precision, change expert count/top-k, or replace kernels merely to fit.

Do not install or mutate node109 from this CPU Goal; write the producer contract only.

---

# Stage 3 — canonical C16 input authority for gpt-oss

gpt-oss requires its native Harmony/tokenizer formatting. Do not feed raw C16 prose directly if that bypasses the model's required input format.

Bind the same C16 common semantic source used for cross-model S2_TEXT, but create/freeze a **model-specific gpt-oss token authority** using the exact canonical tokenizer/chat-template/harmony implementation.

Required primary scenario:

`S2_TEXT = B1 / T2048 / D32`

Also freeze a small S0/T128 bring-up input only if it materially reduces node109 bring-up risk.

For every frozen input persist:

- common source artifact/ref and SHA
- tokenizer model/revision/hash
- chat/Harmony template identity
- exact serialized formatted input or token IDs
- exact token count
- payload SHA256
- token-matrix/token-sequence SHA using a defined serialization
- special-token policy
- proof that producer can consume frozen IDs/serialized representation without re-authoring the prompt

If an exact T2048 gpt-oss input cannot be created from the existing common semantic source without violating model input semantics, emit a typed blocker rather than padding/truncating silently.

Store new prospective input authority under the existing C16 provenance/input namespace, not accepted raw/catalog.

---

# Stage 4 — natural-routing MoE source/runtime dataflow

Reconstruct the true runtime MoE dataflow for one representative decoder layer:

`hidden -> router logits -> natural top-4 -> dispatch/grouping -> expert gate/up path -> activation -> expert down path -> route-weighted combine`

Record whether the executable runtime uses:

- per-expert modules
- grouped GEMM
- fused MXFP4 expert kernels
- packed expert-weight tensors
- token/expert sorting or indexing buffers

Do not assume a conventional BF16 `nn.Linear down_proj` exists as a separately launched kernel.

---

# Stage 5 — third-lineage semantic target plan

Primary scientific objective is to obtain a natural-routed expert memory anchor comparable at the **MoE-family semantic level** to Q30/DeepSeek.

Target hierarchy:

1. a naturally selected expert's true down-projection path with clean expert-specific weight/input/output binding, if the native runtime exposes it;
2. a native grouped/fused expert-down target with lossless selected-expert/group attribution;
3. a broader routed-expert weight-consumption target only if the first two are impossible and the evidence class is explicitly narrower/different.

Do not force a particular expert ID.

For the future node109 producer, require natural router receipt containing:

- exact layer/decode state
- router logits hash/shape
- natural top-4 expert IDs
- route weights
- selected-expert/group mapping

Do not label a grouped/fused kernel as a single-expert down projection unless dynamic/object evidence proves that attribution.

---

# Stage 6 — cross-lineage comparability contract

Produce an explicit matrix comparing planned gpt-oss evidence to the accepted Q30 and DeepSeek MoE anchors.

At minimum classify:

- semantic family match
- decode-state relation
- input width
- output width
- expert-weight precision/format
- expert count
- active experts/token
- routed/shared-expert topology
- expected kernel family
- per-expert vs grouped/fused implementation
- which metrics are directly descriptive-comparable
- which metrics require normalization
- which claims remain deployment-specific

Do not predeclare a three-lineage common result.

A future three-lineage common claim is authorized only after gpt-oss formal raw is independently consumed and shows a pattern supported across all three lineages.

---

# Stage 7 — node109 producer contract

Generate a complete executable contract for one node109 Goal that can do:

`runtime bring-up -> exact S2 execution -> natural routing -> semantic target qualification -> replay/signature -> static/path audit -> known-good warp-regsource canary -> formal capture -> serial admission/ACK -> review pack`

The producer contract must specify:

- exact canonical asset subset/path
- exact runtime creation/use instructions at policy level
- exact frozen input authority
- exact semantic target hierarchy
- capacity fallback policy
- stop conditions
- expected review artifacts

Do not require a separate planning round unless there is a genuine unresolved CPU-side blocker.

---

# Required review pack

Create:

`docs/vm_tlb/review_packs/C16_GPT_OSS_20B_THIRD_MOE_AUTHORIZATION_174NEW_V28/`

Include at least:

- `ASSET_AUTHORITY.json`
- `ASSET_FILE_MANIFEST.tsv`
- `ARCHITECTURE_AND_QUANTIZATION.json`
- `RUNTIME_AUTHORIZATION.json`
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

`C16_GPT_OSS_20B_THIRD_MOE_AUTHORIZATION_174NEW_V28_PASS`

Only use PASS if asset, input, runtime, and producer target contract all close sufficiently for node109 execution.

---

# Git closure

Use explicit repo path and current 174-new HTTPS/gh credential integration.

Complete:

`review pack -> SHA256SUMS -> commit -> push -> LOCAL == git ls-remote == authenticated gh api -> clean worktree -> STOP`

If stdout capture is empty, redirect decisive output to `/tmp` and read it rather than declaring missing evidence.