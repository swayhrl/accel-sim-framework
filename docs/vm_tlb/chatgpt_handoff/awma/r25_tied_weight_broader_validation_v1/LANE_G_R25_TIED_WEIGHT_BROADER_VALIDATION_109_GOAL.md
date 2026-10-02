# Codex Goal — Lane G / node109
## AWMA R25 tied-weight broader software validation V1

Date: 2026-10-02

Repository:
`swayhrl/accel-sim-framework`

Stage:
`AWMA_R25_TIED_WEIGHT_BROADER_SOFTWARE_VALIDATION_109_V1`

Execution branch to create:
`hrl/awma-r25-tied-weight-broader-validation-109-v1`

Handoff branch:
`hrl/awma-r25-tied-weight-broader-validation-handoff-v1`

Scientific parent:
`b73ffd2320b5ee952d90625089b2ec31eb25eab4`

R24 execution authority:
`41795817a5b86959c86cc36c6973f292be33c6a6`

One bounded solve-and-continue Goal.
Ordinary engineering issues are solved inside this Goal.
STOP only for scientific identity, authority, numerical-contract, resource, or scope changes.

---

# 0. Purpose and claim boundary

R24 established one discovery point:
- S2 removed formal full VxH tied-gradient materialization;
- large target-region peak-memory reduction was measured;
- S2 was stably faster than S1;
- S2 vs B0 timing was mixed/near-neutral.

R25 asks two narrower questions:

1. Does the S2 capacity result remain after replacing R24's weaker dense-lookup comparator with a stronger **one-full-buffer** software comparator?
2. Does the capacity result and acceptable timing behavior survive one **independent tied-weight model/input performance holdout**?

This is broader software/dataflow validation only.

No claim of:
- training convergence;
- full-model all-parameter training speedup;
- general LLM universality;
- hardware residual;
- hardware/PPA;
- node174/Accel-Sim.

Time and capacity are separate outcomes.

---

# 1. Frozen authorities

## 1.1 D0 — Qwen discovery/calibration point

Reuse exactly the R24 model/input identity:

Model:
- `Qwen/Qwen2.5-0.5B-Instruct`
- revision `7ae557604adf67be50417f59c2c2f167def9a775`
- model SHA256
  `fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe`
- expected tied W: BF16 `[151936,896]`

Input:
- `ACCEPTED_R101_TRAIN_DISCOVERY_256`
- token file:
  `/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927/raw/TRAIN_DISCOVERY_256.json`
- token file SHA256:
  `000404d45d04a183379bd7ffa27efdfc196a08f4f97f2003cabad705ab8e2e6d`
- 256 exact tokens
- `input_ids=tokens[:-1]`, 255 positions
- input_ids SHA256:
  `f59446f6a177507048cad5e272d03b1d910337bf0e626f4ce78aa8c244837a1e`
- `labels=tokens[1:]`
- labels SHA256:
  `c89b22206d04b19d9a018e25c732aa5b1acf01b7b1ca18579bfc9ac4e1214f3a`

Runtime must re-prove tied pointer/storage identity.

## 1.2 H0 — independent performance holdout

Use only the already accepted C16 Llama asset:

- model ID: `meta-llama/Llama-3.2-1B`
- accepted revision:
  `4e20de362430cd3b72f300e6b0f18e50e7166e08`
- expected active replica:
  `/data/c16/models/.incoming/Llama-3.2-1B/4e20de362430cd3b72f300e6b0f18e50e7166e08`
- expected source receipt:
  `/data/c16/models/.provenance/R1_LLAMA3P2_1B_ASSET_RECEIPT.json`
- expected source-receipt SHA256:
  `7694c95442cc7ff1d3fc8ed1104d5c0d6a50c3a17f779f402ef90669edeb7b47`
- the receipt is expected to bind six payloads totaling 2,480,783,094 bytes.

Before any GPU performance work:
- verify the source receipt exact SHA;
- verify all receipt-listed payload size/SHA values;
- record model/config/tokenizer identities into `H0_MODEL_AUTHORITY.json`;
- read the accepted local config and record V/H/dtype/tie_word_embeddings;
- runtime must prove input embedding and output head share exact data pointer and
  untyped-storage pointer.

Do not use public web/config copies as execution authority.

### H0 input

