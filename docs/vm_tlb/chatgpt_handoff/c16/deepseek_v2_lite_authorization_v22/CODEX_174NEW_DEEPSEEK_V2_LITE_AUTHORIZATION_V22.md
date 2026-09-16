# C16 DeepSeek-V2-Lite dynamic authorization and producer contract — 174-new V22

## Execution mode

Execute this task in **GOAL MODE**.

This is one autonomous **CPU-only authorization/planning Goal** for the next C16 model lineage after Qwen3 closure. Do not run GPU work and do not mutate accepted raw/catalog. Do not stop after static inspection while downstream CPU-side authorization stages remain executable.

Use the established 174-new workflow:

- local Git repository: `/root/workspace/accel-sim-framework`
- durable model/data mount: `/root/share/mnt164`
- existing `gh auth` + HTTPS credential integration
- do **not** switch to SSH or generate SSH keys
- known Codex stdout-capture issue: if stdout/stderr is unexpectedly empty, redirect decisive output to `/tmp/...` files and read them; empty captured stdout alone is not evidence of absence.

Canonical repository identity:

`https://github.com/swayhrl/accel-sim-framework.git`

## Mainline context

Qwen3 is closed for the current C16 lineage sampling plan. Do not propose additional Qwen3 captures merely for coverage density.

The next producer lineage is:

`DeepSeek-V2-Lite`

The purpose of V22 is to produce a **hash-closed execution authorization and producer contract** that node109 can execute directly in the next GPU Goal, without rediscovering DeepSeek structure during capture.

## Known prior static facts — verify, do not blindly copy

Previous C16 static work recorded DeepSeek-V2-Lite as approximately:

- 27 decoder layers
- hidden size 2048
- 16 attention heads
- MLA-style attention, including:
  - `kv_lora_rank = 512`
  - `qk_nope_head_dim = 128`
  - `qk_rope_head_dim = 64`
  - `v_head_dim = 128`
- dense early layer(s), followed by MoE
- MoE configuration recorded as:
  - 64 routed experts
  - 2 shared experts
  - top-6 routing
  - MoE intermediate size 1408
- exact model tensor bytes previously recorded as `31,412,968,448`
- an earlier revision authority with prefix `604d566...`

These are **expected facts to audit**, not permission to invent a full revision hash or path. Resolve exact model name, exact full revision, exact asset namespace, exact config, tokenizer, model index, shard list and hashes from the existing local/Git/node164 authorities.

If an exact static fact differs, record the discrepancy rather than silently normalizing it.

## Goal

Close all CPU-side prerequisites needed for a node109 DeepSeek-V2-Lite S2 producer campaign, preserving the true **MLA + MoE** structure.

Do not simplify DeepSeek-V2-Lite to ordinary MHA + dense MLP.

---

## Stage 1 — exact asset/static authority

Perform a bounded search only for DeepSeek-V2-Lite authorities in:

- repository `docs/vm_tlb/` and related C16 receipts;
- `/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/`;
- existing local model-authority files.

Do not enumerate unrelated model assets.

Record:

- exact Hugging Face/model identifier;
- exact full revision SHA;
- canonical asset path;
- config SHA256;
- tokenizer asset hashes;
- model index SHA256;
- exact checkpoint shard list and hashes where practical;
- exact tensor byte count;
- dtype authority;
- architecture class / `auto_map` / custom-code requirements;
- any local modeling source files and their hashes if remote/custom code is used.

Verify the structural facts needed later:

- decoder layer count;
- dense-vs-MoE layer boundary;
- routed/shared expert counts;
- top-k routing;
- MLA dimensions;
- cache-related config;
- rope/position config;
- whether `use_cache` is enabled/meaningful in this implementation.

Produce an explicit `DEEPSEEK_STATIC_AUTHORITY.json`.

---

## Stage 2 — runtime/API contract

Determine the exact runtime contract required to instantiate and execute the pinned model code without GPU execution.

Audit:

- current local Transformers/tokenizers/PyTorch compatibility where inspectable;
- whether model code is native Transformers or pinned custom code;
- exact forward signatures for decoder layer, attention/MLA module, cache arguments and MoE module;
- cache object/type and cache tensor layout;
- whether custom kernels/extensions are required merely for correctness;
- whether optional acceleration packages alter semantics/backend.

Do not install arbitrary latest packages in this authorization Goal.

If a runtime bootstrap is required for node109, specify exact pinned versions/wheels/source hashes in `RUNTIME_CONTRACT.json`.

Network access in the future producer Goal may be authorized only for exact pinned runtime wheels if needed; model weights/input/model-code substitution is not authorized.

---

## Stage 3 — canonical prospective input for DeepSeek

Do **not** reuse Qwen3 token IDs.

