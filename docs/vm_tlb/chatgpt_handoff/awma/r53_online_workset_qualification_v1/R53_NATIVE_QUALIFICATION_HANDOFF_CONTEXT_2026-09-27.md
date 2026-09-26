# AWMA R53 Native Qualification Handoff Context — 2026-09-27

## 0. Purpose

This handoff starts the **first native qualification** for R53 after Round06 literature/source design.

The only active scientific question is:

`R53_N1_ONLINE_LEGAL_WORKSET_REALIZATION`

> With the per-request decoder and KV refresh/reuse rules held fixed, does the dynamically changing set of legally required work still leave a material online organization cost after a credible software implementation using shared forward execution, active-request packing/compaction, bounded batch buckets, reusable buffers, and CUDA-graph/compile capabilities where legal?

This is **not yet a hardware mechanism study**.

The next execution is node109 only. Node174/Accel-Sim remains idle unless a later ChatGPT review explicitly authorizes architecture modeling.

---

# 1. Frozen project state

## 1.1 Previous accepted execution

Accepted R51 V2 execution:

- branch: `hrl/awma-r51-semantic-contract-requalification-v2`
- commit: `db2000f7222030282f788bd009243ab1a43ed867`
- final: `R51_R52_LIFECYCLE_QUALIFICATION_NO_RESIDUAL_V2`

Interpretation boundary:
- R51 is frozen **for the tested Qwen lm_head / Flash-SDPA handoff scope**.
- Do not generalize that result to every persistent kernel or scheduling problem.
- R52 remains dormant because no accepted real online invalidation authority exists.

Do not rerun R51/R52 in the R53 stage.

## 1.2 Accepted R53 design authority

Literature/source branch:

- branch: `hrl/awma-chatgpt-literature-notes-v1`
- commit: `23e9db4ea6fadafc43430a7b6b878b86b73f19e8`
- file:
  `docs/vm_tlb/literature_notes/awma/rounds/2026-09-27_ROUND_06_R53_RESEARCH_AND_DESIGN.md`

Round06 status:
`R53_DESIGN_READY_NATIVE_NOT_AUTHORIZED`

This handoff authorizes the bounded native qualification described below; it does **not** authorize a hardware mechanism.

---

# 2. What Round06 already established

## 2.1 Do not equate mask sparsity with removable transformer work

Keep separate:

- `U`: currently uncommitted positions;
- `Q_l`: query rows that are legally required at layer `l`;
- KV read range;
- KV refresh/update/commit range;
- `O`: logits rows with a legal consumer;
- `A`: active requests.

They are not interchangeable.

A position whose token ID is already fixed may still need deep-layer recomputation in bidirectional models. In a block-causal diffusion model, completed prefix blocks have stronger reuse semantics, but current-block cache policy still matters.

No result may infer "removable work" merely from the number of mask tokens.

## 2.2 Closest software/system work already covers broad ideas

The stage must treat these as strong prior capabilities, not novelty targets:

- Fast-dLLM / Fast-dLLM v2: parallel token commitment, cache reuse, block-causal diffusion.
- dInfer: decoder/cache separation, compilation, CUDA graphs, loop optimization, batching.
- dLLM-Serve: query-token packing, mixed refresh/reuse, logits chunking, sparse physical KV.
- BlockServe: block-cycle request exit/admission and mixed-state batching.
- Sangam: coordinated repeated prefill / denoising serving and graph-oriented execution.
- BiCache: cross-request/request-local KV reuse policies.
- FluxServe: claims varlen block-decode, CUDA graphs, and low-overhead scheduling.

Therefore this stage must not claim novelty from:
- "dynamic batch sizes";
- "finished requests leave the batch";
- "pack active tokens";
- "use CUDA graphs";
- "cache converged states";
- "schedule refresh and decode together".

The only question is whether a **specific residual capability/cost** remains after a credible version of those relevant capabilities is represented.

---

# 3. Source-code facts that constrain the experiment

Pinned upstream source:

- repo: `NVlabs/Fast-dLLM`
- commit: `a9b81e4caa240c8cad4f7dc1889ff4852a0fca5b`
- file: `v2/generation_functions.py`
- blob observed in Round06:
  `76fc22d1d4eb2d9f959fc5d3148cd9067651d5b1`

Important observed behavior in `batch_sample`:

1. completed requests are already removed at block boundaries;
2. each layer's KV cache is sliced when requests leave;
3. the sub-block loop uses a **batch-wide** mask reduction to decide whether the cohort continues;
4. the block-cache path uses a **batch-wide `any()` condition** to choose full-block refresh versus sub-block reuse.