Use the already accepted C16 frozen input identity:
`S0 / B1 / T128 / Decode4 / TEXT`.

Resolve its exact accepted binding/receipt from existing 109/node164 authority.
The accepted token IDs must already exist.

Required:
- unique authoritative binding;
- exact token-ID payload;
- binding/receipt/hash closure;
- no re-tokenization;
- no alternate TEXT;
- no newly downloaded dataset/input.

Construct the training microstep only by shifting the already-frozen T128 token IDs:
- `input_ids=tokens[:-1]`
- `labels=tokens[1:]`
- expected T=127 after shift.

Write:
- `H0_INPUT_AUTHORITY.json`
- exact source path(s);
- token payload SHA;
- input_ids SHA;
- labels SHA.

If the exact accepted H0 model or input authority cannot be uniquely resolved:
`R25_HOLDOUT_AUTHORITY_NOT_QUALIFIED`
STOP before formal GPU work.

Do not silently substitute another Llama replica, model, revision, tokenizer or input.

---

# 2. Source baseline

Use the same CCE source lineage as R24:
- repository `apple-aiml-research/ml-cross-entropy`
- source commit `3de376c106a1916bc5e1b619f9c77c87a461ee1c`
- accepted first-store patch authority:
  `ec1ccad7bbcead8853cd97840a2007d96f325aa3`
- accepted patch SHA256:
  `e4156b6ec21a7c8696192c9a2ad3eb2196630c72373c64bc8395bc2ef12fda56`

For D0:
- CCE meta must match the accepted R24/CCE values exactly.

For H0:
- keep `CCE_AUTOTUNE=0`;
- resolve the deterministic CCE configuration for the exact H0 shape before
  candidate performance timing;
- record it in `POINT_CONTRACTS.json`;
- do not tune or sweep it;
- all arms at H0 use the same frozen meta.

If first-store/dH/dW paths are not numerically qualified at H0:
`R25_HOLDOUT_NUMERIC_NOT_QUALIFIED`
STOP.
This is not a performance negative.

---

# 3. One shared optimizer contract

Only the tied W is trainable for both points.
All other model parameters are frozen but the full backbone remains in the
gradient path to the input embedding.

Use one explicit AdamW semantic contract across both points:
- same lr;
- same betas;
- same eps;
- same weight_decay;
- BF16 W storage;
- FP32 m/v;
- same tilewise consumer implementation;
- one update per W element per microstep.

Freeze exact values before any candidate performance timing.

No:
- gradient clipping;
- GradScaler;
- microbatch accumulation;
- DDP/FSDP;
- AMSGrad;
- foreach/fused optimizer variation;
- arm-specific precision or hyperparameters.

For each point bootstrap once, then freeze the post-bootstrap W/m/v/step/RNG state.

### Harness snapshot policy

Unlike R24, frozen restore snapshots must live on CPU/pinned CPU memory rather
than duplicate W/m/v persistently on GPU.

Reason:
- remove harness-only GPU memory from allocator comparison;
- keep H0 within bounded RTX4080 capacity;
- restore copies are outside measured regions.

Record CPU snapshot bytes.
Do not count them as GPU peak memory.

Every arm/run starts from the same point-specific frozen state.

---

# 4. Three arms

## B0_DENSE_STRONG

Historical/causal anchor.

- accepted first-store CCE classifier dW path;
- normal dense input-embedding backward;
- full classifier contribution + full dense lookup contribution;
- merge;
- same AdamW consumer.

This arm is not the only production comparator.

## C1_COMPACT_FULL — primary strong software comparator

Purpose:
remove the obvious second full dense lookup-gradient buffer while still retaining
one complete VxH classifier/total gradient.

Required behavior:
1. forward uses the exact tied W and model path;
2. embedding backward accumulates only sorted/unique lookup rows plus their values;
3. do not materialize dense lookup W.grad;
4. after dH propagates through the complete frozen backbone, generate one full
   classifier dW;
5. merge the compact lookup rows directly into that full classifier/total dW in-place;
6. apply the identical AdamW consumer once;
7. release the full dW.

Formal C1 must have:
- no full dense lookup gradient;
- exactly one full VxH gradient/contribution buffer at peak attributable to this path.

This is the primary comparator for S2.

## S2_TILED