Locate the canonical V2 prospective-input source authority used by C16. Determine whether a DeepSeek-V2-Lite payload already exists and is validated.

If it exists:

- verify exact source hash;
- tokenizer authority;
- tokenization policy;
- payload hash;
- scenario dimensions.

If it does not exist, derive the DeepSeek payload using the exact canonical source and the existing V2 tokenization/truncation policy only. Do not invent a new policy.

Primary required scenario:

`S2_TEXT B1 / T2048 / D32`

Optionally prepare `S3_TEXT B1 / T8192 / D16` only if the same canonical policy supports it cleanly; V22 must not make S3 a blocker for the first DeepSeek producer.

Record exact token count, source hash, tokenizer hash and payload SHA256 in `DEEPSEEK_V2_INPUT_AUTHORITY.json`.

If the existing V2 policy cannot produce an unambiguous DeepSeek payload, fail closed with a typed input-authority blocker rather than inventing token IDs.

---

## Stage 4 — capacity and exact execution-mode authorization

The model is much larger than the node109 RTX4080 memory budget, so do not require full-resident BF16 execution if it is infeasible.

Evaluate and authorize an exact semantic execution mode analogous in rigor to the Qwen3 layer-streaming workflow, but adapted to the real DeepSeek implementation.

Preferred authorization if feasible:

`EXACT_SEMANTIC_LAYER_STREAMING_REPLAY`

The contract must preserve:

- exact BF16 checkpoint tensors;
- true embedding/input;
- sequential true decoder-layer execution;
- true position/rope state;
- true cache state in the implementation's actual MLA cache representation;
- true router outputs and selected experts;
- true next-token state where first-decode replay requires it;
- exact target-layer/module weights;
- no synthetic hidden state;
- no synthetic MLA/KV state;
- no fake routing/expert IDs;
- no lower precision solely to fit memory;
- no backend substitution solely to fit memory.

If the model implementation makes exact layer streaming impossible, identify the exact blocker and bounded alternative. Do not silently fall back to CPU offload or another attention implementation without semantic-equivalence proof.

Produce `EXECUTION_MODE_AUTHORIZATION.json`.

---

## Stage 5 — reconstruct the real MLA dataflow

Inspect the pinned DeepSeek implementation and produce a **typed first-decode MLA dataflow**, using actual module/tensor names from code.

Do not force Qwen3 terminology onto DeepSeek.

At minimum identify, where present:

- query projection/compression path;
- KV compression / latent representation path;
- rope-specific K component;
- actual cached tensors and shapes;
- cache update path;
- latent-to-attention operand expansion/materialization path;
- attention-score operand path;
- attention-value operand path;
- output projection.

For each important handoff record expected tensor semantics, shape formulas, storage role and whether the tensor is:

- `MLA_CACHE_STORAGE`
- `MLA_CACHE_DERIVED_BUFFER`
- `ATTENTION_CORE_OPERAND`
- projection/weight data
- other typed role.

The key scientific question is **what DeepSeek actually stores and rereads during decode**, not whether it resembles Qwen3 `repeat_kv`.

### MLA candidate target selection

Select one primary node109 formal target that is both:

1. materially characteristic of MLA / compressed-KV behavior; and
2. capable in principle of same-process dynamic-address attribution.

Preferred evidence classes, in order:

- direct read of true MLA cache/latent storage;
- exact materialization/expansion that directly reads MLA cache storage;
- if the core reads a proven derived buffer, classify it explicitly as derived-buffer evidence rather than direct cache read.

Do not choose ordinary q/k/v/o projection GEMV merely because it is easy to capture.

Record:

- exact module/operation;
- target layer;
- why it is uniquely MLA-relevant;
- expected source object/range;
- replay requirements;
- qualification gates;
- fallback candidate if the primary cannot be losslessly bound.

Produce `MLA_TARGET_PLAN.json` and `MLA_DATAFLOW.md`.

---

## Stage 6 — reconstruct the real MoE dataflow

Identify the exact first MoE decoder layer from the pinned config/code; do not assume a layer number without verification.

Reconstruct:

`hidden -> router/gate -> top-k selection -> routed experts -> shared expert(s) -> combine`

Record:

- router module/tensor shapes;
- exact top-k and normalization policy;
- first MoE layer index;
- routed expert module naming/layout;
- shared expert module naming/layout;
- whether execution is per-expert PyTorch modules, grouped/fused kernels, or another implementation;
- how selected expert IDs map to weight storage;
- whether expert weight ranges can be losslessly identified in the same process.

### MoE candidate target selection

Select one primary S2 formal target that captures a genuinely MoE-specific memory behavior.

Preferred candidates:

