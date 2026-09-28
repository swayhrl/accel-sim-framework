# C16 Lane 7 Handoff — OLMoE Routing Provenance Multi-Round Capture V1

**Date:** 2026-09-28  
**Execution node:** `109`  
**Lane:** `Lane 7`  
**Role:** C16 native GPU producer / routing-only provenance capture  
**GPU:** RTX 4080 / SM89  
**GPU lock:** REQUIRED  
**GPU lock path:** `/data/c16/locks/c16_gpu_campaign.lock`  
**Goal:** `C16_OLMOE_ROUTING_PROVENANCE_MULTIROUND_109_V1`

This is a prospective, source-closed follow-up to the accepted Lane 6 post-hoc result. It is intentionally **multi-round in one campaign** to reduce model-load and coordination overhead.

---

## 0. Scientific starting point

Accepted Lane 6 V1:

- branch: `hrl/c16-moe-temporal-routing-screen-174new-v1`
- V1 commit: `0017527afba6861a4a0cfee95cce7b2a0397f284`
- V1 decision: `TEMPORAL_AUTHORITY_INSUFFICIENT_CROSS_MODEL`

Accepted post-hoc addendum:

- commit: `72fdd0f89aa0d4d4ae8b0d55daea492fbae2f293`
- primary label: `POSTHOC_PERIOD11_SIGNAL_CONFIRMED`
- qualifications:
  - `POSTHOC_PERIOD11_SIGNAL_ASSOCIATED_WITH_TOKEN_REPETITION`
  - `POSTHOC_PERIOD11_ORIGIN_UNRESOLVED`

OLMoE V34 Layer1, 32-step sequence:

- lag11 mean Jaccard: `0.928042`
- lag11 shuffle p95: `0.313967`
- 15/21 unordered exact-set repeats
- 5/21 additional 7-of-8 near repeats
- 19/21 same recorded next token
- router-input SHA equality 0/21
- router-logits SHA equality 0/21

This was found after inspecting V1, so it remains post-hoc. It is not a cache opportunity claim.

### New audit observation that changes this follow-up design

The exact V34 S2 source is itself strongly templated:

`docs/vm_tlb/assets/c16/prospective_common_input_v1/TEXT.txt`

starts with repeated records of the form:

`Local record 00000 has deterministic state value transition.`

The V34 frozen token IDs also show a strong repeated motif. Therefore **repeating only the same S2/TEXT input would be scientifically insufficient**: it could reproduce a content/template periodicity without telling us whether the routing periodicity is general or capture-induced.

This Goal therefore combines:
1. exact historical TEXT authority,
2. two already-frozen alternative synthetic input families from the same asset set,
3. one pinned non-template prose input,
4. no-hook reproducibility/control sessions,

under one model load / one GPU-lock campaign.

---

# 1. Immutable upstream authorities

## 1.1 OLMoE model

Model:

`allenai/OLMoE-1B-7B-0125-Instruct`

Revision:

`b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`

Node109 replica from V34:

`/data/c16/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`

Node164 remains sole durable model authority.

V34 producer:

`ab26365dc663268b0799818db6687ed466e8c925`

Accepted V40 descendant:

`85563ec6f55a0ad743d21483aa49c24fdb5cf3bf`

## 1.2 Historical TEXT input authority

Input asset commit:

`ca683527323e26e3415a805c797c53c5edea322c`

TEXT path:

`docs/vm_tlb/assets/c16/prospective_common_input_v1/TEXT.txt`

V34 recorded source SHA256:

`52761ce278c0e4819f153036e2b93e2b921d7963dda6a1d67a8192503612fa9c`

V34 frozen token count:

`2048`

V34 frozen token file SHA256:

`bba8ad1051b3e96039933d65ad8d77af3877f5603ae743b5e123d82c64de88e5`

V34 contract:

- `add_special_tokens=false`
- chat template NOT applied
- exact frozen IDs
- B1/T2048/D32 historical scenario

For `P_TEXT`, use the exact V34 frozen IDs as authority. Retokenizing the pinned TEXT with the current pinned model tokenizer must reproduce those IDs before GPU execution; otherwise stop.

## 1.3 Alternative already-pinned asset families

Same asset commit:

`ca683527323e26e3415a805c797c53c5edea322c`

Paths:

