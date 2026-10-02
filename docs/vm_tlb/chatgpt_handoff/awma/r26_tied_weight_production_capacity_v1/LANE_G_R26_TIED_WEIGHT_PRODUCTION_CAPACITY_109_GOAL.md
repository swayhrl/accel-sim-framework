# Codex Goal — Lane G / node109
## AWMA R26 tied-weight production integration and natural capacity boundary V1

Date: 2026-10-02 (Asia/Shanghai)

Repository: `swayhrl/accel-sim-framework`
Stage: `AWMA_R26_TIED_WEIGHT_PRODUCTION_CAPACITY_BOUNDARY_109_V1`
Handoff: `hrl/awma-r26-tied-weight-production-capacity-handoff-v1`
Execution: `hrl/awma-r26-tied-weight-production-capacity-109-v1`
Code/execution parent: `2581b6592e79691c4c3e57fe31a339eba9f6b7dd`
Accepted scientific review: `b2ba7f67a46e95ba45073c2a4deb54ee83a5401a`

One bounded solve-and-continue Goal. The user approved continuing from R25 to
production integration, real capacity usefulness, and limited multi-step checks.

---

# 0. Question and scope

R25 established two valid software paths:

- C1: compact lookup rows plus one full classifier/total gradient, beneficial
  relative to B0 on both accepted points.
- S2: compact lookup rows plus late tiled classifier gradient and immediate
  tilewise update, additional causal capacity savings on both points, with
  shape-dependent time effects.

R26 asks:

> In the same integrated tied-weight-only training loop on a 16GB RTX4080, can
> S2 make a physically larger batch executable than strong C1, with unchanged
> model, context, numerical contract, optimizer and trainable parameter set?

First establish the integrated component and a bounded 32-step consistency
check. Then search one natural complete-step memory boundary. A lower
TARGET_REGION peak alone is not a positive answer.

This is production-oriented integration validation, not a production release.
Only the shared input-embedding/lm_head W is trainable. Frozen backbone layers
still execute real forward and backward propagation to that W.

No all-parameter training, convergence, dataset/task-quality, diverse-batch,
universal LLM speedup, new model holdout, hardware, PPA or simulator claim.
R25 H0 has already been consumed; here it is an accepted integration test point.

---

# 1. Immutable authorities

## Model and input

Use only accepted `meta-llama/Llama-3.2-1B`:
- revision `4e20de362430cd3b72f300e6b0f18e50e7166e08`;
- source receipt SHA256
  `7694c95442cc7ff1d3fc8ed1104d5c0d6a50c3a17f779f402ef90669edeb7b47`;
- six receipt-listed payloads, 2,480,783,094 bytes;
- model.safetensors SHA256
  `68a2e4be76fa709455a60272fba8e512c02d81c46e6c671cc9449e374fd6809a`;
- config SHA256
  `bfb5d39c327ee5c3a65e3574596ff30b052a445cfc59a25bdf3b4c0c5a44f4d2`;
- BF16 tied W `[128256,2048]`.

Expected local model/source receipt paths are recorded in PARENT_AUTHORITY.json.
Verify all payload sizes/hashes, not only model.safetensors. Resolve a relocated
accepted replica by hashes rather than download or substitute weights.

Input is the pre-existing `ADOPTED_LLAMA_S0_T128_V1`:
`docs/vm_tlb/assets/c16/ai_workload_inputs/ADOPTED_LLAMA_S0_T128_V1/`.

- `frozen_token_ids.json` byte SHA256:
  `fc712eb0a158f0fe62231f7826feec3eaabfea51906ca6b1588a55ee81ae3624`;
- `ADOPTED_INPUT_RECEIPT.json` byte SHA256:
  `7e3c285f0417291fb53faccf222709c8824d94ee90ab887b718d6b8221c8bc0b`;
- input_ids B1 int64 tensor-byte SHA256:
  `29cc3577a6638646b8212f86e6ac73a8cbf7602dfce456de1780761285a76e27`;
- labels B1 int64 tensor-byte SHA256:
  `ba70169364a3494cfdd60f1d357dc059cbe074daad4b3610ba32cad5953bfd40`.