- a naturally selected routed-expert weight-read path with exact expert-ID authority;
- a grouped/fused expert kernel whose participating expert weight storage can be losslessly attributed;
- an expert materialization/gather path if that is the real implementation bottleneck.

Avoid using the router alone as the only MoE memory anchor unless no expert-data path can be qualified; router-only behavior does not represent expert-weight memory.

The target must use **natural routing from the canonical input**. Do not force an expert ID or fabricate router output.

Record the natural selected experts for the target token/state where CPU/static inspection can determine the contract; actual GPU producer must verify them from exact execution.

Produce `MOE_TARGET_PLAN.json` and `MOE_DATAFLOW.md`.

---

## Stage 7 — producer ordering and formal-admission plan

Create one node109 producer contract with this default ordering:

1. exact DeepSeek S2 execution/runtime smoke;
2. exact semantic state generation;
3. MLA target qualification and replay/signature gate;
4. MLA fresh static/global-address-path audit;
5. MLA complete formal capture;
6. serial Pipeline admission and positive ACK;
7. only after MLA ACK, MoE exact state/route qualification;
8. MoE replay/signature/static audit;
9. MoE complete formal capture;
10. serial Pipeline admission and positive ACK;
11. bounded NCU evidence for each qualified target;
12. producer review pack.

Hard rule remains:

`FORMAL_ADMISSION_CONCURRENCY=1`

Never place MLA and MoE admissions in flight simultaneously.

If MLA is qualified but MoE hits a genuine semantic blocker, the producer may close with scoped MLA evidence plus typed MoE blocker; do not discard valid MLA evidence.

If both qualify, capture both in the same large producer Goal rather than creating unnecessary micro-rounds.

---

## Stage 8 — producer contract and stop conditions

Produce a machine-readable and human-readable producer contract containing:

- exact model/revision/assets;
- exact canonical input;
- runtime/bootstrap pins;
- execution mode;
- exact target layers/modules;
- MLA primary/fallback target;
- MoE primary/fallback target;
- expected semantic state tensors;
- same-process address-context requirements;
- static/path audit requirements;
- formal capture gates;
- admission ordering;
- NCU evidence rules;
- allowed bounded repairs;
- fail-closed conditions.

Fail closed for:

- model/revision/hash mismatch;
- ambiguous canonical input;
- runtime requiring unpinned/untrusted model-code substitution;
- inability to preserve exact MLA cache semantics;
- inability to preserve natural MoE routing semantics;
- candidate target that cannot be semantically distinguished without launch-order inference;
- any proposal to simplify MLA to ordinary MHA or MoE to dense MLP.

Do not fail merely because the full 31GB checkpoint cannot reside on the RTX4080 at once; exact semantic streaming is the intended capacity strategy if validated.

---

## Required review pack

Create:

`docs/vm_tlb/review_packs/C16_DEEPSEEK_V2_LITE_AUTHORIZATION_174NEW_V22/`

At minimum include:

- `DEEPSEEK_STATIC_AUTHORITY.json`
- `RUNTIME_CONTRACT.json`
- `DEEPSEEK_V2_INPUT_AUTHORITY.json`
- `EXECUTION_MODE_AUTHORIZATION.json`
- `MLA_DATAFLOW.md`
- `MLA_TARGET_PLAN.json`
- `MOE_DATAFLOW.md`
- `MOE_TARGET_PLAN.json`
- `PRODUCER_EXECUTION_CONTRACT.json`
- `PRODUCER_EXECUTION_CONTRACT.md`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Preferred PASS decision:

`C16_DEEPSEEK_V2_LITE_174NEW_V22_EXECUTION_AUTHORIZED`

Do not authorize GPU producer work if the exact model/input/runtime/execution semantics are not closed.

---

## Git transport closure

Suggested implementation branch:

`hrl/c16-deepseek-v2-lite-authorization-174new-v22`

Use 174-new's existing GitHub CLI + HTTPS credential setup. Do not switch authentication mechanisms.

After scientific closure:

1. commit only Goal-owned V22 changes;
2. push actual `HEAD:refs/heads/hrl/c16-deepseek-v2-lite-authorization-174new-v22`;
3. verify repository identity is `swayhrl/accel-sim-framework`;
4. verify nonempty SHA via `git ls-remote`;
5. verify the same SHA via authenticated `gh api`;
6. require `LOCAL == LS_REMOTE_SHA == GH_API_SHA`;
7. if stdout capture is unreliable, persist decisive output under `/tmp` and read from files.

Do not ask the user to perform routine Git closure manually.

## Completion

Report:

- implementation branch and final HEAD;
- final authorization decision;
- exact model/revision;
- exact S2 input authority;
- authorized execution mode;
- chosen MLA target;
- chosen MoE target;
- any typed gaps/blockers;
- whether node109 producer is authorized.

Then STOP.
