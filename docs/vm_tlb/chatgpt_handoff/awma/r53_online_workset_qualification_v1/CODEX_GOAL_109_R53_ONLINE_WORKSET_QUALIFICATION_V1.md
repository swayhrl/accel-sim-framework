# CODEX GOAL — AWMA R53 Online Legal-Workset Native Qualification V1

## Mission

Enter Goal mode and execute continuously to the scientific STOP boundary.

This is a **single merged native qualification round** for:

`R53_N1_ONLINE_LEGAL_WORKSET_REALIZATION`

Question:

> With the decoder and KV refresh/reuse policy fixed, does a real block-diffusion LLM expose dynamically changing legal work that a credible software execution cannot realize efficiently, leaving a material online organization residual?

Do not design a hardware mechanism in this Goal.

Repository:
`swayhrl/accel-sim-framework`

Coordination branch:
`hrl/awma-r53-online-workset-qualification-handoff-v1`

Accepted execution base:
`db2000f7222030282f788bd009243ab1a43ed867`

Required literature authority:
`hrl/awma-chatgpt-literature-notes-v1 @ 23e9db4ea6fadafc43430a7b6b878b86b73f19e8`

Required handoff:
`docs/vm_tlb/chatgpt_handoff/awma/r53_online_workset_qualification_v1/R53_NATIVE_QUALIFICATION_HANDOFF_CONTEXT_2026-09-27.md`

Stage:
`AWMA_R53_ONLINE_WORKSET_QUALIFICATION_V1`

Execution node:
**109 / RTX4080 / SM89 only**

Do not use node174.
Do not run Accel-Sim.
Do not build a hardware simulator mechanism.
Do not download any model other than the single pinned R53 model.

Ordinary engineering issues are solve-and-continue.
Stop only for scientific identity/semantic-contract failure or a bounded engineering admission failure defined below.

---

# Phase 0 — read, inventory, isolate

Read the full handoff and Round06 source/design note before changing code.

Confirm the working branch contains accepted R51 V2 but do not rerun it.

Inspect:
- free disk;
- GPU memory/state;
- current Python/CUDA/driver;
- existing hf cache/model assets;
- existing C16 timing/NSYS/hash/publication helpers;
- node164 reachability.

Create a dedicated R53 workspace, e.g.:

`/data/c16/awma/r53_online_workset_qualification_20260927/`

Create a dedicated isolated Python environment under that workspace or a similarly isolated path.

Never mutate:
- accepted C16 environment;
- system CUDA;
- NVIDIA driver;
- existing model assets.

Record `PRE_EXECUTION_INVENTORY.md`.

---

# Phase 1 — pin external source/model/data before GPU science

## 1.1 Fast-dLLM source

Pin exactly:

- repo: `NVlabs/Fast-dLLM`
- commit: `a9b81e4caa240c8cad4f7dc1889ff4852a0fca5b`

Fetch/checkout only this exact commit.

Hash:
- git commit/tree;
- `v2/generation_functions.py`;
- model code/config files actually imported;
- dependency manifests.

No unpinned `main` source may enter a scientific run.

## 1.2 Model

Only allowed model:

`Efficient-Large-Model/Fast_dLLM_v2_1.5B`

Required revision:

`25093b6f63300adfd57f72145083c8a528fe4f16`

Download to R53 staging or an isolated model asset path.

Requirements:
- exact revision must be verified after download;
- hash every scientific model/config/tokenizer/code file;
- no second checkpoint;
- no quantized replacement;
- no CPU/disk offload fallback;
- no trust of changing remote code outside the pinned snapshot.

Create:
`MODEL_ADMISSION_RECEIPT.json`

## 1.3 Datasets

Datasets:

### GSM8K
- repo: `openai/gsm8k`
- config: `main`
- split: `test`
- prompt field: `question`

### HumanEval
- repo: `openai/openai_humaneval`
- split: `test`
- prompt field: `prompt`
- stable source ID: `task_id`

Resolve the exact snapshot revisions and freeze them before model timing.

Do not execute HumanEval generated code.

For each dataset:
- materialize frozen test split;
- calculate exact file/row hashes;
- record dataset library version and snapshot revision.

Create:
`DATASET_SNAPSHOT_RECEIPT.json`

---

# Phase 2 — deterministic request selection and prompt freezing

For each dataset:

Define canonical ID:
- GSM8K: `gsm8k/main/test/<row_index>`
- HumanEval: source `task_id`

Define:
`selection_key = SHA256(canonical_id + "\n" + exact_raw_prompt)`

Sort ascending.

Freeze:
- first 4 = DISCOVERY;
- next 4 = HOLDOUT.

Do not select by:
- length;
- latency;
- output;
- quality;
- number of diffusion iterations;
- dynamicity;
- GPU behavior.