The adopted input is future-use authority frozen on 2026-09-14; it is not a
recovery of the lost historical S0 binding. Do not rewrite that history.

No download, re-tokenization, text replacement or alternate input.

## Source

Reuse the final R25 compact reducer, not its rejected BF16/FP32 index-add
engineering attempts. It remaps sorted unique IDs to the compact domain and
uses native `aten.embedding_dense_backward` with compact row count. It never
requests a vocabulary-size lookup gradient in C1/S2.

R25 source:
`util/vm_tlb/awma/r25_tied_weight_broader_validation/`.

Exact run_r25_campaign.py SHA256:
`599dcdf3326186fd84d2a2743269762311ca614b5c4e73dc1289c9f6fec646fa`.
accepted_r24_base.py SHA256:
`6526c54c74fc3ad1a327322d3221344436da217602ef76dd739fb31772832241`.

CCE original commit:
`3de376c106a1916bc5e1b619f9c77c87a461ee1c`.
Accepted first-store patch authority:
`ec1ccad7bbcead8853cd97840a2007d96f325aa3`.
Accepted first-store patch SHA256:
`e4156b6ec21a7c8696192c9a2ad3eb2196630c72373c64bc8395bc2ef12fda56`.

Reuse the final qualified R25 CCE source/patch and validate its frozen file
hashes in PARENT_AUTHORITY.json. If rebuilding the accepted source from the
R25 review-pack patch, verify patch SHA
`f4d58686c9fb9d617f15d89e25895b59eabd3204a3cdf8b6b51235cc64950c65`
and follow the accepted patch/source provenance. Do not double-apply patches
to a dirty CCE checkout or use a rejected intermediate implementation.

All arms use frozen meta:
`BLOCK_B=128, BLOCK_V=128, BLOCK_D=32, MM_BACK_BLOCK_D=64,
num_warps=4, num_stages=4, CCE_AUTOTUNE=0`.
No autotune, filtering, precision or kernel-parameter sweep.

---

# 2. Fixed training semantics and sole capacity dimension

- Only tied W trainable; assert every other parameter is frozen.
- Re-prove embedding/head exact data pointer and untyped-storage identity at
  initialization and after checkpoint load.
- Full frozen backbone: train mode, accepted SDPA attention, use_cache=False.
- Keep accepted runtime, dtype and backend behavior; record actual versions.
- No activation checkpointing, offload, quantization, compile-policy or attention
  policy change between arms or after boundary results.
- No clipping, GradScaler, scheduler, DDP/FSDP, LoRA, gradient accumulation,
  extra losses or extra W consumers.

Same explicit AdamW:
`lr=0.001, betas=(0.9,0.999), eps=1e-8, weight_decay=0.01`.
BF16 W, FP32 m/v, one shared tilewise consumer, one logical step increment and
one update per W element per complete batch.

Construct batch deterministically on CPU:

- base input `tokens[:-1]`, labels `tokens[1:]`, T=127;
- B copies of that sequence, materialized as actual `[B,127]` tensors;
- all-one attention mask; flatten hidden/labels in matching batch-major order;
- loss is mean over B*127 valid labels, with exactly matching gradient scale;
- record byte hashes and shapes for every tested B.

This increases physical execution batch, not unique training content. Say so
in the report. No claim about stochastic diversity or task quality.

Only B changes, in the integer interval [1,512]. Context, model, trainable set,
optimizer, tile rule and input content stay fixed. Increasing B is authorized
only to bracket capacity, not to hunt for faster S2 timing.

Create one common CPU start state from the accepted R25-style B1 bootstrap:
original accepted W, m=v=0, seed 25002, one B0 step, then freeze W/m/v/step=1
and CPU/CUDA RNG state. Verify against accepted start-state hashes if an exact
parent snapshot/receipt is available. Publish derivation/hashes either way.
All B probes, arms and formal runs consume this common post-bootstrap state;
do not bootstrap at a larger B or create arm-specific starts.

---

# 3. One integrated component with two policies

Implementation path:
`util/vm_tlb/awma/r26_tied_weight_production_capacity/`.

