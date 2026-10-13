# Codex Goal — Lane G / node109
## AWMA R27R3: numerical attribution and conditional varied-batch capacity

Date: 2026-10-13 (Asia/Shanghai)
Stage: `AWMA_R27R3_NUMERIC_ATTRIBUTION_CONDITIONAL_CAPACITY_109_V1`
Repository: `swayhrl/accel-sim-framework`
Handoff: `hrl/awma-r27r3-numeric-attribution-capacity-handoff-v1`
Execution: `hrl/awma-r27r3-numeric-attribution-capacity-109-v1`

Closed source parent: R27R2 execution `ba73fa0bacf3db09f44d8ad421a0a36f56645898`, tree `6988b03184c909123b6a8dfae082e07202cd808b`.

**This is one complete, conditional, solve-and-continue Goal.** No separate GPU rounds for diagnostic, repair, four-step qualification, capacity, 32-step/resume or publication. A passing gate permits the next gate automatically; a genuine identity/scientific/precision/liveness/resource failure is terminal for this execution. Never downgrade a failure into engineering PASS or run capacity speculatively after failed numerical qualification.

## 0. Authority and objective

Read, in order:
1. `START_HERE.md`;
2. `ACCEPTED_R27R2_REVIEW.md`;
3. `PARENT_DATA_AUTHORITY.json`;
4. this Goal;
5. `R27R3_EXPERIMENT_CONTRACT.json`;
6. repository `AGENTS.md`.

The launch message supplies exact handoff HEAD/tree. Verify it, then create a **fresh execution worktree** at the handoff HEAD, not the R27R2 execution commit directly. Do not edit/amend/rebase/restart closed R26/R27/R27R1/R27R2 execution branches or their raw. The R27R3 candidate lives under `util/vm_tlb/awma/r27r3_numeric_attribution/`, with separate report/review/raw folders. Treat old R26 B0 as a frozen reference, not a weak baseline to change.

**Question 1:** Why do the B1 C1/S2 complete BF16 tied-W gradients differ from B0 on the fixed varied stream? Is this a reproducible numerical-order phenomenon, a reference repeatability problem or a correctable semantic/implementation defect?

**Question 2 (conditional):** If and only if an evidence-backed, one-concept repair preserves the intended computation and the unchanged numerical contract passes, does a natural varied-input five-step C1/S2 capacity difference remain, and can a positive S2 witness survive 32-step/resume?

No claim about convergence, full-parameter training, general memory savings, formal throughput, production or hardware follows from this Goal.

## Gate A — CPU-only inherited authority and read-only analysis

1. Verify the closed R27R2 exact commit/tree and its accepted 18-file review pack. Reuse its qualified 6,357,543-byte parquet, its 33×128×128 CPU int64 bank and R26 common checkpoint. Verify the actual **consumed** file bytes/size/SHA against `PARENT_DATA_AUTHORITY.json`. Do not redownload/re-tokenize/repack the seed, change bank offset/order, derive another common bootstrap, or repeat entire 95-item R27R2 / 207-item R27 historical audits without a specific discrepancy.
2. Verify model/revision/six payload hashes, accepted tokenizer, CCE source/meta, R26 component and R27R2 source identities from accepted receipts and actual files needed for this task. R26 W/m/v/RNG/step=1 must remain unchanged. Record finite provenance and all identities in a compact `PARENT_DATA_RECHECK.json`.
3. Read R27R2 `B1_NUMERICAL_QUALIFICATION.json/tsv`, `FIRST_MISMATCH.json`, fresh checkpoint/switch result, `RAW_DATA_INDEX.tsv`, and numerical comparator. Determine **whether actual raw per-element tensors survived**. Existing summary max/mean/cosine cannot identify any exact violating coordinate. If absent, record that fact; do not reconstruct fabricated raw.
4. Read frozen R26 B0 vs C1/S2 and `R25CompactEmbedding` source for possible differences in native `embedding_dense_backward`, sorted `unique`/inverse, compact reducer, `index_add_` and CCE classifier derivative. Produce a **pre-diagnostic hypothesis and discriminator table** before new GPU observations. Keep hypotheses separate from accepted facts.
5. The previous `B1_NUMERICAL_QUALIFICATION.json` has 8/8 total-gradient FAILs (C1 and S2 on four steps), first C1 step-1 max_abs 0.09375 and C1 step-4 FP32 m max_abs ≈0.01464477; loss/dH/most W/v pass. It is an existing discovery sample, **not** an independent holdout or a license to adjust tolerance.
6. If the consumed seed/bank/checkpoint/source cannot be independently identity-checked from accepted payload, STOP `R27R3_PARENT_OR_DATA_NOT_QUALIFIED`. Fix deterministically reconstructible wrapper/index provenance only when surviving payload/algorithm suffice; mark DERIVED/RECONSTRUCTED. No silent replacement of scientific bytes.