For every selected sample record:
- canonical ID;
- selection SHA;
- exact raw prompt;
- prompt SHA;
- rendered model prompt;
- rendered prompt SHA;
- token IDs;
- token IDs SHA.

Use the pinned model/tokenizer's required prompt format.

Any task instruction added to the raw prompt must be defined once and identically for all arms before GPU execution.

Create:
`REQUEST_SELECTION.tsv`

No holdout result may be inspected during A1 design/tuning.

---

# Phase 3 — isolated runtime qualification

Install only what the pinned Fast-dLLM source/model needs in the isolated environment.

Record:
- Python version;
- torch version;
- CUDA wheel/runtime version;
- transformers;
- triton;
- flash-attn/flashinfer/other relevant packages;
- compiler versions;
- package hashes/lock file;
- GPU/driver.

Do not alter host driver.

At most two surgical dependency/runtime fixes are allowed.

If the pinned model cannot run on this node after two bounded fixes:
`R53_INPUT_OR_BASELINE_NOT_QUALIFIED_V1`
with reason `RUNTIME_NOT_QUALIFIED`.

Do not substitute another model.

Create:
`RUNTIME_ENVIRONMENT_RECEIPT.json`

---

# Phase 4 — preregister policy, concurrency, semantics

Before any formal timing create:
`PREREGISTRATION.json`

Freeze:

## 4.1 Generation policy

- dtype = BF16
- block_size = 32
- small_block_size = 8
- threshold = 0.9
- temperature = 0.0
- top_p = 0.95
- use_block_cache = true
- max_new_tokens = 512
- normal stop/EOS enabled

No parameter sweep.

## 4.2 Concurrency

Primary:
`B=4`

Pre-registered resource fallback:
`B=2` only if B4 fails **memory admission before formal timing**.

If B2 fallback is used:
- pair discovery/holdout requests in deterministic selection order:
  `[0,1]`, `[2,3]`;
- aggregate both pairs as one logical dataset bundle in reported totals.

If B2 also cannot run:
`R53_INPUT_OR_BASELINE_NOT_QUALIFIED_V1`
with reason `RESOURCE_ADMISSION_FAILED`.

No offload, precision change, prompt shortening, or second model.

## 4.3 Measurement

Per formal point:
- one canary;
- 2 warmups;
- 7 full-generation measured repetitions.

Use paired/interleaved A0/A1 order.

All formal GPU runs hold:
`/data/c16/locks/c16_gpu_campaign.lock`

Primary performance:
full logical-bundle end-to-end wall-clock.

Also record:
- valid generated tokens;
- tokens/s;
- per-request completion;
- CUDA-event/GPU duration where meaningful;
- peak memory.

One NSYS identity/timeline canary per discovery arm/domain is sufficient.
Do not profile every repetition.

---

# Phase 5 — canary and memory admission

## 5.1 B1 functional canary

Use GSM8K DISCOVERY request 0.

Verify:
- model loads;
- CUDA execution;
- no NaN/Inf failure;
- generation progresses;
- stop/max-token behavior is recorded;
- policy values are really applied;
- block cache path is exercised when expected.

This is not a timing result.

## 5.2 B4 resource canary

Use the 4 GSM8K discovery requests.

Record:
- peak allocated;
- peak reserved;
- generation status;
- OOM;
- truncation;
- unexpected fallback/offload.

If B4 OOM, activate only the preregistered B2 fallback.

Do not decide B2 because it is faster.

---

# Phase 6 — implement untimed semantic/lifecycle ledger

Instrument the **reference A0 algorithm** first.

Keep this pass outside formal timing.

Required schema:

- domain;
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
- forced_commit_positions;
- stop_transition;
- graph_bucket_if_any;
- evidence_class;
- notes.

Evidence classes:
- `REQUIRED_ACTIVE_WORK`
- `COHORT_POLICY_REQUIRED_WORK`
- `PASSIVE_EXECUTION_CANDIDATE`
- `LEGALLY_OMITTABLE_IN_SCOPE`
- `UNKNOWN`

Important:

Do not mark a row legally omittable from mask count alone.

`LEGALLY_OMITTABLE_IN_SCOPE` may be assigned only after A1 actually omits that work **and** preserves the frozen semantic trajectory.

If a per-layer required set cannot be proven, leave it UNKNOWN.

Create:
- `SEMANTIC_TRAJECTORY_SCHEMA.md`
- initial `LEGAL_WORK_LEDGER.tsv.gz`

---

# Phase 7 — A0 reference implementation

Arm:

`A0_PINNED_OFFICIAL_BATCHED_REFERENCE`

Use the exact pinned Fast-dLLM v2 algorithm and the frozen policy.

A0 is semantic authority.