Scientific implication:

Changing cohort membership can alter cache refresh behavior. A faster execution that silently changes the refresh/reuse sequence is an **algorithm/policy change**, not a pure workset-mapping optimization.

R53 must preserve the reference cohort-derived discrete refresh decisions when comparing A0/A1.

---

# 4. Single model authority for this stage

Only one new model may be downloaded:

- Hugging Face repo:
  `Efficient-Large-Model/Fast_dLLM_v2_1.5B`
- required revision:
  `25093b6f63300adfd57f72145083c8a528fe4f16`

Round06 inspected this revision and recorded:
- 28 layers;
- hidden size 1536;
- 12 query heads;
- 2 KV heads;
- BF16 configuration;
- block size 32 in the intended deployment;
- repository weight payload approximately 3.09 GB.

This model represents **block-causal diffusion only**.
Do not generalize results to fully bidirectional LLaDA/Dream-style refresh behavior.

No second diffusion model may be downloaded in this Goal.

No CPU/disk offload may be introduced to make the benchmark fit. If the primary concurrency does not fit, use only the preregistered resource fallback below.

---

# 5. Environment isolation

R53 has different dependencies from the accepted C16/Qwen environment.

Requirements:

- do not mutate the accepted C16 environment;
- create a dedicated isolated Python environment under the R53 stage directory or another clearly isolated path;
- pin every installed package/version and hash the lock/receipt;
- pin the upstream Fast-dLLM source commit;
- pin the model revision;
- no driver/CUDA-system modification;
- no system-wide pip install;
- no replacement of accepted C16 PyTorch packages.

Ordinary package incompatibilities are solve-and-continue, with at most two surgical dependency fixes before declaring the runtime not qualified.

A runtime failure is not a scientific negative.

---

# 6. Dataset/input authority

Use only:

## GSM8K

- Hugging Face dataset:
  `openai/gsm8k`
- config: `main`
- split: `test`
- input field: `question`

## HumanEval

- Hugging Face dataset:
  `openai/openai_humaneval`
- split: `test`
- stable ID field: `task_id`
- model input field: `prompt`

The exact dataset snapshot/revision must be resolved and frozen **before any model timing**.

Do not execute generated HumanEval code. This stage studies inference behavior, not code correctness.

## 6.1 Deterministic request selection

Selection must be independent of runtime, output quality, sequence length, or observed dynamicity.

For each dataset:

1. materialize the frozen test split;
2. define canonical sample ID:
   - GSM8K: `gsm8k/main/test/<zero-based-row-index>`
   - HumanEval: the provided `task_id`;
3. define selection key:
   `SHA256(canonical_id + "\n" + exact_raw_prompt)`;
4. sort ascending by the hex digest;
5. first 4 samples = `DISCOVERY`;
6. next 4 samples = `HOLDOUT`.

Freeze:
- dataset repo/revision;
- row/task IDs;
- raw text hashes;
- tokenizer input IDs/hashes;
- rendered prompt/chat-template hashes.

No replacement is allowed because a selected sample is too slow, too uniform, too dynamic, or produces an inconvenient result.

A malformed/unloadable dataset row is an engineering issue; deterministic next-row substitution is allowed only if the row is structurally unusable **before model execution**, and must be recorded.

---

# 7. Frozen model-generation policy

Primary policy:

- dtype: BF16;
- `block_size=32`;
- `small_block_size=8`;
- `threshold=0.9`;
- `temperature=0.0`;
- `top_p=0.95`;
- `use_block_cache=true`;
- generation ceiling: 512 new tokens;
- normal stop/EOS semantics remain enabled.

These values are a fixed experiment point, not a parameter sweep.

The tokenizer/model's pinned official prompt formatting is used when required by the model code. Any added task instruction must be frozen before timing and identical between A0/A1.

No quality-scoring-driven retry is allowed.

---

# 8. Resource admission and preregistered fallback

Primary concurrency:
`B=4`

One canary bundle consists of the 4 discovery prompts for one dataset.

Admission sequence:

1. B1 short canary;
2. B4 bounded canary with the frozen policy;
3. record peak allocated/reserved memory and OOM state.

If B4 fails because of memory before formal timing:
- fallback concurrency = `B=2`;
- this fallback is preregistered, not a performance choice;
- for each four-request discovery/holdout set, use deterministic pairs `[0,1]` and `[2,3]`;
- aggregate both pairs as one logical dataset bundle for total-work metrics.