- `docs/vm_tlb/assets/c16/prospective_common_input_v1/CODE.txt`
- `docs/vm_tlb/assets/c16/prospective_common_input_v1/STRUCTURED.txt`

These are not historical V34 token authorities. For this prospective campaign:

- tokenize with the exact OLMoE revision tokenizer;
- `add_special_tokens=false`;
- no chat template;
- take the first exactly 2048 token IDs;
- freeze IDs and all source/tokenizer hashes **before GPU execution**;
- never retokenize during the locked run.

## 1.4 Non-template prose holdout

Pinned source:

commit:
`a306e1271c3e70c2ee322a3582979b6abd777a72`

path:
`docs/vm_tlb/scientific_logs/C16_MOE_EXPLORATION_LOG.md`

This is used only as a deterministic, non-record-template technical-prose input source. It is not a model-training or benchmark claim.

For `P_PROSE`:

- exact pinned file bytes;
- exact OLMoE tokenizer/revision;
- `add_special_tokens=false`;
- no chat template;
- first exactly 2048 token IDs;
- freeze before GPU execution.

If this source cannot supply 2048 tokens, STOP before GPU rather than silently concatenate or repeat it.

---

# 2. New branch / worktree

Coordination handoff branch:

`hrl/c16-olmoe-routing-provenance-multiround-109-v1-coordination`

The actual producer should create an independent branch from the accepted Lane7 base:

`0e88faa28c9066b48e394dce657d7a16e6332a32`

Suggested producer branch:

`hrl/c16-olmoe-routing-provenance-multiround-109-v1`

Suggested worktree:

`/home/huangrulin/workspace/worktrees/accel-sim-c16-olmoe-routing-provenance-multiround-109-v1`

Suggested local raw root:

`/data/c16/olmoe_routing_provenance_multiround_v1`

Never reuse V34/V40 raw/output directories.

---

# 3. Why multiple rounds are merged

The GPU campaign should load OLMoE **once** and execute all legal sessions serially under one outer GPU lock.

CPU-only work should be done before taking the lock:

- fetch/verify sources;
- tokenize and freeze all four input conditions;
- generate input manifests;
- prepare runner;
- compile no custom GPU code because none is needed.

Under the lock:

1. verify node109 GPU/platform identity;
2. load model once;
3. execute all sessions below;
4. flush capture files;
5. unload/release GPU;
6. release lock.

After lock release:

- compute hashes;
- do lag/shuffle analysis;
- build review pack;
- transfer/admit to node164.

This is one campaign, not six independent model setup cycles.

---

# 4. Prospective generation semantics

Historical V34 generation-loop semantics are incomplete. Do **not** pretend to reconstruct them by assumption.

This campaign defines a new explicit prospective decode contract.

## 4.1 Common generation policy

For every session:

- batch size = 1;
- prompt length = exactly 2048 frozen token IDs;
- BF16 model execution;
- natural routing only;
- no forced experts;
- no model/weight modification;
- no sampling;
- greedy next token = exact argmax of current final-token logits;
- `use_cache=true`;
- maximum decode steps = 64;
- natural EOS/stopping is honored and recorded;
- no artificial EOS suppression;
- no temperature/top-p/top-k sampling;
- no beam search;
- no chat template;
- no retokenization after input freeze.

Record all generation kwargs and runtime versions explicitly.

## 4.2 Prefer an explicit decode loop

Prefer an explicit, auditable prefill + cached decode loop rather than an opaque `generate()` call.

Required semantic record:

- prompt prefill is separate from decode;
- decode step numbering is 1-based;
- each decode record stores:
  - `input_token_id`: token actually fed to the cached decode call;
  - `output_token_id`: greedy argmax selected from that decode call;
  - cache class;
  - cache sequence length before/after;
  - whether cache object identity is continuous when meaningful;
  - EOS/stopping state.

If the model/runtime requires `prepare_inputs_for_generation` or another standard helper, use it only if the exact runner source and kwargs are committed and the above semantic fields remain auditable.

Do not use historical V34 field name `next_token_id` ambiguously in the new raw schema. Use explicit `input_token_id` and `output_token_id`.

---

# 5. Session matrix

All sessions use the same loaded model.