Gate A needs no GPU lock or CUDA/JIT.

## Gate B — bounded B1 native numerical attribution, not a performance sweep

Predeclare the probes and decision criteria before running. Primary input: **bank step index k=0, physical B=1**. If necessary to distinguish the reported step-4 FP32 m propagation, permit only bank k=3 as a second focused diagnostic, not a new input search. Use the exact R26 common CPU start, accepted BF16 tied W and FP32 AdamW, original frozen CCE/attention/backend, and the same tokenizer/bank.

All CUDA/JIT—including canaries, local gradient probes and Triton compilation—requires a real `flock` on `/data/c16/locks/c16_gpu_campaign.lock` for the **entire** GPU process/subprocess lifetime. Inspect GPU occupancy/processes first. Do not run competing campaigns. Keep diagnostic overhead **out** of later capacity trials.

### B1. Check B0 reference repeatability first

Execute **two fresh-process B0 one-step reproductions** of bank k=0 from the **same exact CPU start/RNG**, with same inputs and all environmental identities. Compare loss, dH, complete BF16 total gradient, updated W/m/v, counters and next-bank loss using the existing elementwise rule: `abs(diff) <= 0.01 + 0.01*abs(B0_ref)`; dtype/shape/finite and tie integrity required. Preserve raw mismatch proof.

If two B0 executions disagree beyond that contract, STOP `R27R3_B0_REFERENCE_NOT_REPEATABLE`. A merely nondeterministic baseline cannot serve to attribute C1/S2 differences. Do not repeat B0 until a favorable pair appears, change seeds or forcibly enable a different deterministic algorithm in the formal B0. A distinct deterministic/high-precision computation may be **diagnostic-only** and clearly marked.

### B2. Separate lookup, classifier and merge

If B0 repeatable, perform at most **six pre-correction diagnostic GPU processes total**, inclusive of the two B0 controls, with only the fixed B1 scope (k=0; optional k=3). A process may contain bounded sub-probes; avoid repeated model reload when within the same valid process and without state contamination.

Distinguish in a controlled manner:
- whether B0/C1/S2 forward hidden states and classifier `dH` differ before lookup backward;
- native B0 dense embedding lookup gradient versus C1/S2 compact sorted-unique/inverse-remapped lookup gradient **scattered back to original vocabulary rows**;
- CCE classifier gradient with matched hidden/lse/state;
- full BF16 total gradient **after** the lookup+classifier merge, including accumulation order;
- effects on updated FP32 first moment and W after the same optimizer step;
- a **matched-dH** lookup-backward control to isolate the embedding/reducer from upstream differences;
- uniqueness/duplication multiplicity of selected token IDs, touched versus untouched rows, and gradient behavior by token row.

Use bounded CPU captures/chunked comparisons (≤64 MiB chunks), not unlimited extra full-V×H GPU shadows. At least:
- exact count and fraction of elements violating `atol+rtol*abs(reference)`;
- first 32 violating flattened coordinates in canonical row-major order and 32 with largest **excess above tolerance**, actual B0/candidate values, allowed bound and absolute difference;
- indexed vocabulary rows, whether they were in input/labels, and token-frequency histogram including duplicate input tokens;
- max/mean absolute difference and cosine **only as secondary descriptors**;
- per-component identity, path, dtype, scaling and accumulation/rounding status.

