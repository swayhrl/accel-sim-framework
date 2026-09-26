# CODEX GOAL — AWMA P1/P2 Native Problem Qualification V1

## Purpose

Enter Goal mode and execute continuously to the scientific STOP boundary.

This is one merged qualification round for two post-AWMA research questions:

- **P1 — numerical-contract / reduction parallelism**
- **P2 — online sparse-selection / index-readiness dependency**

The objective is **not** to build a mechanism. The objective is to decide, in one bounded native campaign, whether either problem still has a material, localized residual after a credible software baseline.

Ordinary engineering issues are solve-and-continue. Do not stop for routine package, build, parser, or wrapper problems. Stop only for a scientific identity/contract/claim change that cannot be resolved without redefining the preregistered question.

Repository:
`swayhrl/accel-sim-framework`

Coordination branch:
`hrl/awma-p1-p2-native-qualification-handoff-v1`

Accepted base:
`9098443082d8edd4f0efa2fa8922969c0559254a`

Stage:
`AWMA_P1_P2_NATIVE_PROBLEM_QUALIFICATION_V1`

Execution node:
**109 / RTX4080 / SM89 only**

Do not run Accel-Sim in this Goal.
Do not create a 174 execution dependency.
Do not download new models.

---

# 0. Required reading / frozen evidence

Read the accepted post-negative closure:

`docs/vm_tlb/review_packs/AWMA_POST_NEGATIVE_PROBLEM_PIVOT_V1/`

Especially:
- `FINAL_DECISION.md`
- `RULED_OUT_SPACE.md`
- `CANDIDATE_SCREEN.tsv`

Fetch and read the ChatGPT literature branch at the exact accepted literature commit:

Branch:
`hrl/awma-chatgpt-literature-notes-v1`

Required commit:
`082dd8b36b199e135585c0ba61cab587d6814e60`

Required file:
`docs/vm_tlb/literature_notes/awma/rounds/2026-09-26_ROUND_04_PROBLEM_DISCOVERY.md`

Do not reinterpret the earlier negative results as positives:
- no new resident-translation problem;
- no UVM mechanism problem;
- no generic cache/MSHR/DRAM resource problem;
- no PREL1 revival;
- no raw-vs-AWQ mechanism in this Goal.

---

# 1. Shared campaign rules

## 1.1 Reuse existing infrastructure

Prefer existing:
- C16 frozen input/model authorities;
- runtime-native runner identity logic;
- NSYS wrapper / CUDA-event timing infrastructure;
- model/local replay state if already accepted;
- GPU lock:
  `/data/c16/locks/c16_gpu_campaign.lock`
- data-plane publication to node164.

Do not rebuild the C16 pipeline.

Any new harness must be small, local to this stage, and produce explicit identity/receipt files.

## 1.2 Parallelism

Before GPU execution:
- audit/build P1 and P2 harnesses in parallel when they do not share mutable state;
- run CPU unit tests/source audits concurrently if resources permit.

Actual GPU measurements are serialized under the existing GPU lock.

Do not run two independent GPU profilers concurrently.

## 1.3 Measurement policy

For every timing arm:
- one bounded canary first;
- then **2 warmups + at least 5 measured repetitions**;
- preserve individual measurements, median, min/max, CV;
- use CUDA events for operator-local GPU time when valid;
- keep wall-clock time as secondary;
- use fresh processes when the comparison depends on runtime/kernel-selection state;
- record GPU/driver/CUDA/PyTorch/library identity;
- no thermal-throttled run may silently enter the comparison.

NCU is **conditional**, not default:
- only after a native timing residual survives;
- at most two targets per candidate;
- collect only metrics needed to distinguish the registered alternatives.

No NVBit full-address capture in this Goal.

## 1.4 Materiality gate

A timing residual is `MATERIAL` only if both hold:

1. median relative difference is at least **5%**;
2. the relative difference is greater than **3x the larger arm CV**.

If the absolute operator time is so small that the result cannot affect a meaningful operator/phase share, classify `LOW_APPLICATION_RELEVANCE` even if the relative percentage is large.

Do not tune thresholds after seeing results.

---

# 2. P1 — numerical contract vs reduction parallelism

## 2.1 Scientific question

Under a fixed output contract for one target request:

> Does enforcing batch/schedule-invariant numerical behavior still impose a material execution cost after a credible software baseline, and can that cost be localized to reduction completion/commit or intermediate-result handling rather than simply extra arithmetic?

This is not:
- generic floating-point non-associativity;
- generic determinism;
- cross-GPU determinism;
- a requirement that every inference deployment be bitwise invariant.

The primary contract for this stage is:

`TARGET_REQUEST_BATCH_INVARIANCE_V1`

Within one fixed GPU/software environment, the target request's output must be compared when unrelated companion requests change the batch/execution shape.

## 2.2 Target selection — bounded

Attempt at most **two** operator targets:

Priority A:
- an accepted attention/SplitKV/Combine-style reduction target already tied to a real Qwen/Llama execution and recoverable functional inputs.

Priority B:
- an accepted GEMM/linear reduction target with a real model-derived shape/input and an actual multi-part reduction or split accumulation path.

Do not invent semantic names from kernel names.

If no target has recoverable functional input/output identity, a shape-faithful synthetic reduction fixture may be built only as:
`DIAGNOSTIC_FIXTURE_ONLY`.
It cannot qualify P1 for hardware development.

## 2.3 Frozen target-request construction

For each qualified target:

- freeze one target request/input exactly;
- construct batch arms with target request in a fixed slot;
- companion requests must be deterministic and independent;
- begin with the two cheapest legal shape-changing arms, preferably B1 and B4 if memory permits;
- use B2 or a second frozen input/length as holdout only if P1 survives discovery.

The target request's mathematical input must not change across batch arms.

Record:
- target input hashes;
- companion-input generation rule and hashes;
- exact operator/kernel implementation selected in each arm;
- launch/grid/block/runtime identities.

A kernel implementation change is evidence, not automatically a failure.

## 2.4 Output contract measurements

For the target request only, record:
- raw output bytes hash where feasible;
- bitwise equality;
- max absolute difference;
- max relative difference;
- ULP-style difference when dtype/tooling makes it well-defined.

Never substitute task accuracy for this contract.

Classify each implementation arm as:
- `BITWISE_INVARIANT`
- `NUMERICALLY_CLOSE_NOT_BITWISE`
- `CONTRACT_MISMATCH`

## 2.5 Required baselines

At minimum distinguish:

### P1-A — stock optimized execution

Use the qualified existing library/runtime implementation.

### P1-B — contract-preserving software baseline

Audit the strongest credible implementation available on this environment.

Acceptable examples include:
- existing deterministic/reproducible library mode;
- fixed work decomposition/split size;
- a library-supported deterministic reduction mode;
- a small software implementation that preserves the **same arithmetic contract** and is not intentionally serialized beyond what the contract requires.

A deliberately single-threaded or globally locked reduction is **not** a strong baseline.

If no credible contract-preserving software baseline can be established, P1 may characterize behavior but must end:
`P1_NOT_QUALIFIED_STRONG_BASELINE_MISSING`.

### P1-C — decomposition diagnostic, optional

Only if needed to localize a surviving gap:
separate producer work, partial-result storage, and final reduction/commit timing.

This is diagnostic only and must not redefine the output contract.

## 2.6 P1 decisions

Emit exactly one:

- `P1_NO_BATCH_DEPENDENT_NUMERICAL_PROBLEM`
- `P1_CONTRACT_COST_LOW_OR_NOISY`
- `P1_SOFTWARE_BASELINE_CLOSES_GAP`
- `P1_NOT_QUALIFIED_STRONG_BASELINE_MISSING`
- `P1_RESIDUAL_REDUCTION_COST_SUPPORTED`

The final state is allowed only if:
- output contract is explicit;
- stock execution exhibits a relevant contract/cost tradeoff;
- a strong software baseline preserves the same contract;
- a material residual remains;
- diagnostic evidence localizes the residual beyond “the deterministic version does more work.”

If P1 does not survive, stop P1 and continue P2.

---

# 3. P2 — online sparse selection to consumer dependency

## 3.1 Scientific question

For a fixed sparse-selection algorithm and exact selected-index result:

> After strong software execution, how much of the online
> `selection -> index readiness -> selected-KV consumption -> attention`
> chain remains exposed, and is any residual more than the selector's own arithmetic cost?