Preserve:
- official block/subblock loops;
- official block cache;
- official batch-wide mask conditions;
- official batch-wide full-refresh/reuse decision;
- official finished-request behavior.

Do not "optimize" A0.

Before formal timing establish deterministic or repeatably equivalent discrete trajectories under temperature=0.

If the same A0 input produces inconsistent discrete commit/cache trajectories across repeated clean runs:
fail closed:
`R53_INPUT_OR_BASELINE_NOT_QUALIFIED_V1`
reason `REFERENCE_TRAJECTORY_NOT_STABLE`.

---

# Phase 8 — A1 strong software workset implementation

Arm:

`A1_STRONG_SEMANTIC_WORKSET_SOFTWARE`

A1 is an execution reorganization only.

The rule is:
**compute A0's algorithmic decision first, then reorganize how the already-decided work is executed.**

## 8.1 Preserve cohort policy

For every logical step:
- compute the same A0 cohort-level mask/full-refresh decision;
- freeze it;
- only then form execution sub-batches.

A1 must not reduce refreshes by changing cohort membership.

## 8.2 Active request/subblock packing

Pack only request rows whose output/cache work is required under the already-frozen A0 decision.

Scatter results back to canonical request order.

An omitted request keeps prior state/cache exactly.

## 8.3 Finished-request compaction

Physically remove a finished request at the earliest state-safe boundary after its logical A0 finish point.

Do not advance the logical finish time.

## 8.4 Reusable buffers

Reuse:
- gather indices;
- scatter indices;
- packed inputs;
- output scatter buffers;
- metadata buffers.

Avoid obvious allocator churn.

## 8.5 Strong performance hardening

Allowed batch buckets:
`1, 2, 4` only.

At most two hardening attempts:

1. CUDA Graph capture for stable legal bucket segments;
2. compile/fused control path if graph capture is structurally incompatible.

Do not invent a custom GPU scheduler.

Do not reproduce a full serving system.

A1 is qualified only if it is a credible implementation of:
- legal active-work packing;
- state-safe compaction;
- reusable metadata/buffers;
- bounded graph/compile optimization where legal.

If A1 cannot be made credible without semantic change:
`R53_INPUT_OR_BASELINE_NOT_QUALIFIED_V1`
reason `STRONG_SOFTWARE_BASELINE_NOT_QUALIFIED`.

Engineering failure is not a hardware-positive result.

---

# Phase 9 — semantic equivalence gate

Define:
`R53_FIXED_DECODER_CACHE_TRAJECTORY_V1`

For every request in each DISCOVERY bundle, A1 must match A0 on:

- logical block sequence;
- subblock sequence;
- committed position set per logical step;
- committed token IDs;
- threshold/confidence commit decision;
- fallback/max-prob forced commit;
- stop/EOS transition;
- request-finished transition;
- A0 cohort-derived full-refresh/reuse decision;
- cache epoch/update events;
- next-block seed transition where applicable.

Also record:
- final token IDs;
- final text hash.

Internal logits need not be bitwise equal if all frozen discrete decisions remain identical.

If a difference appears:
- one surgical correctness repair is allowed when clearly an implementation bug;
- do not change the algorithm or thresholds.

If the gain requires different decisions:
`R53_ALGORITHM_CHANGE_NOT_MAPPING_GAIN_V1`
and STOP after closure.

Create:
`A0_A1_SEMANTIC_EQUIVALENCE.tsv`

---

# Phase 10 — discovery formal matrix

Discovery logical bundles:

1. GSM8K DISCOVERY
2. HumanEval DISCOVERY

Arms:
- A0
- A1

Total:
4 logical formal conditions.

For each:
- canary;
- 2 warmups;
- 7 measured repetitions.

Do not execute HumanEval output code.

Use identical inputs/policy across A0/A1.

Record each repetition separately.

One NSYS canary per domain/arm.

---

# Phase 11 — workset and performance accounting

For A0/A1 compute:

## Work proxies

- transformer token rows executed;
- attention query rows;
- attention score-element proxy when exact key length is known;
- logits rows materialized;
- forward count;
- request-active area over logical time.

## Organization costs

- packing rows;
- scatter rows;
- packing/scatter bytes;
- gather/scatter GPU time;
- metadata preparation wall/GPU time;
- host control/API time;
- allocation count if observable;
- graph launch count;
- GPU idle gaps.

## End-to-end

- full bundle wall-clock;
- valid generated tokens;
- tokens/s;
- per-request completion;
- GPU union busy time;
- peak memory.

No independent component times may be naively summed into an artificial critical path.

---

# Phase 12 — discovery classification

Use the following gates.

A performance effect is called stable only if:
- end-to-end difference is >=5%, **and**
- the effect exceeds 3x the larger run-to-run noise/jitter envelope.

The 5% gate is an investment screen, not an equality proof.