No inference of numeric correctness from a large cosine or tiny mean. Do not confuse enormous `max_rel` caused by near-zero denominators with a calibrated global relative error.

Use a small directed CPU/GPU fixture with known unique/repeated token IDs only to check reduction/remapping logic; fixture results are diagnostics, **not** natural-batch evidence.

Attribution outcome must distinguish: `REFERENCE_VARIABILITY`, `LOOKUP_REDUCTION_OR_MERGE`, `CCE_CLASSIFIER_PATH`, `OPTIMIZER_OR_CHECKPOINT`, `OTHER_LOCALIZED`, and `UNRESOLVED`. A label requires supporting component comparisons and first discrepancy; do not invent a mechanism from symptoms.

If no stable root cause or checkable improvement route is established within this bounded diagnostic, STOP `R27R3_NUMERIC_CAUSE_UNRESOLVED`. Do not enlarge the GPU grid to search for a convenient PASS.

## Gate C — one evidence-driven correction, conditional

Only if Gate B has localized a defensible semantic/implementation defect or a numerical-order implementation choice with a **bounded equivalent** correction is there authority to create **one** targeted candidate. One distinct root-cause correction only (including its directly necessary support code/tests), with full patch/behavior/provenance record.

Requirements:
- preserve the identical tied-W mathematical operation, total-gradient contributions, loss, reduction scaling, hidden/backbone semantics, optimizer W/m/v and step order;
- preserve model/revision, R26 common start, exact bank/token IDs/labels, BF16 tied weight and FP32 moments, CCE meta and attention, `ROWS_PER_TILE=4096`;
- retain C1 default and S2 explicit opt-in, no policy fallback;
- preserve the exact input/output embedding storage tie;
- C1 may still materialize **one** full V×H total classifier/gradient tensor as in the accepted design; S2 must **not** create a full V×H total-gradient/lookup-gradient GPU shadow or silently turn into B0;
- quantify new allocations, staging/synchronization/extra reduction work and any application-bound overhead if the correction changes resources; no free precision or unlimited buffering;
- preserve historical R26 and R27R2 code unchanged; keep diagnostic mode and corrected candidate separate. Default behavior outside the expressly enabled new candidate remains the historical accepted path;
- no tuning of B0 baseline, threshold, dataset, batch, optimizer, tile, precision, allocator, CCE meta, model or environment to force a pass.

A high-precision/deterministic reduction is permitted as an isolated **diagnostic reference**. It is not automatic authority for a higher-precision production S2 path. If the only way to pass B0 equivalence adds a prohibited S2 full tensor, alters the numerical contract, or sacrifices the intended resource distinction, STOP and report cost/why.

Before rerunning B1, pass directed correctness tests for unique/duplicate tokens, inverse mapping, exactly-once gradient contributions, tie identity and C1/S2 resource constraints. If the correction cannot be justified under these rules, STOP `R27R3_CORRECTION_NOT_QUALIFIED`.

**No second scientific correction** and no parameter/precision grid after seeing results. Ordinary syntax/import/receipt/launch problems that preserve frozen scientific semantics can be fixed within this same Goal before freeze and the affected tests repeated.

## Gate D — re-run unchanged formal B1 four-step numerical qualification

Only after Gate C passes. This is a **new candidate** being evaluated under the **original, unchanged** numerical criteria, not a retroactive PASS for R27R2.

Run from identical migrated R26 starts and frozen bank:
- B=1, bank steps k=0,1,2,3 for B0/C1/S2;
- per step: loss, dH, complete BF16 total gradient, W, FP32 m/v, exact counter, cursor, next-bank forward loss, finite/tied state;
- `rtol=atol=1e-2` elementwise, not statistical averages;
- fresh-process checkpoint restore and C1↔S2 policy switch, with moments/RNG/step/cursor unchanged;
- record first mismatch with real values and per-coordinate bound; no unreported failure.

The baseline B0 remains the accepted unchanged native path. C1/S2 must BOTH pass on ALL four varied steps: eight gradient comparisons plus every other required check. A passing C1-vs-S2 comparison by itself is insufficient.

