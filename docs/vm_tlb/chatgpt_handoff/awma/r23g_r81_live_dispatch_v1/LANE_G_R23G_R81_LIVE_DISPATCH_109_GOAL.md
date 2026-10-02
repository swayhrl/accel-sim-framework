# Codex Goal — Lane G / node109
## AWMA R23G R81 live RULE_U01 mixed-dispatch validation V1

Date: 2026-10-02

Repository:
`swayhrl/accel-sim-framework`

Execution branch:
`hrl/awma-r23g-r81-live-dispatch-109-v1`

Scientific parent:
`296263043f4949467b33c6c99a695ac5c139104d`

Stage:
`AWMA_R23G_R81_LIVE_DISPATCH_109_V1`

Review pack:
`docs/vm_tlb/review_packs/AWMA_R23G_R81_LIVE_DISPATCH_109_V1/`

One bounded solve-and-continue Goal.

Scientific question:

> On unseen structured-generation inputs, does the fixed RULE_U01 policy retain a positive **net head-region response after exact union computation and real dense/direct-index switching costs are included**, and does it avoid a material complete-generation regression?

This is a software execution-organization validation.
No hardware claim is authorized.

---

# 0. Frozen historical authority

Reuse the exact accepted R81 runtime/model/toolchain where available:

Scientific parent:
`69e74fe74e18d1f3a71bfac0d097ce49234327a9`

Audit parent:
`296263043f4949467b33c6c99a695ac5c139104d`

Frozen model/head:
- Qwen2.5-0.5B accepted R81 model/tokenizer/head identity
- BF16 vendor dense A0
- A3 fixed direct-index ragged implementation
- XGrammar 0.2.8 exact wheel/source authority
- greedy generation semantics
- accepted persistent A0/A3 scratch lifetime.

Do not change head kernels or optimize A3 in this Goal.

RULE_U01 remains exactly:

`IF legal_union_fraction < 0.01: A3 ELSE: A0`

Strict less-than.
No threshold sweep.
No learned classifier.
No per-step measured winner.

Old C0/C1/H0 are not validation inputs and are not relabeled as holdout.

---

# 1. New public validation-input authority

Use a public function-calling corpus disjoint from the authored R81 fixtures.

Preferred source:
`korotkov/glaive-function-calling-v2-parsed`
public Hugging Face dataset, `test` split.

This source is a parsed derivative of Glaive Function Calling V2.
Do not claim it is an independent production distribution.

Before any GPU performance work:
- resolve and record exact dataset repository revision/commit through Hugging Face Hub;
- record exact downloaded/parquet/cache file SHA256(s);
- record dataset split fingerprint if available.

If this exact dataset becomes unavailable, STOP:
`R23G_PUBLIC_VALIDATION_INPUT_NOT_QUALIFIED`

Do not silently substitute another dataset.

## Deterministic candidate extraction

Parse each test row's:
- messages
- functions.

A row is structurally eligible only if:
1. exactly one function definition is present;
2. the function contains an object-like `parameters` JSON schema;
3. at least one user message occurs before the first function-call message;
4. a first user message and function name/description can be extracted deterministically;
5. XGrammar 0.2.8 can compile the parameter schema.

Construct the validation prompt with one frozen template:

`You may call function <NAME>. <DESCRIPTION>\nUser request: <FIRST_USER_MESSAGE>\nReturn only the JSON arguments object for this function.`

Grammar:
exact function `parameters` schema.

Canonical row identity:
SHA256 over canonical JSON containing:
- dataset revision
- original row index
- function definition
- first user message
- frozen prompt template version.

Sort structurally eligible rows by canonical SHA256.

Take the first 24 rows as the **qualification pool**.

No union fraction, output length, timing, or A0/A3 performance may influence this ordering.

## Baseline semantic qualification and final 12

Run only B0/A0 semantic qualification, with timing ignored, over the 24 rows in sorted order.

Select the first 12 rows that:
- compile under XGrammar
- terminate within max_new_tokens=128
- produce parseable JSON
- satisfy the exact parameter schema
- do not truncate.

This correctness filter is frozen before candidate execution.
Do not inspect union fraction distribution while selecting the 12.

If fewer than 12 qualify:
`R23G_PUBLIC_VALIDATION_INPUT_NOT_QUALIFIED`
STOP.

Freeze the final 12 record hashes before RULE_U01 timing.