If B2 also fails:
`R53_INPUT_OR_RUNTIME_NOT_QUALIFIED`

Do not:
- offload;
- reduce model precision;
- shorten the selected prompt;
- lower generation ceiling solely to fit;
- download a smaller second model.

Canary output is not a formal timing point.

---

# 9. Semantic contract

The experiment compares execution organization, not a different diffusion algorithm.

Define:
`R53_FIXED_DECODER_CACHE_TRAJECTORY_V1`

For every request, A1 must match A0 on all discrete algorithm-visible state transitions:

- logical block index;
- sub-block index;
- committed position set at each logical step;
- committed token IDs;
- confidence/threshold commit decision;
- fallback/max-prob forced-commit decision;
- stop/EOS transition;
- request-finished transition;
- cohort-derived full-refresh vs reuse decision;
- cache epoch/update event;
- next-block seed token/transition where applicable.

Final generated text equality alone is insufficient.

Internal floating-point logits do not need to be bitwise equal if all frozen discrete decisions and trajectory states remain identical.

If A1 changes the discrete trajectory:
`R53_ALGORITHM_CHANGE_NOT_MAPPING_GAIN`
unless the difference is clearly an engineering bug that can be surgically repaired within the bounded attempt limit.

Do not relax the semantic contract after observing performance.

---

# 10. Untimed legal-work ledger

Before formal timing, run an **untimed** instrumented reference/qualification pass.

Required logical ledger columns:

- dataset/domain;
- request_id;
- logical_step;
- block_idx;
- subblock_idx;
- cohort_id;
- active_request_count;
- request_active;
- request_finished;
- mask_count_current_request;
- cohort_mask_count;
- cohort_full_refresh_decision;
- request_has_current_subblock_work;
- input_token_rows_executed;
- logits_rows_materialized;
- cache_epoch;
- cache_action;
- commit_positions;
- commit_token_ids;
- graph_bucket_if_any;
- notes/UNKNOWN boundary.

Do not add per-layer CPU synchronization to formal timing.

## 10.1 Legal-work interpretation

A row/operation may be labeled `LEGALLY_OMITTABLE_IN_SCOPE` only if:

- A1 actually omits it;
- the A0/A1 semantic trajectory remains identical;
- all cache/consumer dependencies remain satisfied.

The ledger must distinguish at least:

- `REQUIRED_ACTIVE_WORK`
- `COHORT_POLICY_REQUIRED_WORK`
- `PASSIVE_EXECUTION_CANDIDATE`
- `LEGALLY_OMITTABLE_IN_SCOPE`
- `UNKNOWN`

Do not classify work as removable from mask count alone.

Useful work proxies:

- transformer input token-rows executed;
- attention query rows;
- attention logical score elements when key length is known;
- logits rows materialized;
- forward-call count;
- active-request count over time.

These are explanatory proxies, not direct speedup predictions.

---

# 11. Execution arms

## A0 — PINNED_OFFICIAL_BATCHED_REFERENCE

Use the pinned upstream Fast-dLLM v2 algorithm and model code with the frozen policy.

Preserve:
- official block/sub-block loop;
- official cache policy;
- existing block-boundary finished-request removal;
- official cohort decisions.

A0 is the semantic authority, not necessarily the strongest performance baseline.

## A1 — STRONG_SEMANTIC_WORKSET_SOFTWARE

A1 must preserve the A0 discrete trajectory while applying only execution-organization changes.

Required capabilities, in order:

### A1.1 Active-request/sub-block packing

At each legal forward boundary:

- compute the **A0 cohort decision first**;
- preserve A0's full-refresh/reuse decision;
- pack only request rows whose outputs/cache updates are actually required under that already-frozen decision;
- requests omitted from a forward keep their prior state/cache exactly;
- scatter resulting state back to canonical request order.

Changing cohort membership may not change the A0 policy decision.

### A1.2 Finished-request compaction

A request already declared finished by A0 semantics may be physically removed at the earliest state-safe boundary where:
- it has no future consumer;
- no shared batch tensor/cache entry still references it.

Do not change the logical finish time.

### A1.3 Reusable buffers / metadata

Preallocate and reuse:
- gather indices;
- scatter indices;
- packed input buffers;
- output scatter buffers;
- small metadata tensors,

where shapes permit.

Avoid per-step allocator churn when an existing reusable buffer is sufficient.

### A1.4 Bounded buckets / graph or compile optimization

Permitted batch buckets only:
`1, 2, 4`

No other bucket count.