Run this behind a fail-closed dispatcher: `set -euo pipefail`, capture pipeline statuses, and require the written machine result to explicitly say PASS. Never let `tee` or a later checkpoint/switch PASS mask earlier numeric FAIL. **Do not run Gate E if any Gate D condition fails**. Emit `R27R3_NUMERIC_OR_STATE_NOT_QUALIFIED` and STOP.

Even after PASS, this is not an independent holdout because these same four steps were already used in diagnosis. State the limitation. Next allow implementation freeze, not immediate claims of general numerical equivalence.

## Gate E — freeze before any capacity observation; then natural bounded search

Only after A–D PASS:
- persist `IMPLEMENTATION_FREEZE.json` with exact corrected source hashes, delta against R27R2/R26, opted-in candidate switches, model, CCE/meta, environment, tokenizer/raw bank/common checkpoint, tile, optimizer, input rules, correctness criteria, memory-path guardrails, search/decision classifier and lock/resource contract;
- assert freeze timestamp and hashes **precede** any capacity trial;
- turn off diagnostics, full-gradient CPU capture/profiling and baseline-repeatability scaffolding for capacity;
- after freeze, scientific input/GPU behavior/decision classifier/precision/tolerance/optimizer/allocator change → STOP/review, not in-place rescue.

The capacity protocol is unchanged from R27R2:

1. Each (policy,B) trial runs in a **fresh process** from the identical R26 CPU start; first five distinct bank step indices 0..4; 2 designated warmups followed by 3 further complete training steps with no restore between steps. Complete frozen backbone forward + dH backward, finite W/m/v/loss/counter, unique input hash per step, graph/quiescence, active allocation and OOM phase/request/traceback are mandatory.
2. Search C1 then S2, start B64, on PASS probe B96 then B128 until OOM or right censor; on B64 OOM probe B32/B16/B8/B4/B2/B1 until PASS, then integer floor midpoint to adjacent PASS/OOM. `1<=B<=128`, maximum 12 distinct search B per policy.
3. Only genuine CUDA OOM is OOM; timeout, CPU kill, ordinary crash, bad numerical state or competing load is UNKNOWN/non-qualification. Monotonicity and no artificial memory pressure are mandatory. B128 PASS is **right censored** and cannot be extrapolated.
4. Each passing boundary and adjacent OOM must confirm **3/3 in fresh processes** per policy/B; no majority vote, no repeated trials until a favorable answer. Reuse only genuinely identical earlier confirmations (same policy, B, bank, source, start and frozen environment); never reuse evidence across different policies as equivalent.
5. Define `B_common=min(C1 largest confirmed PASS, S2 largest confirmed PASS)`. Forward capacity witness requires C1 3/3 OOM at its largest confirmed PASS+1 and S2 3/3 PASS at **that same B**, `B_witness`.
6. If equal, S2 regression, right-censored without a proved witness, UNKNOWN or nonmonotone, publish corresponding terminal result; **do not** run F/G or add a second input/allocator tweak.
7. Per-step latency/memory only descriptive feasibility diagnostics. **No formal timing campaign or speedup claim.**

## Gate F — positive-only 32-step and recovery

Only after a qualified same-B forward witness in E:

1. At B_common, one-step C1/S2 loss, dH, full total gradient and W/m/v numerical pairing from the identical common start, unchanged `1e-2` and bounded capture.
2. Run C1 and S2 for 32 consecutive distinct bank steps 0..31 with identical initial W/m/v/RNG; per-step loss, next-bank loss, finite state, step/cursor, hashes, graph lifetime and memory; full W/m/v checks at trajectory indices 1,4,8,16,32.
3. Fresh-process resume each policy from its own step-16 CPU checkpoint for steps 16..31; compare final step33/cursor32/W/m/v/loss. From the C1 step-16 checkpoint switch the next step between C1 and S2, no counter/moment reset.
4. Independently run S2 at B_witness for 32 steps with state/memory liveness and fresh-process step-16 resume. Because C1 OOMs at B_witness, **do not invent** a matched full witness-B C1 numerical trajectory.
5. If F fails, retain the five-step observation **only** and classify `R27R3_EXTENDED_CAPACITY_TRAJECTORY_NOT_QUALIFIED`; no shrinking batch/tuning allocator to rescue.
6. If F passes, label `R27R3_VARIED_BATCH_CAPACITY_EXTENSION_32_STEP_SUPPORTED` **only** for this one Llama revision, the fixed WikiText-2 train bank, this BF16 tied-W-only protocol, RTX4080 configuration and *new corrected* implementation. R26 repeated-sequence claim remains separate.

