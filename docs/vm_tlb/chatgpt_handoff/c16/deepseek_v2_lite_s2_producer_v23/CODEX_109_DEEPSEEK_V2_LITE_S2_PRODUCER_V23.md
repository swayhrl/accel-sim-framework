# C16 DeepSeek-V2-Lite S2 MLA + MoE producer — node109 V23

## Execution mode

Execute this task in **GOAL MODE**. This is one autonomous node109 GPU producer Goal.

Do not stop after setup, model/runtime preflight, state capture, target discovery, static audit, or the first formal target while downstream stages remain executable.

Use node109's existing Linux Git workflow and authentication. Do **not** install/configure `gh`, do not switch Git authentication, and do not use any local Windows repository mirror.

Preferred repo/worktree root:

`/home/huangrulin/workspace/accel-sim-framework`

or a fresh node109 worktree created from it.

## V22 authority

Consume the accepted CPU authorization review pack:

`docs/vm_tlb/review_packs/C16_DEEPSEEK_V2_LITE_AUTHORIZATION_174NEW_V22/`

Model authority:

- model: `deepseek-ai/DeepSeek-V2-Lite`
- revision: `604d5664dddd88a0433dbae533b7fe9472482de0`
- architecture: `DeepseekV2ForCausalLM`
- config SHA256: `f346286b0f1c8b044252fd54cb4fa78b9fab6472a6e8bebb9edfe03d414ea03d`
- model asset bytes: `31418842074`
- baseline capacity mode: `EXACT_SEMANTIC_LAYER_STREAMING_REPLAY`
- native full-resident: only if a producer precheck independently proves it feasible; do not change precision/backend merely to fit.

DeepSeek must preserve its actual architecture:

- MLA with compressed KV latent, `kv_a/kv_b` expansion, RoPE/nope split and reconstructed K/V;
- natural-routing MoE with router logits, top-k routing, selected expert MLPs and weighted combine.

Do **not** simplify it to ordinary MHA + dense MLP.

V22 formal-target candidates are discovery candidates, not pre-proven dynamic targets:

MLA:
- `mla_kv_latent_read`
- `mla_kv_b_expand`
- `attention_output_projection`

MoE:
- `router_topk_natural_routing`
- `selected_expert_down_proj`
- `moe_combine`

The producer must dynamically qualify the actual target before formal capture.

## Scientific objective

Build the first **native DeepSeek-V2-Lite S2 dynamic-memory anchor** for C16 using two orthogonal, architecture-specific paths:

1. one MLA target that is demonstrably tied to the actual MLA dataflow and, if possible, a real persistent/semantic KV-related storage object;
2. one natural-routing MoE target tied to a naturally selected routed expert and its true expert-weight/dataflow state.

The goal is not broad kernel coverage. The goal is two clean, auditable semantic anchors with exact state/replay equivalence and formal traces.

Run S2 only in this Goal. S3 is **deferred** until the independent consumer decides whether long-context scaling is the highest-value next dimension. Do not automatically run S3 just because V22 listed it as a supported scenario.

---

# Stage 0 — immutable input/model/runtime preflight

## 0.1 Exact model assets

On node109 verify the exact DeepSeek-V2-Lite revision and local asset authority.

Record:

- exact asset path;
- revision;
- config SHA256;
- tokenizer/config/model file hashes or deterministic asset receipt available in the existing C16 asset namespace;
- total bytes;
- runtime package versions;
- CUDA/driver/GPU identity.

Fail closed on revision/config mismatch.

Do not redownload or substitute a different DeepSeek revision if the canonical asset already exists.

## 0.2 Canonical S2 input

V22 intentionally left DeepSeek S2 input as:

`C16_PROSPECTIVE_COMMON_INPUT_V2`

with:

`PREEXECUTION_CANONICAL_AUTHORITY_REQUIRED`

Resolve this **only from the existing canonical V2 authority/manifest/artifact**. Do not author a new prompt, do not retokenize from prose, do not regenerate equivalent text.

Persist:

- exact source artifact/path;
- exact payload/token IDs actually consumed by DeepSeek;
- payload SHA256;
- token-count/scenario contract;
- proof that no retokenization/substitution occurred in V23.

Required scenario:

`S2_TEXT = B1 / T2048 / D32`

If the canonical DeepSeek S2 input cannot be uniquely resolved from existing C16 authority, STOP before GPU execution with a typed blocker.

## 0.3 Runtime/API contract

Before tracing, make the actual DeepSeek implementation concrete.

Record:

- Python / torch / transformers / remote-code package versions;
- exact modeling source/module used;
- attention implementation/backend;
- cache object/API type;
- MoE implementation path;
- whether model uses custom remote code;
- whether any fused/grouped kernels are active.

Do not assume V22's static dataflow description equals the exact runtime implementation.

## 0.4 Capacity precheck

Measure GPU capacity and expected model/state residency.

If full-resident BF16 is truly feasible, it may be used only with an explicit receipt.

Otherwise use the authorized:

`EXACT_SEMANTIC_LAYER_STREAMING_REPLAY`

Do not use quantization, lower precision, CPU offload that changes the target execution backend, synthetic hidden states, or synthetic KV merely to fit memory.

---

# Stage 1 — exact S2 semantic-state engine

Construct an exact first-decode state chain for S2.

The state engine must preserve true model semantics through all preceding layers needed to reach each target layer:

checkpoint
→ selective exact parameter loading
→ true hidden state
→ true positions / RoPE state
→ true cache state
→ true natural MoE routing
→ true next-token decode state
→ freeze the semantic target state
→ exact isolated replay

Prefer the smallest exact layer-streaming implementation that reproduces the in-context tensor/operator outputs bitwise or with a clearly justified exact numeric criterion.

Persist hashes for all frozen target inputs and outputs used in later replay.

Do not fabricate a hidden state directly at the target layer.

---

# Stage 2 — MLA runtime dataflow qualification

The main purpose is to determine what the **actual runtime** caches and reads.

Do not assume compressed latent is the persistent cache merely because the architecture is MLA.

Instrument the earliest practical decoder layer with MLA and explicitly observe:

- input hidden;
- q projection;
- `kv_a` output / compressed latent;
- RoPE/nope components;
- `kv_b` expansion / reconstructed K/V;
- cache-before / cache-after objects and storage ranges;
- the operands consumed by attention-core kernels;
- output projection.

Build a typed runtime dataflow with alias/storage metadata, for example only if proven:

`HIDDEN -> KV_A_LATENT -> KV_B_EXPANDED -> CACHE_STORAGE / DERIVED_KV -> ATTENTION_CORE`

The actual labels must follow evidence.

## 2.1 MLA target selection hierarchy

Choose exactly one primary MLA formal target using this order:

1. **direct read from a proven persistent KV/cache storage object**, if the runtime actually exposes such a target and dynamic addresses can be losslessly joined;
2. otherwise a proven `kv_b` expansion read of the exact compressed latent produced by the model;
3. otherwise another V22 candidate only if it has a clean semantic replay and lossless object binding.

Do not call a transient compressed latent a KV-cache read unless it is actually persistent cache storage in this runtime.

Do not use attention launch order as object identity.

## 2.2 MLA replay/signature gate

For the selected target:

- freeze exact source tensors/state;
- isolate the semantic operator in a fresh process if necessary;
- prove output equivalence to in-context execution;
- prove source/destination alias relations;
- establish exact kernel function/grid/block signature;
- capture same-process `ADDRESS_CONTEXT` ranges for the semantic source/destination objects.

Only after this gate may the target become a formal MLA anchor.

---

# Stage 3 — natural-routing MoE qualification

Identify the first actual MoE layer for the canonical S2 execution from runtime/model config, not from a hard-coded assumption.

For the true first-decode token/state, record:

- router logits hash/shape;
- natural top-k expert IDs;
- router weights;
- any expert grouping/device/group-limited routing behavior actually used;
- shared expert behavior;
- token-to-expert dispatch representation;
- selected expert input/output tensors.

Routing must remain:

`NATURAL_ROUTING_REQUIRED`

Do not force an expert ID for convenience.