This is **not**:
- UVM/page migration;
- TLB translation;
- “gather is always slow”;
- random sparse masks;
- a claim that the existing dense model naturally implements sparse attention.

## 3.2 Selector contract

Use one bounded, explicit selector.

Preferred selector:
**Quest-style query-aware page selection**, because its algorithm is sufficiently specified and has a simple two-stage contract.

Quest source semantics to preserve:
- page-granularity KV metadata;
- per page, channel-wise `K_min` and `K_max`;
- for query component `q_i`, page bound component:
  `max(q_i * K_min_i, q_i * K_max_i)`;
- page score is the sum over dimensions;
- choose exact Top-K pages under a declared stable tie-break;
- run standard attention on the selected pages.

Primary source:
Tang et al., QUEST, ICML 2024:
`https://proceedings.mlr.press/v235/tang24l.html`

Code/project:
`https://github.com/mit-han-lab/Quest`

Do not claim a full Quest reproduction unless implementation/source equivalence is actually established.

If using a local reimplementation, label it:
`QUEST_STYLE_SELECTOR_DIAGNOSTIC_V1`.

## 3.3 Input identity

Prefer real model-derived Q/K/V from an accepted local Qwen/Llama execution.

A model-derived input is qualified only if:
- exact model/revision/scenario/layer/head identities are recorded;
- Q/K/V tensor shapes/dtypes and hashes are bound;
- the extraction does not alter the tensors used for the measured operator.

If real Q/K/V extraction cannot be closed after bounded engineering work, a deterministic shape-faithful fixture may be used only as:
`P2_SHAPE_DIAGNOSTIC_ONLY`.
Such a fixture cannot authorize hardware development.

Do not download a new sparse-attention model for this stage.

## 3.4 Frozen sparse configuration

Use at most two discovery configurations:
- one moderate selected fraction;
- one more aggressive selected fraction.

Choose them **before timing** based on context length / page count.
Do not sweep Top-K to find a positive point.

Page size, context length, head count, head dimension, dtype, and tie-break rule must be frozen in the preregistration receipt.

## 3.5 Three required arms

For each discovery configuration:

### P2-A — ONLINE

Execute:
`metadata score -> stable Top-K -> gather/select KV -> sparse attention`

Measure full chain and each legal stage.

### P2-B — READY-INDEX DIAGNOSTIC

Use the **exact indices produced by the paired ONLINE run** and execute the same selected-KV consumer.

This removes index-generation timing.

It is:
`DIAGNOSTIC_NOT_IMPLEMENTABLE_BASELINE`

It must **not** be called a strict performance upper bound.

Selected pages, order, Q/K/V values, dtype, and consumer arithmetic must match the ONLINE arm.

### P2-C — STRONG SOFTWARE ONLINE

Keep online selection semantically live.

Use the strongest feasible software implementation available without changing the selector result, for example:
- fused/compiled score + top-k path;
- buffer reuse;
- CUDA Graph where appropriate;
- kernel fusion that preserves exact selected indices;
- efficient gather/index-select already present in the runtime.

Do not call eager Python/PyTorch alone a strong baseline if an obvious compiled/fused path is available.

## 3.6 Required accounting

Record:
- full online chain time;
- selector-only time;
- top-k/index-publication time when separable;
- selected-KV gather/consumer time;
- ready-index consumer time;
- strong-software online time;
- selected index hash;
- selected page count/order;
- output hash and numerical difference between ONLINE and READY-INDEX arms;
- logical selected KV bytes;
- bytes/materialization that can be measured without heavy tracing;
- kernel/launch count.

The key diagnostic is not simply:

`ONLINE - READY_INDEX`.

Explicitly test whether the observed difference is explainable by selector arithmetic and extra work.

## 3.7 P2 decisions

Emit exactly one:

- `P2_ONLINE_DEPENDENCY_LOW`
- `P2_COST_DOMINATED_BY_SELECTOR_COMPUTE`
- `P2_SOFTWARE_PIPELINE_CLOSES_GAP`
- `P2_SHAPE_DIAGNOSTIC_ONLY_NOT_QUALIFIED`
- `P2_RESIDUAL_INDEX_READINESS_COST_SUPPORTED`