| Session | Prompt | Router capture | Purpose |
|---|---|---|---|
| `T0_NOHOOK_A` | exact P_TEXT | OFF | deterministic no-hook control A |
| `T1_NOHOOK_B` | exact P_TEXT | OFF | deterministic no-hook control B |
| `T2_TEXT_ALLLAYER` | exact P_TEXT | ON, all MoE layers | historical-text prospective reproduction + all-layer periodicity |
| `C1_CODE_ALLLAYER` | P_CODE | ON, all MoE layers | input-family control |
| `S1_STRUCTURED_ALLLAYER` | P_STRUCTURED | ON, all MoE layers | input-family control |
| `P1_PROSE_ALLLAYER` | P_PROSE | ON, all MoE layers | non-template prose holdout |

Every session starts from:

- a fresh prompt prefill;
- a fresh KV-cache/session state;
- the same loaded model weights;
- no state carried from the previous session except immutable model residency.

Do not concatenate sessions into one generation.

## 5.1 Control interpretation

After T0/T1/T2:

- if T0 output-token sequence == T1 == T2 for all common executed steps:
  `PROSPECTIVE_OUTPUT_REPRODUCIBILITY_AND_HOOK_NEUTRALITY_PASS`

- if T0 != T1:
  `PROSPECTIVE_GREEDY_REPRODUCIBILITY_NOT_EXACT`
  Continue the remaining sessions, but exact cross-session sequence claims are forbidden.

- if T0 == T1 but T2 differs:
  `ROUTER_CAPTURE_OUTPUT_NEUTRALITY_FAIL`
  Stop before C1/S1/P1. Publish the negative receipt; do not redesign hooks inside the same scientific Goal.

---

# 6. All-layer routing capture contract

For each routed MoE layer and each decode step in capture-enabled sessions, record:

- session ID;
- decode step;
- layer ID / stable module path;
- `input_token_id`;
- `output_token_id`;
- ordered top-k expert IDs;
- corresponding route weights;
- router-input dtype/shape/SHA256;
- router-logits dtype/shape/SHA256;
- configured expert count;
- configured experts-per-token;
- norm-topk setting if present;
- cache sequence length before/after.

Expert identity is always:

`(layer_id, expert_id)`

Do not mix identical numeric expert IDs across layers.

Top-k rank is routing rank, not GPU kernel execution order.

## 6.1 Passive capture only

Hooks/observers must not:

- change tensor values;
- replace outputs;
- force experts;
- change dtype;
- call a different model path.

Avoid retaining full GPU tensors across steps. Copy only the minimal values needed for the record and release promptly to avoid artificial memory pressure.

No timing result is produced by this campaign, so hook overhead itself is not a performance variable.

---

# 7. Historical V34 comparison

For `T2_TEXT_ALLLAYER`, compare **Layer1 first 32 steps** against:

`ab26365dc663268b0799818db6687ed466e8c925:
docs/vm_tlb/review_packs/C16_OLMOE_S2_PRODUCER_109_V34/NATURAL_TOP8_ROUTING.json`

Report separately:

- ordered top-k equality count;
- unordered top-k set equality count;
- Jaccard per step;
- new `output_token_id` vs old `next_token_id` equality;
- new `input_token_id` vs old `next_token_id` equality;
- router-input SHA equality where hash serialization is demonstrably identical;
- router-logits SHA equality where serialization is demonstrably identical.

Allowed historical labels:

- `HISTORICAL_V34_SEQUENCE_REPRODUCED_UNDER_EXPLICIT_RUNNER`
- `HISTORICAL_V34_SEQUENCE_PARTIALLY_REPRODUCED`
- `HISTORICAL_V34_RUNNER_NOT_RECONSTRUCTED`

Do not infer exact historical runner semantics merely because one field aligns.

---

# 8. Prompt periodicity audit

Before interpreting routing, quantify the inputs themselves.

For each 2048-token prompt:

- token equality rate for lags 1..32 over the full frozen prompt;
- token equality rate for lags 1..32 over the last 256 prompt tokens;
- exact repeated n-gram diagnostics for n=2,4,8 where cheap;
- strongest prompt-token lag(s).

This is important because P_TEXT/CODE/STRUCTURED are intentionally templated data sources.

Do not call any of these natural-language population statistics.

---

# 9. Decode/routing periodicity analysis

CPU-only after GPU release.

For every capture-enabled session and every MoE layer with enough steps:

## 9.1 Complete lag spectrum