Provide a reusable component used by the campaign runner, not two independent
scientific scripts. Its explicit scope is a tied-weight-only training step.
A small API such as `train_step(input_ids, labels, policy="c1")` is sufficient.
Document caller responsibilities and unsupported training features.

- C1 is default within this new component.
- S2 requires explicit `policy="s2"` or equivalent capacity flag.
- Adoption by any existing unrelated workflow remains opt-in/default OFF.
- Diagnostic capture is separately controlled and OFF during boundary/timing.
- No automatic OOM retry, shape-dependent policy predictor or hidden fallback.
- Both policies share model forward, compact reducer and optimizer semantics.

## C1_COMPACT_FULL

Propagate classifier dH through the full backbone first. Accumulate compact
lookup rows, then generate exactly one full classifier/total gradient, merge
compact rows into it in-place, and apply the common AdamW consumer.

No full dense lookup W.grad. One full VxH classifier/total gradient is retained
only as long as required; no full-size clone/auxiliary shadow.

The accepted CCE full dW path may require its recorded FP32 accumulation
workspace before the final BF16 gradient. Account for it honestly. Do not
mislabel this workspace as an illicit clone, omit its bytes, or weaken C1 with
extra copies. No new full-workspace algorithm is authorized.

## S2_TILED

Same compact lookup reduction and delayed update. Generate classifier dW
vocabulary-row tile by tile using saved old-W forward hidden/LSE; merge compact
lookup rows; apply the same AdamW consumer to the tile and release temporaries.

No full VxH gradient or full VxH gradient-accumulation/shadow in boundary/formal
paths. Existing persistent W/m/v are optimizer state, not gradient shadows.

Tile rule remains 32 MiB FP32 gradient budget and a BLOCK_V multiple:
`floor(33554432/(2048*4)/128)*128 = 4096` rows; 32 tiles.
No sweep; correctly mask the last partial tile.

Complete all old-W backbone/dH/lookup consumers before updating any W tile.
Each later classifier tile uses untouched rows plus the original forward LSE
and hidden. No backward graph may read partially updated W.

## Real training loop lifetime

- No per-step gc.collect(), empty_cache(), cold model/JIT reload or state restore
  inside a continuous trajectory/capacity run.
- Release graph, hidden/LSE, compact collector and scratch references when no
  longer needed. Do not retain hidden.grad in non-diagnostic execution.
- Clearing transient state between steps is permitted; graph retention and
  accumulation across steps are forbidden.
- No persistent GPU copies of frozen start state, reference W/m/v, captured full
  gradients or comparison tensors.
- CPU start/checkpoints and chunked CPU comparison are allowed.
- No artificial ballast/reserved dummy allocation, artificial VRAM limit, cache
  reservation, coexistence GPU job or injected training state.
- No CPU optimizer/offload to make S2 fit.

Do not claim C1/S2 production readiness for arbitrary PyTorch autograd graphs.
Assert this Goal's trainable/consumer scope rather than silently ignoring
unsupported gradient contributors.

## Checkpoint contract

Expose explicit state save/load for W, FP32 m/v, logical step, RNG and identity/
policy metadata. Save CPU tensors; load into the existing tied storage.
Changing policy on the same valid state must not reset moments or the counter.
Unsupported model/state identity is rejected before CUDA execution.

---

# 4. Correctness before implementation freeze

Use fixed `rtol=atol=1e-2`, finite checks, exact step counter. No widening with
step count or batch size. Record max_abs, mean_abs, max_rel, cosine, shape/dtype
and first mismatch. Compare CPU tensors in bounded chunks.

1. B1 one-step: B0 accepted dense anchor, integrated C1 and integrated S2.
   Compare loss, dH, total gradient, updated W, m/v, step and next-forward loss.
2. B1 four-step: compare both integrated policies to B0, each with its own
   uninterrupted optimizer lineage.
3. B1 32 consecutive steps: C1 vs S2, identical start and batch, no step restore.
   Compare loss/next loss every step; full W/m/v at steps 1,4,8,16,32; counter
   exact every step. All checked observables must pass the same tolerance.
4. For each policy save its step-16 CPU state, create a fresh process, load it
   and execute its remaining 16 steps. Compare resumed final state/loss to the
   corresponding uninterrupted step-32 result under the same tolerance.
   Re-prove tied storage. Check state serialization contains no GPU tensor and
   no lost/duplicated step.