## 12.1 No material legal excess

If A1 cannot legally reduce meaningful work in either domain, or every meaningful work proxy changes by <5%:

`R53_NO_OBSERVED_EXCESS_WORK_IN_SCOPE_V1`

No D.
No holdout.
STOP after closure.

## 12.2 Strong software closes it

If:
- semantic gate passes;
- A1 legally reduces work;
- A1 gives stable >=5% end-to-end improvement;
- no >=5% online organization residual is visible;

then:

`R53_SOFTWARE_BASELINE_SUFFICIENT_IN_SCOPE_V1`

No architecture review.

A holdout is optional only if needed to ensure the software-positive conclusion is not a one-bundle anomaly; do not expand into a paper-scale campaign.

## 12.3 Host/runtime limited

If:
- legal work reduction exists;
- A1 does not realize it efficiently;
- remaining cost is dominated by Python/host/API control;
- graph/compile hardening cannot close it for engineering reasons;

then:

`R53_HOST_RUNTIME_COST_NOT_ARCH_LOCALIZED_V1`

Do not send directly to 174.

## 12.4 Residual needs one diagnostic

Only if:
- semantic equivalence passes;
- legal work reduction is >=5% in at least one meaningful work proxy;
- A1 is a credible strong baseline;
- >=5% end-to-end unresolved cost or severe realization gap remains;
- pure host control does not already explain it;

set intermediate:
`R53_RESIDUAL_DIAGNOSTIC_REQUIRED`

Then run D.

---

# Phase 13 — D diagnostic, maximum one condition

D is:
`CURRENT_STEP_METADATA_READY_DIAGNOSTIC_ONLY`

Choose domain by frozen rule:
- larger absolute unresolved A0↔A1 cost;
- tie -> GSM8K.

D may prepare outside the timed region only metadata derivable from the **current logical step at entry**:

- pack indices;
- scatter indices;
- bucket ID;
- buffer offsets.

D may not use:
- future commit decisions;
- future confidence;
- future cache state;
- future model outputs.

Then run the same A1 GPU computation.

D is not deployable.
Do not call it an upper bound.

If stable D gain is <5%:
online workset/metadata organization is not material enough:
classify according to the observed software/host result and STOP.

If stable D gain is >=5%:
continue to one holdout pair.

---

# Phase 14 — holdout, conditional only

Use the same domain that triggered the residual.

Use that domain's preregistered next 4 HOLDOUT prompts.

Use the same admitted B4/B2 mode.

Run:
- A0;
- strongest qualified A1;
- D only when required to confirm the localized residual.

No tuning on holdout.

For a candidate to survive:
- semantic trajectory still matches;
- legal work reduction remains;
- >=5% stable organization residual/diagnostic effect remains.

Otherwise close negative.

---

# Phase 15 — final decision

Emit exactly one:

- `R53_NO_OBSERVED_EXCESS_WORK_IN_SCOPE_V1`
- `R53_SOFTWARE_BASELINE_SUFFICIENT_IN_SCOPE_V1`
- `R53_ALGORITHM_CHANGE_NOT_MAPPING_GAIN_V1`
- `R53_INPUT_OR_BASELINE_NOT_QUALIFIED_V1`
- `R53_HOST_RUNTIME_COST_NOT_ARCH_LOCALIZED_V1`
- `R53_RESIDUAL_READY_FOR_ARCH_REVIEW_V1`

The last state requires all:

1. real pinned Fast-dLLM v2 checkpoint;
2. deterministic frozen requests;
3. exact discrete A0/A1 decoder/cache trajectory match;
4. legal work reduction actually demonstrated;
5. strong A1 qualified;
6. stable >=5% end-to-end or current-step organization residual;
7. holdout support;
8. not mainly Python/host overhead;
9. closest-work review identifies a concrete missing capability.

Do not invent a hardware mechanism after reaching this state.
STOP for ChatGPT review.

Do not move to R54/R55.

---

# Phase 16 — publication

Durable root:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r53_online_workset_qualification_20260927/`

Review pack:

`docs/vm_tlb/review_packs/AWMA_R53_ONLINE_WORKSET_QUALIFICATION_V1/`

Required:
- `README.md`
- `R53_SOURCE_AND_CLOSEST_WORK_AUDIT.md`
- `PRE_EXECUTION_INVENTORY.md`
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

Large model/raw profiler files do not enter Git.

Final closure:

`science/engineering -> node164 -> review pack -> hashes -> commit -> push -> fetch-back -> exact remote SHA/tree verification -> clean worktree -> GPU lock released -> STOP`

Git transport failure is publication failure only.
Do not rerun science because push fails.
Use the accepted HTTPS -> HTTP/1.1 -> SSH -> gh/API fallback sequence.

No automatic merge.