For lags 1..32:

- pair count;
- mean expert-set overlap;
- mean Jaccard;
- mean retention;
- exact unordered-set repeat count;
- ordered-topk repeat count.

## 9.2 Per-lag marginal-preserving shuffle control

For each session/layer/lag:

- seed = `20260928`;
- 1000 permutations;
- shuffle whole decode-step top-k sets;
- preserve each step's set, marginal expert frequencies and within-step co-selection;
- destroy only time ordering.

Report actual and shuffle:

- p05;
- median;
- p95.

These are descriptive intervals, not preregistered p-values.

## 9.3 Token sequence periodicity

For both explicit decode token streams:

- `input_token_id` lag equality 1..32;
- `output_token_id` lag equality 1..32.

Report association between routing-set similarity and:
- same input token;
- same output token;

separately.

Input-token association is now scientifically interpretable as an input-side relation; output-token association remains downstream/descriptive.

## 9.4 Cross-layer concordance

For each capture session:

- count layers whose strongest above-shuffle-p95 routing lag is 11;
- count layers with any above-p95 lag;
- list the dominant lag by layer;
- do not average expert IDs across layers.

This asks whether any periodicity is layer-local or model-wide.

## 9.5 Cross-input comparison

Predeclare these comparisons:

- P_TEXT vs P_CODE
- P_TEXT vs P_STRUCTURED
- P_TEXT vs P_PROSE
- CODE vs STRUCTURED vs PROSE descriptively

Do not rank models; this is one model across four prompt families.

---

# 10. Decision logic

This prospective campaign is primarily about **origin**, not cache performance.

Allowed top-level outcomes include:

### A. `PERIOD11_REPRODUCED_TEXT_ONLY_CONTENT_ASSOCIATED`

Use when:
- P_TEXT reproduces a strong lag11 structure;
- CODE/STRUCTURED/PROSE do not show a comparable lag11;
- prompt/decode token structure provides a coherent content association.

This supports input/content-specific routing periodicity, not a general MoE periodicity.

### B. `PERIODICITY_TRACKS_INPUT_FAMILY_WITH_DIFFERENT_LAGS`

Use when different prompt families show different dominant routing lags that align descriptively with their token structure.

### C. `PERIOD11_REPRODUCED_ACROSS_INPUT_FAMILIES`

Use only if lag11 independently appears across multiple predeclared input families/layers.

This would justify a later independent consumer and possibly a broader temporal-locality question, but still not a cache mechanism.

### D. `HISTORICAL_PERIOD11_NOT_REPRODUCED_PROSPECTIVELY`

Use when the explicit new P_TEXT runner does not reproduce the old sequence/periodicity.

The old post-hoc V34 result remains valid for its accepted artifact; only its generality is reduced.

### E. `ROUTER_CAPTURE_OUTPUT_NEUTRALITY_FAIL`

Stop scientific capture expansion.

### F. `PROSPECTIVE_ROUTING_CAPTURE_PASS_ORIGIN_STILL_UNRESOLVED`

Use when data are valid but content/capture origin still cannot be separated.

No post-result new thresholds may be invented.

---

# 11. What this Goal must NOT do

Do not:

- run NVBit;
- run NCU;
- run NSYS unless a pure engineering launch/debug need is unavoidable and not used as science;
- capture SASS;
- run cache simulation;
- run Accel-Sim;
- modify Lane4 or read Lane4 partial outputs;
- force routing;
- modify model weights;
- change expert count/top-k;
- compare performance timings;
- claim full-model speedup;
- design a period-11 cache;
- add more prompt families after seeing results;
- add sampling modes after seeing results;
- change decode length after seeing results except natural EOS shortening;
- use CODE/STRUCTURED/PROSE as if they were historical V34 authorities.

---

# 12. GPU lock / efficiency policy

Every CUDA operation must hold:

`/data/c16/locks/c16_gpu_campaign.lock`

Use one outer lock for the full six-session campaign.

Never:
- steal/delete/bypass lock;
- kill another GPU process;
- alter clocks/power/persistence/driver.

If lock is occupied:
- finish CPU-only prep;
- wait for legal acquisition;
- do not run partial sessions outside the lock.

Record:

`GPU_LOCK_RECEIPT.json`