5. Minimal policy-switch test at B1: load the same C1 step-16 checkpoint into
   both modes, perform one step and compare the normal observables. This checks
   that capacity mode uses shared moments/step state; it is not another
   performance point.

B0 is qualification-only in R26; do not give it a new formal campaign.

Gradient reconstruction for qualification may use CPU storage and streaming
tile copies. Extra full GPU debug shadow is permitted only for the small B1
qualification if needed and is excluded from capacity/formal paths.

Trajectory indices 1..32 are relative to the post-bootstrap logical step=1.
At trajectory index k the optimizer counter must be 1+k: checkpoint index 16
contains logical step 17, and both uninterrupted/resumed index 32 end at step
33. Policy-switch qualification starts from logical step 17 and ends at 18.

Checkpoint comparisons may stream C1 snapshots from disk while S2 progresses.
Do not hold all snapshots simultaneously in RAM or copy them to GPU. Preserve
checkpoint hashes and enough raw state for independent recomputation.

Any real numerical/trajectory failure is
`R26_NUMERIC_OR_TRAJECTORY_NOT_QUALIFIED`, with first mismatch and STOP.
Ordinary implementation defects may be fixed before freeze and all affected
B1 gates rerun. Do not treat intrinsic accumulation-order drift as permission
to change the frozen reducer, optimizer, tolerance or input.

After all gates pass, write `IMPLEMENTATION_FREEZE.json` binding code, CCE
source, runtime/config, common start state, batch construction, tile rule,
decision classifier and contract hashes. Only then inspect capacity or formal
timing results. Behavior changes after freeze require STOP and review; CPU
report/path fixes may continue if they cannot change observations/classifiers.

The repeated batch trajectory is optimizer/dataflow consistency evidence,
not evidence of training quality or convergence.

---

# 5. Bounded natural-OOM capacity search

Use a fresh subprocess per (policy,B) trial, one GPU process at a time. Parent
or child must hold the shared flock throughout every CUDA/JIT operation.
An environment sentinel alone is not lock evidence.

Every trial:
1. load the same model and CPU-frozen start into one W/m/v set;
2. create the actual B batch; perform any deterministic JIT as required;
3. execute two training warmup steps then three further complete training steps,
   continuously without restore, each on the same B batch;
4. check finite losses, one update/step counter, no retained transient growth,
   and finite W/m/v via bounded checking;
5. capture complete-step and per-phase peaks, exit process and release context.

PASS requires all five actual complete steps and checks. Model/JIT/data setup
and the first cold step are part of feasibility: a first-step OOM is failure
even if a hypothetical prewarmed process might fit.

An OOM is only `torch.cuda.OutOfMemoryError` or an unambiguous recorded CUDA
allocation failure. Save request bytes, free/total VRAM, allocated/reserved,
OOM phase and full traceback. Generic crash, timeout, CPU kill, device fault,
numeric failure or a conflicting GPU job is not an OOM datapoint.

After OOM, serialize the CPU receipt, exit that subprocess and use a clean
process for the next trial. Do not retry with reduced precision, empty_cache
mid-step, offload, accumulation or changed semantics.

## Deterministic search per policy

Search C1, then S2, with identical algorithm:

- B=1,2,4,8,16,32,64,128,256,512, stopping exponential growth at the first OOM.
- If [L PASS, U OOM] is found, test floor((L+U)/2) and tighten the bracket
  until U=L+1.
- At most 19 distinct B trials per policy, excluding confirmation.
- If B=512 passes, record right-censored capacity: Bmax >=512. Do not expand.
- Preserve every attempted B and outcome; never remove a inconvenient point.

Report a measured monotone-bracket boundary, not an exhaustive proof over
every possible batch. If observed outcomes contradict monotonicity, or endpoint
confirmations disagree, classify `R26_CAPACITY_BOUNDARY_UNSTABLE` and STOP
the search; no extra tuning/repetitions to manufacture a clean boundary.

No formal performance comparisons are selected from this search. Feasibility
outcomes and allocation observations are used only to select endpoints.