Attempt at most two performance-hardening paths:
1. graph capture for stable legal bucket segments, or
2. compile/fused control path when graph capture is structurally impossible.

A1 does not need to reproduce BlockServe/Sangam/dLLM-Serve wholesale.
It does need to represent the directly relevant strong-software ideas fairly.

If no credible A1 can be built without changing semantics:
`R53_INPUT_OR_BASELINE_NOT_QUALIFIED`

Do not interpret failed engineering as hardware opportunity.

---

# 12. Formal discovery matrix

Primary concurrency = admitted B4 or preregistered B2 fallback.

Discovery domains:
- GSM8K DISCOVERY bundle;
- HumanEval DISCOVERY bundle.

Formal arms:
- A0;
- A1.

Total main discovery conditions:
**4** logical points.

Each formal condition:
- 1 canary;
- 2 warmups;
- 7 measured full-generation repetitions;
- paired/interleaved A0/A1 order to reduce drift;
- save each repetition individually.

GPU lock:
`/data/c16/locks/c16_gpu_campaign.lock`

No concurrent GPU profiler.

Timing:
- primary: full logical-bundle wall-clock from first GPU-relevant generation submission to all requests complete;
- also record per-request completion times;
- record CUDA-event/GPU timing where valid;
- one NSYS identity/timeline canary per A0/A1 discovery condition, not every repetition.

Do not use profiler replay timing as the primary performance number.

---

# 13. Metrics

For each condition record:

## 13.1 Correctness/trajectory

- semantic-trajectory PASS/FAIL;
- final token IDs and hashes;
- generated-text hashes;
- stop reason/truncation;
- discrete decision ledger hash.

## 13.2 End-to-end

- full bundle wall-clock;
- generated valid tokens;
- valid tokens/s;
- per-request completion time;
- truncated request count;
- peak allocated/reserved memory.

## 13.3 GPU/runtime

From one NSYS canary:
- GPU union busy time;
- kernel launch count;
- relevant forward/kernel count;
- GPU idle gaps;
- host/API waiting;
- graph launch count;
- dominant kernel families.

## 13.4 Workset

- transformer token-row executions;
- attention query-row executions;
- attention score-element proxy where valid;
- logits rows materialized;
- packed/scattered row count;
- packing/scatter bytes;
- metadata preparation time;
- gather/scatter GPU time;
- host-side organization time.

---

# 14. Discovery decisions

Use the same 5% end-to-end scale as the **investment screen**, not as a proof of equality.

Also require the observed effect to exceed a 3x run-to-run noise/jitter envelope before calling it stable.

## 14.1 `R53_NO_OBSERVED_EXCESS_WORK_IN_SCOPE`

Use when:
- A1 cannot legally omit a meaningful amount of A0 execution in either discovery domain; or
- the dynamic workset exists only nominally and produces <5% change in all meaningful work proxies.

No diagnostic D or holdout.

## 14.2 `R53_SOFTWARE_BASELINE_SUFFICIENT_IN_SCOPE`

Use when:
- A1 preserves semantics;
- A1 demonstrates legal work reduction;
- A1 improves full-bundle end-to-end cost by >=5% with stable effect;
- remaining online organization overhead is not itself >=5% of end-to-end cost.

This is a software-positive / architecture-negative result.

## 14.3 `R53_HOST_RUNTIME_COST_NOT_ARCH_LOCALIZED`

Use when:
- a legal work reduction exists;
- A1 cannot realize it efficiently;
- evidence localizes the loss primarily to Python/host control/API overhead;
- graph/compile hardening is unavailable or insufficient for engineering reasons.

Do not send this directly to 174.

## 14.4 `R53_ALGORITHM_CHANGE_NOT_MAPPING_GAIN`

Use when the apparent gain depends on:
- altered refresh/reuse decisions;
- altered committed positions/tokens;
- altered fallback/threshold decisions;
- altered stop trajectory.

## 14.5 Conditional `R53_RESIDUAL_DIAGNOSTIC_REQUIRED`

Use only when:
- semantics match;
- legal work reduction is real;
- A1 is a credible strong software baseline;
- end-to-end result suggests >=5% unresolved organization cost or severe inability to realize the legal reduction;
- the cost is not already explained by pure host control.

Only this state triggers D.

---

# 15. Diagnostic D — one condition maximum

Purpose:
separate unavoidable model compute from **online current-step organization**.

D is not deployable and is not an upper bound.

Select the diagnostic discovery domain by frozen rule:
- choose the domain with the larger absolute A0↔A1 unresolved cost after discovery;
- ties go to GSM8K.