with:
- acquisition/release;
- start/end UTC;
- GPU model/UUID;
- driver;
- CUDA/runtime;
- pre/post nvidia-smi;
- one-model-load / six-session execution confirmation.

---

# 13. Durable raw and node164

Suggested campaign ID:

`C16R_olmoe-routing-provenance-multiround-v1_<UTC>_<nonce>`

Local raw:

`/data/c16/olmoe_routing_provenance_multiround_v1/raw/<RUN_ID>`

Durable authority target:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/<RUN_ID>`

Use existing C16 transfer/admission conventions where available.

Required durable closure:

- immutable manifest;
- per-file size/SHA256;
- source/input/tokenizer/runtime receipt;
- session matrix receipt;
- positive node164 ACK/catalog binding if the existing pipeline supports this raw class.

Do not overwrite V34/V40.

---

# 14. Required review pack

Create:

`docs/vm_tlb/review_packs/C16_OLMOE_ROUTING_PROVENANCE_MULTIROUND_109_V1/`

Keep the pack compact.

At minimum:

- `README.md`
- `SOURCE_AUTHORITY.json`
- `INPUT_FREEZE_INDEX.tsv`
- `GENERATION_CONTRACT.json`
- `GPU_LOCK_RECEIPT.json`
- `SESSION_RECEIPT.tsv`
- `OUTPUT_TOKEN_SEQUENCES.tsv`
- `ROUTING_RECORD_INDEX.tsv`
- `CONTROL_REPRODUCIBILITY.json`
- `V34_LAYER1_COMPARISON.tsv`
- `PROMPT_PERIODICITY.tsv`
- `ROUTING_LAG_SPECTRUM.tsv`
- `ROUTING_LAG_SHUFFLE.tsv`
- `TOKEN_ROUTING_ASSOCIATION.json`
- `CROSS_LAYER_PERIODICITY.tsv`
- `CROSS_INPUT_INTERPRETATION.md`
- `FINAL_DECISION.json`
- `NEXT_174_CONSUMER_CONTRACT.md`
- `RAW_LOG_INDEX.tsv`
- `SHA256SUMS`

The exact runner source must be committed under:

`util/vm_tlb/c16/`

Do not omit the runner as happened in V34.

---

# 15. Producer self-check vs independent consumer

Lane7 may compute the complete producer-side descriptive analysis after releasing the GPU lock.

However final scientific acceptance should later be independently recomputed on **174-new** from the durable raw.

Therefore create `NEXT_174_CONSUMER_CONTRACT.md` that binds:

- exact RUN_ID;
- manifest SHA;
- producer commit;
- four input identities;
- six session identities;
- expected row counts;
- lag/shuffle definitions;
- no use of producer summary as calculation authority.

Do not automatically start the 174 consumer from Lane7.

---

# 16. Solve-and-continue / STOP policy

Ordinary engineering issues may be solved automatically if they do not alter:

- model/revision;
- the four predeclared prompt sources;
- 2048-token freeze rule;
- six-session matrix;
- greedy/use-cache policy;
- 64-step cap;
- all-layer routing record schema;
- lag range 1..32;
- shuffle seed/count;
- GPU lock;
- claim boundaries.

STOP for review if:

1. P_TEXT retokenization does not reproduce V34 frozen IDs;
2. model/runtime authority is unavailable or materially changed;
3. T0==T1 but T2 output sequence differs (hook neutrality failure);
4. the required all-layer routing values cannot be observed without modifying model semantics;
5. GPU lock cannot be safely acquired;
6. model no longer fits legally on RTX4080 under the accepted BF16 path;
7. any proposed workaround changes routing/model precision/weights;
8. node164 durable identity cannot be closed after a scientifically valid run.

If T0 != T1, do not stop automatically; continue but record non-exact prospective reproducibility and restrict claims.

---

# 17. Publication

After the full merged campaign:

`validate -> git diff --check -> SHA256SUMS -> commit -> push -> fetch-back verify exact commit/tree -> clean -> report -> STOP`

Report:

- producer branch / HEAD;
- RUN_ID;
- GPU lock receipt;
- six session completion;
- hook-neutrality/reproducibility state;
- historical V34 comparison;
- dominant periodicity per input family;
- final bounded decision;
- node164 durable/ACK state.

Do not automatically run another GPU experiment.

The Lane7 window remains the persistent node109 / RTX4080 GPU lane after STOP.