## Confirmation and fixed witness selection

For each uncensored policy confirm its final L and L+1 in three fresh subprocesses
per endpoint, alternating policy order where endpoints coincide. PASS is 3/3
complete successes; OOM is 3/3 unambiguous OOMs. No majority vote.

For a censored endpoint confirm B=512 in three fresh processes.

Define:
- B_common = min(largest confirmed passing B of C1, S2).
- If C1 has a confirmed OOM at B_C1+1 and S2 passes at a larger B, select the
  sole positive witness B_witness = B_C1+1.
- If S2 alone has a confirmed OOM at B_S2+1 and C1 passes at a larger B, use
  that sole reverse witness.
- No searching within the gap for a more favorable witness.

Run both policies at the selected witness in three fresh processes each.
Each successful witness process executes the same two warmups + three complete
steps; the other policy must give 3/3 natural OOMs. Reuse exact matching endpoint
confirmations rather than repeating them unnecessarily.

Also verify B_common in three fresh processes per policy unless already
covered by endpoint/witness confirmations.

The primary positive observation is SAME B, SAME model/input/context/state,
C1 OOM, S2 PASS, with complete-step success rather than merely target-memory
savings. If both share the same forward/backbone OOM boundary, that is a valid
negative for useful batch extension at this configuration.

---

# 6. Selected-endpoint correctness and formal measurements

Before formal timing at B_common, do one C1-vs-S2 one-step numerical comparison
from the common start state. Compare the Section 4 observables with the same
tolerance. Stream gradient/dH/state capture to CPU without allocating any extra
full gradient/reference/FP32 W shadow on GPU; do not retain diagnostic graph
state. If diagnostics would themselves change endpoint feasibility, use direct
CPU streaming from existing tensors and component hooks, not a different B.

Numerical failure at B_common is a qualification STOP and not a performance
negative. The frozen candidate is not tuned at this endpoint.

A positive S2-only witness cannot have a matched full-batch C1 numerical run.
Report that limitation explicitly. Its evidence is runtime finite/step/arm
invariants at that batch, with numerical equivalence established at B1 and
B_common; do not invent a C1 reference at the OOM shape.

## One formal timing point

Only B_common, only C1/S2, after endpoint correctness and source freeze:
- 3 paired groups;
- per policy/group: 2 warmups + 5 formal samples;
- group orders: C1->S2, S2->C1, C1->S2;
- fresh policy/group processes allowed to remove cross-policy allocator history;
- same common CPU state restore outside timing before every sample;
- no extra GPU start-state copies;
- retain all 30 formal samples, including first group;
- no profiler, JIT compilation or allocator cache flushing in timed regions.

Record:
- TARGET_REGION: before classifier dH/backbone backward through AdamW completion,
  all compact preparation/merge/tiling/launch/sync costs included;
- COMPLETE_TRAIN_STEP: before real backbone + CCE forward through update
  completion, synchronized host wall time;
- start-state restore, model/data load, checkpoint I/O excluded identically.

Batch tensors are preloaded identically. COMPLETE_TRAIN_STEP is GPU training
compute-loop time, not end-to-end dataloader/deployment throughput.

For candidate S2 vs C1 per group:
- stable benefit if median(C1)-median(S2) > 3*max(MADs);
- stable regression if median(S2)-median(C1) > 3*max(MADs);
- otherwise MIXED.

Point class: BENEFIT if >=2 benefit groups and <2 regression groups;
REGRESSION if >=2 regression groups; MIXED otherwise.
Report all group directions and absolute time/percent. No universal 5% gate
and no tuning to eliminate R25's 0.13% direction.

## Memory and attribution

Primary capacity is full complete-step feasibility, including forward,
backbone backward, classifier/update, transitions and repeated-step state.

Record complete-step peak allocated/reserved, process/device footprint,
pre/post-step active bytes and peaks at forward/dH/backbone/classifier/update.
Phase observations may be from capacity trials; expensive observer captures
are not inserted only into one formal arm.

Record actual C1 full BF16 gradient and accepted FP32 dW workspace lifetimes,
S2 tile/consumer bytes and compact rows/index bytes. Distinguish W/m/v, runtime/
allocator reservations and gradient workspaces.