D may move **only the current logical step's** already-derivable metadata preparation outside the timed region:
- packing indices;
- bucket selection;
- scatter map;
- buffer-offset map.

It may not:
- use future commit/acceptance results;
- use future cache state;
- precompute model outputs;
- alter refresh policy.

Compare D with the same A1 execution kernels.

If D gains <5% full-bundle equivalent cost:
online metadata/workset realization is not material enough for this stage.

If D gains >=5% stably:
the residual is localized enough to justify holdout.

---

# 16. Holdout

Holdout is conditional.

A holdout is run only if:
- discovery reaches a stable residual requiring validation; or
- D identifies >=5% online organization cost.

Choose holdout domain:
- use the same domain that triggered the residual;
- use that domain's next 4 preregistered HOLDOUT prompts;
- use admitted concurrency/fallback identically.

Run only:
- A0;
- strongest qualified A1;
- D only if D was the reason the candidate survived discovery and is necessary for causal confirmation.

Do not tune A1 on holdout results.

---

# 17. Architecture-review gate

The final state may be `R53_RESIDUAL_READY_FOR_ARCH_REVIEW_V1` only if all hold:

1. real Fast-dLLM v2 model and frozen requests;
2. exact discrete decode/cache trajectory equivalence;
3. legal work reduction demonstrated, not inferred from mask count;
4. credible A1 with packing/buffer reuse and legal graph/compile hardening;
5. stable >=5% end-to-end residual or diagnostic current-step organization cost;
6. effect survives the preregistered holdout;
7. not explained mainly by Python/host runtime;
8. closest-work capability comparison identifies a concrete missing capability rather than the generic idea of dynamic batching.

This state authorizes only ChatGPT architecture review.
It does not authorize simulator modification.

---

# 18. Nodes and storage

## node109

Only node used for this stage:
- model download/staging;
- isolated runtime environment;
- native inference;
- semantic ledger;
- NSYS timing.

All formal GPU runs use the existing lock.

## node164

Durable authority for:
- model/dataset receipts if needed;
- large raw logs/traces;
- runtime package lock/hash;
- generated logical ledgers;
- NSYS artifacts;
- raw timing results.

Suggested durable root:
`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r53_online_workset_qualification_20260927/`

## node174

Do not use.

---

# 19. Publication discipline

Review pack target:

`docs/vm_tlb/review_packs/AWMA_R53_ONLINE_WORKSET_QUALIFICATION_V1/`

Required minimum:

- `README.md`
- `R53_SOURCE_AND_CLOSEST_WORK_AUDIT.md`
- `MODEL_ADMISSION_RECEIPT.json`
- `RUNTIME_ENVIRONMENT_RECEIPT.json`
- `DATASET_SNAPSHOT_RECEIPT.json`
- `REQUEST_SELECTION.tsv`
- `PREREGISTRATION.json`
- `SEMANTIC_TRAJECTORY_SCHEMA.md`
- `LEGAL_WORK_LEDGER.tsv.gz`
- `LEGAL_WORK_SUMMARY.tsv`
- `A0_A1_SEMANTIC_EQUIVALENCE.tsv`
- `DISCOVERY_TIMING_RESULTS.tsv`
- `DISCOVERY_WORKSET_RESULTS.tsv`
- `NSYS_DISCOVERY_SUMMARY.tsv`
- optional `DIAGNOSTIC_D_RESULTS.tsv`
- optional `HOLDOUT_RESULTS.tsv`
- `R53_DECISION.md`
- `FINAL_DECISION.md`
- `RAW_DATA_INDEX.tsv`
- `SHA256SUMS`

Large raw files do not enter Git.

Closure:
`science/engineering -> node164 -> review pack -> hashes -> commit -> push -> fetch-back -> exact SHA/tree verification -> clean worktree -> STOP`

No auto merge.

---

# 20. Allowed final states

Exactly one:

- `R53_NO_OBSERVED_EXCESS_WORK_IN_SCOPE_V1`
- `R53_SOFTWARE_BASELINE_SUFFICIENT_IN_SCOPE_V1`
- `R53_ALGORITHM_CHANGE_NOT_MAPPING_GAIN_V1`
- `R53_INPUT_OR_BASELINE_NOT_QUALIFIED_V1`
- `R53_HOST_RUNTIME_COST_NOT_ARCH_LOCALIZED_V1`
- `R53_RESIDUAL_READY_FOR_ARCH_REVIEW_V1`

Negative or incomplete qualification is a valid successful outcome.

Do not continue to R54/R55 inside this stage.