Generalize the accepted R24 tiled behavior without tuning:

1. compact unique-row lookup backward;
2. no dense lookup W.grad;
3. late classifier dW generated by vocabulary-row tile;
4. merge matching compact rows into each tile;
5. identical AdamW consumer for the tile;
6. release tile and continue;
7. formal path never allocates full VxH gradient/shadow.

### Tile policy

The memory budget is frozen globally:
`32 MiB FP32 classifier-gradient tile`.

For each point:
- use the point's frozen H and frozen CCE `BLOCK_V`;
- `rows_per_tile` is the largest positive multiple of `BLOCK_V` whose
  FP32 gradient tile does not exceed 32 MiB;
- derive before performance timing;
- record exact rows/tile, tile bytes and tile count.

No tile-size sweep.
Do not tune D0 and H0 separately beyond this deterministic formula.

---

# 5. Implementation and holdout discipline

Candidate changes are opt-in/default OFF.
Behavior and diagnostics switches are separate.

Build one architecture-neutral runner that reads point identity dynamically.
Do not fork two scientifically different Qwen/Llama candidate implementations.

Allowed model-specific code:
- loading/token binding;
- model forward API adaptation if required;
- shape/config identity;
- deterministic CCE meta resolution.

Forbidden model-specific performance tuning:
- special tile size;
- different candidate algorithm;
- different optimizer;
- hand-selected fast path after seeing timing.

## Freeze sequence

1. Resolve D0/H0 authorities without performance timing.
2. Implement B0/C1/S2 generic paths.
3. Run engineering/unit tests.
4. Run one-step numerical qualification on D0 and H0 with timing ignored.
5. Run the multi-step trajectory qualification below.
6. If any correctness bug requires candidate code changes, fix it and rerun
   numerical/trajectory qualification on **both points**.
7. Write `IMPLEMENTATION_FREEZE.json` with source hashes.
8. After that freeze, no candidate behavior change is allowed.
9. Only then run formal D0 and H0 performance.

H0 is a performance holdout:
- correctness qualification may inspect numerical outputs;
- do not inspect/compare H0 performance before implementation freeze;
- do not tune anything using H0 timing.

---

# 6. Numerical qualification

Use the inherited `rtol=atol=1e-2` numerical bound.
Do not widen it.

## 6.1 One-step qualification — both points, all three arms

From identical frozen state compare:
- loss;
- final-hidden dH;
- reconstructed/complete total tied-weight gradient;
- updated W;
- FP32 m;
- FP32 v;
- exact step counter;
- next-forward loss.

S2/C1 debug qualification may reconstruct a full gradient solely for comparison.
That reconstruction is forbidden in formal timing.

Record finite, max_abs, mean_abs, max_rel, cosine, dtype, shape and first mismatch.

## 6.2 Four-step trajectory qualification — both points, all three arms

Purpose:
test repeated optimizer-order behavior; not training convergence.

For each arm:
- start from the same point-specific frozen state;
- execute four consecutive microsteps using the same frozen token batch;
- do not restore between the four steps;
- at each step record loss, W, m, v, step and next-forward loss.

Compare C1 and S2 to B0 after every step with the same frozen tolerance.
Step counter exact.

This repeated same-batch trajectory is only an optimizer/dataflow consistency test.
Do not claim convergence or training quality.

If any arm fails at either point:
`R25_NUMERIC_OR_TRAJECTORY_NOT_QUALIFIED`
STOP before formal timing.
No tolerance tuning, second input, or alternate algorithm.

---

# 7. Memory and lifetime accounting

For every point/arm measure direct causal state plus CUDA allocator peaks.

## Direct causal accounting

Record:
- full VxH dense lookup buffer present yes/no;
- full VxH classifier/total gradient buffer present yes/no;
- peak number of full VxH gradient buffers;
- full-gradient bytes;
- first and last full-gradient lifetime timestamps;
- compact lookup unique rows/bytes;
- inverse/index temporary bytes;
- S2 FP32 tile bytes;
- S2 consumer tile bytes;
- persistent metadata bytes;
- saved hidden/LSE/labels bytes;
- optimizer W/m/v bytes.

Expected structural intent:
- B0: up to two full gradient contributions;
- C1: one full gradient buffer;
- S2: zero full gradient buffer.