Arm identity must come from source plus actual allocation/buffer receipts, not
hard-coded labels alone. C1 retains one full total gradient and no dense lookup;
S2 has no full gradient/shadow; both use all dense optimizer state.

Use the measured OOM phase to identify whether classifier materialization,
backbone activations, initialization/JIT or another common allocation determines
the boundary. Do not infer boundary movement from subtracting nominal gradient
bytes. Allocator reduction is not DRAM traffic.

---

# 7. Exhaustive final outcomes

Qualification STOPs take precedence and preserve all completed evidence:
- R26_AUTHORITY_OR_SOURCE_NOT_QUALIFIED
- R26_TIED_STORAGE_OR_ARM_IDENTITY_NOT_QUALIFIED
- R26_NUMERIC_OR_TRAJECTORY_NOT_QUALIFIED
- R26_RESOURCE_OR_SCOPE_NOT_QUALIFIED

After qualification, use the following capacity decision in order:

1. `R26_CAPACITY_BOUNDARY_UNSTABLE`: conflicting endpoint outcomes or observed
   non-monotonicity prevents a reproducible bracket/witness.
2. `R26_INTEGRATED_BATCH_CAPACITY_EXTENSION_SUPPORTED`: same fixed positive
   witness has C1 OOM 3/3 and S2 complete PASS 3/3.
3. `R26_S2_BATCH_CAPACITY_REGRESSION`: fixed reverse witness has S2 OOM 3/3
   and C1 complete PASS 3/3.
4. `R26_CAPACITY_SEARCH_RIGHT_CENSORED`: no directional witness established
   and either search ends at the B=512 ceiling without natural OOM.
5. `R26_NO_BATCH_CAPACITY_EXTENSION`: both boundaries qualified/confirmed,
   no directional witness, and the same measured complete-step batch limit.

Unexpected unhandled decision state is a contract/implementation STOP; do not
invent a new favorable label after seeing results.

These are separate fields, not combined performance-positive labels:
- integration/32-step/resume qualification;
- C1/S2 passing bracket or censored lower bound;
- directional capacity witness;
- TARGET_REGION timing class;
- COMPLETE_TRAIN_STEP timing class;
- actual memory difference and OOM phase.

A positive capacity result may coexist with timing regression and remains a
capacity-oriented opt-in result. A negative boundary result does not erase R25
target-memory savings. A censored search is unobserved, not a negative.

The decision classifier and JSON constants are frozen before search. Never
modify their meaning after measurements.

---

# 8. Resource and engineering rules

Node109 only, one RTX4080; node164 for durable data. No node174 compute.
Before GPU work record process list, driver/device total VRAM, CPU/RAM/swap,
disk and node164 health. No interfering CUDA user process; do not kill unrelated
processes to make the contract true.

All CUDA/JIT/testing uses the shared flock:
`/data/c16/locks/c16_gpu_campaign.lock`.
Record PID/FD ownership and receipt, including fresh subprocesses. Do not hold
the GPU hostage waiting for unavailable scientific payload.

Bound campaign-created scratch/checkpoints to 64 GiB; publish raw/checkpoints
to node164 incrementally. Full checkpoint payload budget 40 GiB. Bound extra
CPU working set to 24 GiB and compare tensors in <=64 MiB CPU chunks.
Do not swap or keep duplicate model campaigns in RAM to satisfy these limits.
If current free resources do not support this bounded design, resource STOP;
do not remove required checks or switch algorithms.

A probe with no useful progress for five minutes is terminated with its logs
and marked timeout/UNKNOWN, not OOM. Reassess CPU-only whether it is an ordinary
launch/path bug; do not silently rerun formal measurements. Long useful
operations should report progress and retain receipts.

P2/P3 wrapper/derived files may be rebuilt deterministically from accepted
authority. Missing/unrecoverable scientific payload or changed identity is a
STOP. Small integration/API/lifetime fixes before freeze are solve-and-continue.
No separate repair Goal is needed.

No deployment, package publication or modification of existing production
workflows is part of this Goal; only the scoped component/docs in the execution
branch are authorized.

---

# 9. Forbidden expansion