## 3.1 MoE target selection

Primary target should be a **naturally selected routed expert's actual expert MLP memory path**, preferably `down_proj` if it is implemented as a separable semantic operator with clean state binding.

Target selection requirements:

- the expert must be selected by the canonical natural router for the exact token/state;
- record exact expert ID and route weight;
- load/use that expert's real checkpoint weights;
- isolate the exact routed token tensor entering the expert;
- if grouped/fused expert kernels prevent lossless expert-specific attribution, do not pretend a single expert was isolated; instead choose a typed grouped-MoE target or fail closed.

Shared expert is secondary evidence, not a substitute for proving a routed expert path.

## 3.2 MoE replay/signature gate

For the selected MoE target:

- reproduce the expert operator using the exact naturally routed input and weights;
- prove in-context vs replay equivalence;
- record expert weight storage ranges and activation ranges;
- establish kernel function/grid/block signature;
- prove that the formal dynamic addresses can be attributed to the selected expert object without cross-process VA assumptions.

---

# Stage 4 — fresh static/address-path audit for each qualified target

For **each** of the two selected targets (MLA and MoE):

- dump/resolve the actual SM89 SASS/function identity;
- enumerate every direct GLOBAL MREF static instruction;
- independently audit LDGSTS / GLOBAL_TO_SHARED;
- audit other address-bearing special paths;
- distinguish load-source and store-destination semantics where callback behavior differs;
- do not assume generic MREF operand semantics if SASS shows address registers are required;
- freeze the complete address-bearing static set before formal capture.

V20's register-pair fix is precedent, not a universal mapping. Derive any DeepSeek register-pair source address from the actual target SASS.

---

# Stage 5 — complete formal capture: MLA

Capture every frozen static address-bearing shard for the exact MLA replay.

Requirements:

- fresh output root;
- explicitly clear inherited `C16_CTA_BEGIN` / `C16_CTA_END` and equivalent selectors;
- explicit function/static selector;
- sufficient capacity for full launch;
- same-process `ADDRESS_CONTEXT` per shard;
- terminal closure;
- drop = 0;
- overflow = 0;
- explicit executed vs `ZERO_EXECUTION_PROVEN` partition.

Before admission independently decode the formal traces and require:

- no CTA slicing evidence;
- target occurrence identity is unambiguous;
- dynamic source/destination addresses losslessly join the proven semantic object ranges required by the MLA evidence class;
- no hidden fallback to a different target kernel.

If object attribution fails, do not promote the capture as an MLA semantic anchor.

---

# Stage 6 — MLA Pipeline admission / ACK

Only after local closure:

- package/transfer to node164;
- verify hashes;
- submit exactly one formal admission;
- wait for positive verification/catalog/ACK.

Hard rule:

`FORMAL_ADMISSION_CONCURRENCY=1`

Do not start MoE formal admission while MLA admission is still in flight.

A rejected diagnostic capture must never be promoted into accepted raw/catalog.

---

# Stage 7 — complete formal capture: natural-routing MoE

After positive MLA ACK, capture the selected MoE target using the same formal discipline.

Requirements include:

- exact canonical natural-routing receipt attached to the run;
- selected expert/group identity explicitly bound;
- same-process expert-weight/activation context;
- full static/path closure;
- no forced routing;
- drop/overflow zero;
- full-scope/occurrence validation appropriate to the actual grouped or per-expert kernel.

Then admit exactly one MoE formal run and wait for positive ACK.

---

# Stage 8 — bounded profiling evidence

For each qualified MLA/MoE semantic target preserve:

- NSYS signature/context evidence;
- bounded NCU report when practical.

NCU rules:

- keep raw report/log;
- report numeric metrics only with explicit native values/units;
- preserve cache-control warnings;
- do not infer bytes from ambiguous units;
- do not make cache/TLB causality claims from uncontrolled-cache profiling.

---

# Stage 9 — producer interpretation

Create an evidence-bounded comparison of the two DeepSeek S2 anchors.

At minimum describe:

- semantic object/path;
- runtime dataflow role;
- static MREF/path structure;
- kernel signature;
- executed/zero partition;
- active-lane events;
- per-shard 4K/64K/2M page distributions;
- per-shard 128B line distributions;
- object-membership result;
- CTA/full-scope result;
- typed NCU status.

Do **not** construct:

- cross-target absolute-VA comparison;
- cross-replay VA union;
- cross-shard chronology;
- reuse distance from independent shards;
- broad "DeepSeek MLA cache behavior" claims from one selected target.

The two anchors are architecture-specific representative semantic paths, not unbiased estimators of the whole model.

---

# Stage 10 — next-step recommendation

V23 itself must **not** automatically run S3.

Produce a typed recommendation for V24/V25 based on actual S2 evidence:

- if MLA anchor is clearly context-size-sensitive and cleanly closed: recommend `PROMOTE_DEEPSEEK_MLA_ANCHOR_TO_S3_LONG_CONTEXT`;
- if MoE routing/footprint diversity is more informative: recommend a batch/structured routing dimension such as S4 rather than long-context by default;
- if one anchor remains semantically ambiguous, recommend one bounded repair for that anchor only;
- do not collect more DeepSeek operators merely for coverage density.

---

# Required V23 review pack

Create:

`docs/vm_tlb/review_packs/C16_DEEPSEEK_V2_LITE_S2_PRODUCER_109_V23/`

At minimum include:

- `MODEL_RUNTIME_AUTHORITY.json`
- `S2_INPUT_AUTHORITY.json`
- `CAPACITY_EXECUTION_RECEIPT.json`
- `EXACT_STATE_CHAIN.json`
- `MLA_RUNTIME_DATAFLOW.json`
- `MLA_TARGET_QUALIFICATION.json`
- `MLA_REPLAY_SIGNATURE.json`
- `MLA_STATIC_PATH_AUDIT.json`
- `MLA_FORMAL_SUMMARY.json`
- `MLA_ADMISSION_ACK.json`
- `MOE_ROUTING_RECEIPT.json`
- `MOE_TARGET_QUALIFICATION.json`
- `MOE_REPLAY_SIGNATURE.json`
- `MOE_STATIC_PATH_AUDIT.json`
- `MOE_FORMAL_SUMMARY.json`
- `MOE_ADMISSION_ACK.json`
- `NCU_TYPED_EVIDENCE.json`
- `S2_MLA_VS_MOE_INTERPRETATION.md`
- `NEXT_STEP_AUTHORIZATION.json`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Final PASS should be scoped, e.g.:

`C16_DEEPSEEK_V2_LITE_S2_PRODUCER_109_V23_PASS_WITH_MLA_AND_MOE_ANCHORS`

Only use that PASS form if both semantic anchors close and both formal runs receive positive ACK.

---

# Git closure

Suggested implementation branch:

`hrl/c16-deepseek-v2-lite-s2-producer-109-v23`

Use node109's existing Git transport/authentication.

Do not install `gh`.

After all Goal-owned artifacts are committed:

1. push the actual HEAD to the implementation branch;
2. verify canonical repository identity is `swayhrl/accel-sim-framework`;
3. verify nonempty canonical `git ls-remote` SHA;
4. require exact local HEAD == remote SHA;
5. working tree must be clean.

Do not ask the user to perform routine Git closure.

---

# Stop conditions

Fail closed only for a real blocker such as:

- canonical S2 input cannot be uniquely resolved;
- revision/config/asset mismatch;
- exact semantic layer-streaming state cannot be reproduced;
- runtime MLA dataflow contradicts the selected semantic label;
- natural MoE routing cannot be preserved;
- expert-specific attribution is impossible but the run is being labeled expert-specific;
- replay/signature mismatch;
- static/address-path closure failure;
- drop/overflow;
- full-scope/occurrence ambiguity that cannot be boundedly repaired;
- Pipeline rejection / negative ACK;
- terminal artifact corruption.

On a true blocker, preserve valid evidence, create a typed partial review pack, hash-close it, commit/push with canonical remote verification, and STOP.

Otherwise continue automatically through both S2 semantic anchors and STOP only after final Git closure.