The final state requires:
- model-derived or otherwise scientifically qualified input;
- exact index-result equality across compared semantic arms;
- strong software baseline;
- material native residual;
- evidence the residual is not explained by selector arithmetic alone.

If P2 fails, do not vary masks/models until a positive result appears.

---

# 4. Conditional NCU diagnostics

Only a candidate with a native `MATERIAL` residual may invoke NCU.

Maximum:
- P1: 2 target/arm comparisons total.
- P2: 2 target/arm comparisons total.

Pre-register the metrics before collection.

Allowed purposes include:
- occupancy/register pressure;
- memory traffic;
- issue/stall class;
- selected cache/DRAM traffic.

Do not use NCU replay timing as the primary native runtime result.

Do not infer hidden TLB/page behavior.

---

# 5. Cross-candidate decision

After both P1 and P2 finish, build:

`P1_P2_DECISION_MATRIX.tsv`

Columns:
- candidate
- qualified_input
- exact_contract
- strong_software_baseline
- material_native_cost
- localized_cause
- closest_work_overlap
- holdout_available
- next_action

Final stage state must be exactly one:

- `P1_P2_NATIVE_QUALIFICATION_NO_RESIDUAL_V1`
- `P1_NATIVE_RESIDUAL_READY_FOR_ARCH_REVIEW_V1`
- `P2_NATIVE_RESIDUAL_READY_FOR_ARCH_REVIEW_V1`
- `P1_P2_BOTH_RESIDUALS_READY_FOR_ARCH_REVIEW_V1`
- `P1_P2_NATIVE_INPUT_OR_BASELINE_NOT_QUALIFIED_V1`

“READY_FOR_ARCH_REVIEW” does **not** authorize a simulator mechanism.
It only authorizes the next ChatGPT review to decide whether 174 modeling is justified.

If a candidate survives discovery, run one bounded holdout **in this same Goal** if an already-qualified holdout input exists.
Do not create a new model download merely to manufacture a holdout.

---

# 6. Efficiency / engineering bounds

This is intentionally one merged round.

- Build/audit both harnesses before the first long GPU measurement where practical.
- Reuse one environment identity and one GPU-lock protocol.
- Reuse shared timing/output/hash helpers.
- Do not create separate engineering repair Goals.
- Do not create a new branch for every small fix inside this stage.
- If one candidate becomes scientifically blocked, close it and continue the other.
- No broad parameter search.
- No new model download.
- No NVBit full trace.
- No Accel-Sim.
- No PPA.
- No automatic merge.

Engineering attempt bounds:
- at most two surgical attempts for any optional compiled/fused baseline before marking it unavailable;
- a missing wrapper/index that can be deterministically reconstructed is not a scientific blocker;
- missing scientific tensor/input identity is a blocker for that arm.

---

# 7. Publication / authority

New native raw/results go first to 109 staging and then publish to node164 under a dedicated stage authority.

Suggested durable root:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/p1_p2_native_qualification_20260926/`

Large raw profiler files do not enter Git.

Review pack:

`docs/vm_tlb/review_packs/AWMA_P1_P2_NATIVE_PROBLEM_QUALIFICATION_V1/`

Required minimum:
- `README.md`
- `SOURCE_AND_ASSET_AUDIT.md`
- `PREREGISTRATION.json`
- `P1_TARGETS.tsv`
- `P1_NUMERIC_CONTRACT_RESULTS.tsv`
- `P1_TIMING_RESULTS.tsv`
- `P1_DECISION.md`
- `P2_SELECTOR_CONTRACT.md`
- `P2_INPUT_RECEIPT.json`
- `P2_TIMING_RESULTS.tsv`
- `P2_INDEX_EQUALITY.tsv`
- `P2_DECISION.md`
- conditional NCU result files if used
- `P1_P2_DECISION_MATRIX.tsv`
- `FINAL_DECISION.md`
- `RAW_DATA_INDEX.tsv`
- `SHA256SUMS`

Closure:

`science/engineering -> node164 -> review pack -> hashes -> commit -> push -> fetch-back -> exact remote SHA/tree verification -> clean worktree -> STOP`

Git transport failure is publication failure only. Preserve the exact local commit and use the configured HTTPS -> HTTP/1.1 -> SSH -> gh/API fallback sequence. Never rerun science because push transport fails.