If formal code violates these arm identities, STOP:
`R25_ARM_IDENTITY_NOT_QUALIFIED`.

## CUDA allocator

Use common point-specific environment.

Before forward and before TARGET_REGION:
- record allocated/reserved;
- reset peak stats at the specified boundary.

Report:
- target peak allocated/reserved;
- target peak delta;
- complete-microstep peak allocated/reserved.

CPU restore snapshots are outside GPU memory accounting.
Other static GPU state remains common across arms.

Allocator bytes are not DRAM traffic.

---

# 8. Timing boundaries

No profiler during formal timing.

## Primary: TARGET_REGION

Immediately before backward work
through completion of the tied-W AdamW update.

Includes all arm-specific work:
- dH generation;
- full backbone propagation;
- dense or compact embedding backward;
- compact unique/index work;
- late classifier dW;
- merge;
- full/tiled AdamW;
- launches/synchronization.

Do not subtract candidate work.

## Secondary: COMPLETE_MICROSTEP

Before real-model forward
through tied-W update completion.

Same point-specific input/model/forward across arms.

No full-training-throughput claim.

---

# 9. Formal timing

Run points separately to bound VRAM.
No simultaneous GPU model campaigns.

For each point:
- one persistent process where practical;
- arms B0, C1, S2;
- 3 paired groups;
- 2 warmups/arm/group;
- 5 formal samples/arm/group;
- rotate order:
  - G0: B0 -> C1 -> S2
  - G1: C1 -> S2 -> B0
  - G2: S2 -> B0 -> C1
- exact frozen state restore before every warmup/formal run;
- retain all samples.

All CUDA/JIT uses:
`/data/c16/locks/c16_gpu_campaign.lock`.

Primary comparison:
`S2_TILED vs C1_COMPACT_FULL`.

Also report:
- C1 vs B0;
- S2 vs B0.

Per group compute median/MAD.

Define timing class for a candidate vs baseline unambiguously:

- stable benefit group:
  `median(baseline)-median(candidate) > 3*max(MADs)`
- stable regression group:
  `median(candidate)-median(baseline) > 3*max(MADs)`

Point-level:
- `BENEFIT`: >=2 stable-benefit groups and <2 stable-regression groups;
- `REGRESSION`: >=2 stable-regression groups;
- `MIXED`: otherwise.

Always report all three group directions even when point-level class is BENEFIT.

No universal 5% gate.

---

# 10. Capacity classification

Primary capacity comparison is S2 vs C1.

A point has `CAUSAL_CAPACITY_RESPONSE` only if:
1. C1 formal path has exactly one full VxH gradient buffer and no dense lookup buffer;
2. S2 formal path has zero full VxH gradient buffers;
3. every formal S2 sample has lower TARGET_REGION peak allocated memory than
   the corresponding point's C1 group median;
4. median S2 target peak allocated memory is lower than C1;
5. direct accounting agrees with allocator direction.

No percentage threshold.
Report absolute MiB and percentage.

---

# 11. Decision logic

No post-formal classifier edits.
This table is exhaustive.

## A. R25_TILED_CAPACITY_RESPONSE_CROSS_MODEL_SUPPORTED

Requirements:
- D0 and H0 one-step + four-step trajectory qualification pass;
- both points have `CAUSAL_CAPACITY_RESPONSE`;
- S2 vs C1 timing class is not `REGRESSION` at either point.

Interpretation:
the tiled approach's capacity advantage survives a stronger one-full-buffer
software baseline and one independent tied-weight model/input holdout.
Timing is reported separately as BENEFIT/MIXED per point.
Software/dataflow result only.

## B. R25_TILED_CAPACITY_TIME_TRADEOFF

Requirements:
- both points have causal capacity response,
- but S2 vs C1 is `REGRESSION` at D0 or H0.

Interpretation:
capacity generalizes, timing cost does not remain neutral/favorable.
Do not call performance positive.

## C. R25_ONE_FULL_BUFFER_SUFFICIENT

Requirements:
- C1 itself removes the important R24 allocator/lifetime effect,
- and S2 fails to establish additional causal peak-memory reduction on D0 or H0,
  without qualification failure.

Interpretation:
prefer simpler one-full-buffer software organization.

## D. R25_CAPACITY_RESPONSE_NOT_GENERALIZED