No second model, second content input, longer context, diverse dataset,
optimizer/tile/attention/precision sweep, performance shape sweep, microbatch
accumulation, all-parameter training, convergence, offload, LoRA/MoE, NCU/NSYS/
NVBit/SASS, tracing, node174/Accel-Sim, hardware/PPA, adaptive dispatch, artificial
memory pressure, old-Goal restart or hidden OOM fallback.

Do not use H0 timing to tune the implementation. Do not describe repeated
copies of the accepted sequence as an independent data holdout.

---

# 10. Deliverables and ownership

Review pack:
`docs/vm_tlb/review_packs/AWMA_R26_TIED_WEIGHT_PRODUCTION_CAPACITY_BOUNDARY_109_V1/`.

At minimum:
- README.md, FINAL_DECISION.md;
- PARENT_AUTHORITY.json, MODEL_INPUT_AUTHORITY.json;
- TRAINING_CONTRACT.json, OPTIMIZER_CONTRACT.json, COMMON_START_STATE.json;
- IMPLEMENTATION_FREEZE.json and exact component/source hashes;
- COMPONENT_API_AND_LIMITS.md, INTEGRATION_VALIDATION.json;
- ONE_STEP_NUMERICAL_QUALIFICATION.tsv, FOUR_STEP_ANCHOR_QUALIFICATION.tsv;
- TRAJECTORY_32_STEP.tsv, CHECKPOINT_RESUME_QUALIFICATION.tsv;
- POLICY_SWITCH_QUALIFICATION.tsv, FIRST_MISMATCH.json;
- BATCH_INPUT_BINDINGS.tsv;
- CAPACITY_SEARCH_LOG.tsv, CAPACITY_ENDPOINT_CONFIRMATIONS.tsv;
- CAPACITY_WITNESS.json, SELECTED_ENDPOINT_NUMERICAL_QUALIFICATION.tsv;
- MEMORY_ACCOUNTING.tsv, BUFFER_LIFETIME_RECEIPTS.json;
- FORMAL_TARGET_TIMING.tsv, FORMAL_COMPLETE_TRAIN_STEP_TIMING.tsv;
- GROUP_RESPONSE_SUMMARY.tsv, CAPACITY_AND_TIMING_DECISION.json;
- RESOURCE_LOCK_RECEIPTS.json, NODE164_PUBLICATION.json;
- RAW_DATA_INDEX.tsv, SHA256SUMS, ENGINEERING_ATTEMPTS.md.

Include exact commands, exit codes, source/runtime/config/input identity,
changes/diff summary and source/diagnostic/formal distinctions. Large tensors
and checkpoints are node164 raw; Git stores code and compact evidence only.

Reporting path assigned to this lane:
`docs/vm_tlb/codex_handoff/awma/r26_tied_weight_production_capacity_v1/LANE_G_FINAL_REPORT.md`.

ChatGPT owns this handoff directory. Codex may read it but not rewrite its
frozen contract. Codex owns the new util path, assigned report and review pack.
Do not mutate R25 files, accepted packs or historical root M4 state.

---

# 11. Closure and final Chinese report

Complete required scoped checks, git diff --check and explicit-path staging.
Commit and push the execution branch. Fetch back and verify exact remote SHA/
tree. Verify node164 archive/manifest/checkpoint hashes. End campaign CUDA
processes, release GPU lock, verify clean worktree, then STOP.

Do not automatically start a later stage, broaden a censored search or deploy
the component.

Chinese final report should lead with:
1. integrated API/default C1/opt-in S2 and supported training scope;
2. exact model/input plus replicated-batch meaning;
3. B1 one/four/32-step, checkpoint resume and policy-switch qualification;
4. actual C1 and S2 complete-step brackets, all OOM phases and ceiling censoring;
5. whether SAME B C1 OOM/S2 PASS was confirmed 3/3;
6. whole-step memory versus target-memory results and whether savings matter
   at the determining peak;
7. common-batch TARGET_REGION and COMPLETE_TRAIN_STEP timing separately;
8. remaining limits and whether capacity opt-in integration deserves follow-up.

Do not lead with R24/R25 nominal savings or claim full training quality.