## Gate G — conditional attribution, not another campaign

Only if E/F positive and **remaining allocator mechanism** cannot be explained from existing receipts: at most one bounded fresh-process C1/S2 diagnostic pair at B_witness with PyTorch allocator history/`memory_stats`. It is diagnostic-only, not endpoint confirmation, timing sample or permission to change allocator. Skip if unnecessary.

## Resource and publication

- Only node109 Lane G is authorized for CUDA under the actual `/data/c16/locks/c16_gpu_campaign.lock` flock; one GPU campaign process at a time. Do not run profiler or GPU tasks from other lanes. Avoid oversubscription; first inspect CPU/RAM/swap/I/O/node164 free space and mounted data authority.
- CPU-only hash/parser/receipt and independent bounded comparisons may parallelize when paths are read-only or outputs isolated. No parallel mutation of checkpoints/manifests; no speculative capacity runs before numeric gate PASS.
- All new mechanics/code are isolated and **opt-in**. No modification of old R26/R27/R27R1/R27R2 worktrees, source, checkpoints or science receipts.
- Predeclare decision rules before observations; preserve ALL diagnostic FAIL, first mismatch, unsupported and negative results. Do not choose a favorable run.
- Node164 is durable authority for new raw, detailed attribution, bank/seed/reference links and checkpoints; Git only compact code, exact manifest/index/review pack.
- Publish `docs/vm_tlb/review_packs/AWMA_R27R3_NUMERIC_ATTRIBUTION_CONDITIONAL_CAPACITY_109_V1/` including `README.md`, `PARENT_RECHECK.json`, `B0_REPEATABILITY.json`, `NUMERIC_ATTRIBUTION.json`, failure-coordinate/component tables and provenance, `CORRECTION_DECISION.json` (if eligible), `B1_REQUALIFICATION.json` (if reached), `IMPLEMENTATION_FREEZE.json` (if reached), every capacity trial/endpoint (if reached), 32-step/resume (if reached), resource/lock receipts, `RAW_DATA_INDEX.tsv`, `SHA256SUMS`, `FINAL_DECISION.json/md`, validation and open issues. The CPU finalizer must **derive** observed labels/indices rather than hardcode outcome-specific numbers.
- Final report: `docs/vm_tlb/codex_handoff/awma/r27r3_numeric_attribution_capacity_v1/LANE_G_FINAL_REPORT.md`.
- Check scripts/tests, `git diff --check`, explicit-path stage (never `git add .` / `git add -A`), commit/push, bounded timeout and SSH transport fallback if needed, **fetch back exact commit/tree**, clean worktree, remote node164 SHA/size readback, no campaign CUDA processes, lock released. Transport failures do not authorize re-running science or rewriting an existing scientific commit.
- STOP after one review pack/execution commit, whether negative or positive. Do **not** automatically open next Goal, default-on S2, production, formal timing/profiler, node174/Accel-Sim, hardware/PPA, second corpus/model, full-parameter training or deployment.

### Scientific outcome distinctions

`PARENT_OR_DATA_NOT_QUALIFIED` ≠ `B0_REFERENCE_NOT_REPEATABLE` ≠ `NUMERIC_CAUSE_UNRESOLVED` ≠ `CORRECTION_NOT_QUALIFIED` ≠ `NUMERIC_OR_STATE_NOT_QUALIFIED`. Only successful **new candidate four-step** numerical qualification opens capacity; an aggregate mean/cosine or C1↔S2 equality is not sufficient. Capacity negative/regressed/censored, five-step-only positive, and full 32-step positive are separate scoped conclusions. All old R26–R27R2 outcomes remain unchanged.