Group them consecutively by canonical hash order into:
- V0 = rows 0..3
- V1 = rows 4..7
- V2 = rows 8..11

Three B4 batches.
Do not regroup by schema/sparsity/output length.

Write:
- `PUBLIC_INPUT_AUTHORITY.json`
- `VALIDATION_COHORT.tsv`

---

# 2. Exact online union statistic — one fixed implementation

The accepted source already has the current CPU XGrammar bitmasks before head execution.

Do NOT reuse the post-head ledger union count.

Implement exactly one online statistic:

1. view active CPU masks as the same packed 32-bit vocabulary bitset;
2. OR active request masks into one persistent preallocated union buffer using NumPy bitwise OR/reduce;
3. popcount the union buffer with one fixed 256-entry uint8 lookup table over the buffer byte view;
4. divide by exact vocabulary size 151936;
5. apply strict RULE_U01.

Do not tune or compare alternative union algorithms.
Do not use Python sets / union over legal IDs as a second candidate.
Do not use GPU union.

The exact implementation must be frozen in:
`UNION_DISPATCH_CONTRACT.md`
before candidate timing.

Measure separately:
- union OR time
- popcount time
- branch time
- total union+dispatch CPU time.

These costs are included in the candidate head boundary.

No D2H is required for this implementation because masks are already CPU-resident.

---

# 3. Strong live baseline and mixed candidate

Use one persistent runner/process.

## B0_STRONG

- same accepted XGrammar mask path
- same accepted A0 dense-vendor head
- no union computation
- always A0
- keep the existing duplicate head-internal unpack/materialization unchanged.

## M1_RULE_U01

- exact same mask path
- run the new union+popcount+branch after masks are ready and immediately before head selection;
- if fraction <0.01, call accepted A3;
- else call accepted A0;
- keep accepted A0/A3 head code unchanged;
- do not refactor away duplicate unpack/materialization in only one arm;
- do not alter model/backbone.

Thus the only new work is:
- union statistic
- branch
- real per-step switching between already accepted A0/A3.

Persistent A0/A3 buffers coexist exactly as in parent.

---

# 4. Engineering correctness canary

Before formal timing use one old R81 fixture only as an engineering canary, not validation evidence.

Verify:
- online union count exactly matches parent post-head ledger union count for every retained timestep;
- RULE_U01 arm choice exactly matches the parent retrospective classification;
- no selected-token or stop-position changes between old all-A0 and new mixed path where semantics should match.

If union counts differ:
`R23G_UNION_SIGNAL_NOT_QUALIFIED`
STOP.

Do not tune implementation against timing.

---

# 5. New validation semantic qualification

For each final V0/V1/V2 B4 batch:

Run B0_STRONG and M1_RULE_U01 with timing ignored first.

Require:
- exact same selected token IDs at every aligned timestep between arms
- exact same stop positions
- same generated JSON text modulo no formatting normalization beyond exact token identity
- each of 12 outputs parses and satisfies its frozen schema
- no truncation at 128
- all grammar matchers terminate cleanly.

If mixed dispatch changes greedy semantics:
`R23G_MIXED_DISPATCH_SEMANTICS_NOT_QUALIFIED`
STOP.

Record:
- timestep count
- A0/A3 step counts
- union fraction per step
- transition count A0<->A3
- longest consecutive run per arm.

These are descriptive; do not alter RULE_U01.

---

# 6. Timing boundaries

No profiler.

All CUDA work holds the campaign lock.

Compilation/model loading/preallocation outside timing.

## Primary local boundary: LIVE_HEAD

For each generation timestep:

B0:
`mask ready -> A0 head result + selected token committed`

M1:
`mask ready -> union OR + popcount + RULE_U01 branch + selected A0/A3 head result + selected token committed`

This includes:
- union computation
- branch
- A0/A3 internal duplicate unpack/materialization
- A3 grouping/metadata/H2D
- A0 mask H2D
- head compute
- candidate reduction
- winner D2H/sync
- launch overhead
- arm-transition/cache effects.

Do not subtract union cost from candidate after measurement.

## Secondary boundary: COMPLETE_GENERATION

Use the same complete-generation wall boundary as accepted R81 where possible:
- same prompt/prefill policy
- full constrained continuation
- all backbone/head/matcher trajectory effects.

Complete generation is secondary for family value; it must not show a stable material regression if local response is promoted.

---

# 7. Formal timing protocol

For each V0/V1/V2 independently:

Arms:
- B0_STRONG
- M1_RULE_U01