Requirements:
- D0 has causal S2-vs-C1 capacity response,
- H0 is fully qualified numerically/semantically,
- but H0 has no causal S2-vs-C1 capacity response.

Interpretation:
R24 effect is not generalized to the independent family.

## Qualification STOPs

- `R25_HOLDOUT_AUTHORITY_NOT_QUALIFIED`
- `R25_TIED_STORAGE_NOT_QUALIFIED`
- `R25_SOURCE_NOT_QUALIFIED`
- `R25_HOLDOUT_NUMERIC_NOT_QUALIFIED`
- `R25_NUMERIC_OR_TRAJECTORY_NOT_QUALIFIED`
- `R25_ARM_IDENTITY_NOT_QUALIFIED`
- `R25_RESOURCE_NOT_QUALIFIED`

Qualification failures are not performance negatives.

---

# 12. Profiling

No NCU/NVBit/SASS/Accel-Sim.

After all formal results are frozen, at most one NSYS capture per point is
allowed only if direct/allocator accounting cannot establish a specific
allocation/materialization fact.

Profiler timings are diagnostic only.

Skip NSYS when direct accounting closes the causal question.

---

# 13. Resource policy

Node109 only.
No node174 compute.

Before GPU:
- process list;
- VRAM;
- CPU/RAM/swap;
- local disk;
- node164 health.

Do not download new models/inputs.
Use accepted replicas/authority only.

H0 must fit on RTX4080 under the specified harness.
CPU frozen restore snapshots are allowed.
Do not change model precision, sequence length, or candidate algorithm to make it fit.

If the exact H0 point cannot fit without scope changes:
`R25_RESOURCE_NOT_QUALIFIED`
STOP.

P2/P3 derived/wrapper artifacts may be deterministically reconstructed.
Unrecoverable scientific payload/identity is a STOP.

Small engineering fixes remain in this Goal.

---

# 14. Forbidden expansion

No:
- third model;
- second H0 input;
- Qwen second input;
- context/batch sweep;
- tile sweep;
- optimizer sweep;
- numerical-tolerance change;
- full all-parameter training;
- convergence run;
- LoRA/quantization/MoE extension;
- NCU/NVBit/SASS;
- node174/Accel-Sim;
- hardware/PPA.

No performance-driven holdout replacement.

---

# 15. Deliverables

Review pack:
`docs/vm_tlb/review_packs/AWMA_R25_TIED_WEIGHT_BROADER_SOFTWARE_VALIDATION_109_V1/`

At minimum:
- README.md
- FINAL_DECISION.md
- PARENT_AUTHORITY.json
- D0_AUTHORITY.json
- H0_MODEL_AUTHORITY.json
- H0_INPUT_AUTHORITY.json
- POINT_CONTRACTS.json
- OPTIMIZER_CONTRACT.json
- IMPLEMENTATION_FREEZE.json
- ARM_CONTRACT.md
- ONE_STEP_NUMERICAL_QUALIFICATION.tsv
- TRAJECTORY_QUALIFICATION.tsv
- FIRST_MISMATCH.json
- MEMORY_ACCOUNTING.tsv
- LIFETIME_TRACE.tsv
- FORMAL_TARGET_TIMING.tsv
- FORMAL_MICROSTEP_TIMING.tsv
- GROUP_RESPONSE_SUMMARY.tsv
- POINT_DECISIONS.json
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Tooling:
`util/vm_tlb/awma/r25_tied_weight_broader_validation/`

Raw/receipts:
new immutable node164 R25 path.

---

# 16. Closure

One exact execution commit.
Push/fetch-back verify SHA/tree.
Release GPU lock.
Terminate campaign GPU processes.
Clean worktree.
STOP.

Final Chinese report must lead with:

1. exact D0/H0 authorities and H0 independence;
2. exact B0/C1/S2 buffer identities;
3. one-step and four-step trajectory qualification;
4. C1 vs B0 capacity/time result;
5. S2 vs C1 capacity result on D0 and H0;
6. S2 vs C1 timing class and all three group directions per point;
7. whether the capacity response crossed model/input lineage;
8. whether the result justifies production-quality software integration.

Do not lead with R24's old 773/796 MiB numbers.
Do not claim hardware, convergence, or general LLM speedup.