Use:
- one persistent process
- 3 paired groups
- 2 warmup generations/arm/group
- 5 formal generations/arm/group
- alternate arm order by group
- reset exact prompts/grammar states each generation
- retain every sample.

No profiler during formal timing.

For each formal run record:
- complete generation wall time
- sum of LIVE_HEAD per-step time
- sum union OR/popcount/branch time
- A0/A3 step counts
- transition count
- all selected IDs / stop positions / schema validity.

Primary local response is **net LIVE_HEAD including union+dispatch**.

For each B4 batch/group compute paired median/MAD.

No universal 5% requirement.

A stable local positive requires:
1. all semantics qualify;
2. all 3 group medians for that batch favor M1;
3. median absolute LIVE_HEAD gap >3x larger-arm group-MAD estimate.

Cross-batch conclusion:
- require at least 2 of 3 B4 batches to have stable local positive;
- the remaining batch must not show a stable local regression.

Complete-generation safety:
- if 2 or more batches show stable complete-generation regression >2%, classify system regression even if head-local positive.
- otherwise complete generation is reported as positive/neutral/mixed without a universal benefit threshold.

The 2% value is a safety regression bound for this software validation, not a mechanism-promotion threshold.

---

# 8. Decision

## A. Live dispatch validates local net benefit
`R23G_R81_LIVE_DISPATCH_LOCAL_RESPONSE_PRESENT`

Requirements:
- cross-batch local rule above passes
- exact semantics
- no complete-generation safety regression.

Interpretation:
a fixed online-computable dense/direct-index software dispatch preserves a local head-region response after union and transition costs on unseen public structured-generation inputs.

This is a software result.
No hardware claim.

Optionally recommend production-quality software integration / broader workload validation.
Do not start architecture work from this alone.

## B. Union/dispatch cost removes the local benefit or candidate regresses
`R23G_R81_LIVE_DISPATCH_NOT_BENEFICIAL`

STOP R81 as a current optimization candidate.
Preserve old sparse-stratum positive as conditional evidence.

## C. Mixed
`R23G_R81_LIVE_DISPATCH_RESULT_MIXED`

STOP.
Do not tune threshold, union algorithm, batching or input grouping.

---

# 9. Scope limits

Forbidden:
- threshold sweep
- alternate union algorithms
- learned dispatch
- model change
- vocabulary change
- A3 kernel tuning
- batch-size sweep
- reusing old H0 as holdout
- NSYS/NCU/NVBit/SASS
- node174/Accel-Sim
- hardware mechanism
- task-accuracy claim.

The new public cohort is a structured-generation validation set, not a production distribution.

---

# 10. Resource/failure policy

All CUDA/JIT/generation:
`/data/c16/locks/c16_gpu_campaign.lock`

Persist lock acquire/release timestamps.

Dataset/model/raw -> node164 durable authority as appropriate.

Before any STOP save:
- dataset revision and row hashes
- prompts/schemas
- outputs/tokens
- first mismatch
- per-step union/arm trace
- raw timing
- environment.

---

# 11. Deliverables

Review pack:
`docs/vm_tlb/review_packs/AWMA_R23G_R81_LIVE_DISPATCH_109_V1/`

At minimum:
- README.md
- FINAL_DECISION.md
- PARENT_AUTHORITY.json
- PUBLIC_INPUT_AUTHORITY.json
- VALIDATION_COHORT.tsv
- UNION_DISPATCH_CONTRACT.md
- CANARY_UNION_VALIDATION.tsv
- SEMANTIC_QUALIFICATION.tsv
- PER_STEP_DISPATCH_TRACE.tsv
- FORMAL_LIVE_HEAD_TIMING.tsv
- FORMAL_COMPLETE_GENERATION_TIMING.tsv
- UNION_COST_SUMMARY.tsv
- RESPONSE_SUMMARY.md
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

---

# 12. Closure

Publish one exact commit.
Push/fetch-back verify SHA/tree.
Release GPU lock.
Terminate GPU processes.
Worktree clean.
STOP.

Final Chinese report must lead with:
1. exact public validation cohort authority;
2. exact union algorithm and measured cost;
3. real A0/A3 step/transition distribution;
4. net LIVE_HEAD response after union+dispatch;
5. complete-generation safety result;
6. whether the old sparse-stratum response survives in live mixed execution.

Do not lead with the old 7.17/4.37/6.09% retrospective numbers.
