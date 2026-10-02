# Codex Goal — Lane G / node109
## AWMA R24 tied-weight gradient lifetime native validation V1

Date: 2026-10-02

Repository:
`swayhrl/accel-sim-framework`

Stage:
`AWMA_R24_TIED_WEIGHT_GRADIENT_LIFETIME_NATIVE_109_V1`

Execution branch to create:
`hrl/awma-r24-tied-weight-gradient-lifetime-native-109-v1`

Handoff branch:
`hrl/awma-r24-tied-weight-gradient-lifetime-native-handoff-v1`

Scientific parent:
`6a094ccf28b708d8f8c6419cbdc516922082aa39`

This is one bounded solve-and-continue Goal.
Ordinary engineering issues are solved in-place and execution continues.
STOP only for a scientific identity, numeric contract, input authority, or scope change.

---

# 0. Scientific question and claim boundary

Question:

> On one frozen real Qwen2.5-0.5B tied-weight training microstep, does delaying the dense classifier-gradient contribution until the input-embedding contribution is ready, and then avoiding a full VxH gradient materialization with bounded row tiling, provide a net time and/or memory benefit after all required costs are included?

This Goal is a target-family software/dataflow validation.

It does NOT claim:
- full-model training convergence;
- end-to-end pretraining speedup;
- multi-step optimizer quality;
- generality across models/shapes;
- a hardware mechanism;
- an architecture residual.

Do not start hardware design from a positive result.

---

# 1. Frozen model, input, source and strong baseline authorities

Use exactly:

## Model

- `Qwen/Qwen2.5-0.5B-Instruct`
- revision `7ae557604adf67be50417f59c2c2f167def9a775`
- model.safetensors SHA256:
  `fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe`
- expected tied matrix shape: `[151936, 896]`, BF16
- runtime must prove:
  `model.get_output_embeddings().weight.data_ptr() == model.model.embed_tokens.weight.data_ptr()`

If tied storage is not exact:
`R24_TIED_STORAGE_NOT_QUALIFIED`
STOP.

## Input

Reuse the accepted real-token authority from:
`AWMA_EXACT_LOSS_CCE_LIGER_109_V1`

- authority: `ACCEPTED_R101_TRAIN_DISCOVERY_256`
- token file:
  `/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927/raw/TRAIN_DISCOVERY_256.json`
- token file SHA256:
  `000404d45d04a183379bd7ffa27efdfc196a08f4f97f2003cabad705ab8e2e6d`
- exact token_count: 256
- `input_ids=tokens[:-1]`, count 255
- input_ids int64 SHA256:
  `f59446f6a177507048cad5e272d03b1d910337bf0e626f4ce78aa8c244837a1e`
- `labels=tokens[1:]`, count 255
- labels int64 SHA256:
  `c89b22206d04b19d9a018e25c732aa5b1acf01b7b1ca18579bfc9ac4e1214f3a`
- B=1, T=255, H=896, V=151936
- no prefix shortening, second text, random tokens, or performance-selected input.

If this exact authority cannot be resolved:
`R24_INPUT_AUTHORITY_NOT_QUALIFIED`
STOP.
Do not silently substitute another input.

## CCE strong baseline

Use:
- repository `apple-aiml-research/ml-cross-entropy`
- commit `3de376c106a1916bc5e1b619f9c77c87a461ee1c`
- archive SHA256:
  `446d282d5b9f5bf2f8bc5a551a016498706f5066230ed682f7477c16c09cc553`

Reuse the accepted zero-init-removal software baseline:
- authority commit:
  `ec1ccad7bbcead8853cd97840a2007d96f325aa3`
- patch SHA256:
  `e4156b6ec21a7c8696192c9a2ad3eb2196630c72373c64bc8395bc2ef12fda56`
- patched `cce_backward.py` SHA256:
  `e5402a590ef019692d8341805d3adf18ed95d3062c59236b364322c296b42d36`
- patched `tl_utils.py` SHA256:
  `e117b70a0fdc2ec4313fd7d9ba5a7e1d78b30fb478760c3c661f9d717cc65ea4`

Keep the accepted fixed CCE meta:
- `CCE_AUTOTUNE=0`
- `BLOCK_B=128`
- `BLOCK_V=128`
- `BLOCK_D=32`
- `MM_BACK_BLOCK_D=64`
- `num_warps=4`
- `num_stages=4`

Do not fall back to the old full pre-zero C0 baseline.
B0 in this Goal is the accepted first-store software path.

---

# 2. Target microstep and what remains trainable

Use one real-model forward and backward path through the full Qwen backbone.

For this V1 target-family experiment:
- the tied input-embedding / lm_head weight W remains trainable;
- all other model parameters are frozen (`requires_grad=False`);
- gradients must still propagate through the full backbone to the input embedding;
- `use_cache=False`;
- no gradient checkpointing;
- no DDP/FSDP;
- no gradient accumulation;
- no gradient clipping;
- no GradScaler;
- no dropout/config changes;
- no model architecture changes.

This deliberately isolates the tied-weight two-contributor path.
It is not a full-model-training claim.

Use the same forward path for all arms.
If stochastic modules are active under the shipped config, snapshot and restore RNG state identically for all arms/runs.

---

# 3. One frozen optimizer contract

Only W is updated.

Use one explicit AdamW reference contract shared by B0/S1/S2:
- one parameter: tied W;
- BF16 parameter storage remains BF16;
- optimizer moment/state tensors use one identical dtype/layout across all arms;
- fixed hyperparameters and implementation are resolved and written to
  `OPTIMIZER_CONTRACT.json`
  before any candidate timing;
- no foreach/fused/capturable/AMSGrad variation after freeze;
- no arm-specific hyperparameter or precision difference.

Bootstrap once before formal candidate execution:
1. start from the frozen checkpoint W;
2. run one untimed B0 reference microstep;
3. freeze the resulting W, first moment, second moment, and step counter as the common starting optimizer state for all qualification/formal runs;
4. write hashes and dtype/shape into `FROZEN_START_STATE.json`.

Every later run restores the same frozen start state outside timing.

No optimizer-state tuning against results.

---

# 4. Three arms

## B0_STRONG — early full dense gradient

Use the accepted CCE first-store path.

During loss backward:
- compute dH and dense classifier dW contribution in the accepted CCE path;
- allow autograd to propagate dH through the frozen backbone;
- the same tied W receives the input-embedding contribution later;
- preserve normal dense accumulation semantics;
- after total W gradient is complete, apply the frozen AdamW contract once.

This is the strong baseline.

## S1_LATE_FULL — late but still full dense gradient

Purpose:
separate **long gradient lifetime** from **full-gradient materialization**.

Required behavior:
1. during loss backward compute dH, but do not generate the classifier dW contribution yet;
2. propagate dH through the full frozen backbone;
3. allow the input-embedding contribution to become available;
4. only then generate the classifier dW contribution;
5. form the same complete dense W gradient;
6. apply the same AdamW update once;
7. release the full dense gradient immediately afterward.

S1 may shorten full-gradient lifetime but must still materialize a complete VxH gradient.

Do not use a different CE math, different reduction precision, or weaker baseline.

## S2_LATE_TILED — late and no full dense gradient

Purpose:
test whether full VxH gradient materialization can be avoided after all costs.

Required behavior:
1. during loss backward compute dH, but not classifier dW;
2. propagate through the full frozen backbone;
3. capture the lookup-side W contribution in a compact per-token/per-unique-row representation without materializing a full VxH lookup gradient;
4. after the lookup contribution is complete, generate classifier dW by vocabulary-row macro-tile;
5. merge lookup rows belonging to the current tile;
6. apply the identical AdamW semantics to that W/state tile exactly once;
7. release/reuse the tile buffer and continue;
8. never allocate a full VxH gradient or full VxH shadow gradient in the formal S2 path.

### Macro-tile rule

Do not tune tile size.

Use one deterministic memory-budget rule:
- temporary classifier-gradient tile budget = 32 MiB;
- gradient tile dtype follows the frozen classifier-gradient accumulation dtype;
- rows_per_tile is the largest positive multiple of accepted `BLOCK_V=128` whose gradient buffer does not exceed 32 MiB;
- derive and record the exact resulting row count before candidate timing.

No sweep or second tile size.

Persistent metadata/preallocated buffers may be built before timing, but all bytes must be reported.
Per-input unique-row / lookup aggregation work is candidate work and must be included in the measured boundary.

---

# 5. Required engineering/correctness implementation structure

Candidate changes must be opt-in and default OFF.

Separate:
- behavior switches;
- diagnostics/telemetry.

OFF must reproduce B0 strong behavior.

Do not patch global package state in place without an isolated source/worktree copy.
Record exact modified source hashes.

S1/S2 are allowed to add:
- a dH-only CCE backward path;
- a dW-only late path;
- bounded vocabulary-row dW generation;
- compact lookup-gradient accumulation;
- a tilewise AdamW consumer;
- diagnostics needed to prove allocation/lifetime.

Do not:
- change forward logits/loss definition;
- change labels;
- change vocabulary;
- use future information;
- drop token occurrences;
- use sparse/approximate optimizer semantics;
- change parameter dtype;
- change CCE block meta;
- tune candidate after timing.

---

# 6. Numerical qualification before timing

Candidate timing is forbidden until numerical qualification passes.

Run B0/S1/S2 from the exact same frozen start state with timing ignored.

Qualification must compare:

1. forward loss;
2. dH at the final hidden-state boundary;
3. total tied-weight gradient;
4. updated W;
5. AdamW first moment;
6. AdamW second moment;
7. optimizer step counter;
8. one next-forward loss from the updated W.

For S2 only, a qualification/debug mode may materialize or reconstruct a full diagnostic gradient after the fact solely for comparison.
That debug materialization is forbidden in formal timing.

Use the inherited accepted CCE real-shape numerical bound:
`rtol=atol=1e-2`
for floating tensor/scalar comparisons.
Do not loosen it after observing candidate results.

Also record:
- finite/non-finite checks;
- max_abs;
- mean_abs;
- max_rel;
- cosine similarity where meaningful;
- exact shape/dtype;
- first mismatch.

Integer/token/step-counter identities are exact.

If S1 or S2 fails:
`R24_NUMERIC_CONTRACT_NOT_QUALIFIED`
STOP after preserving the first mismatch and all inputs/source hashes.

No tolerance tuning, alternate math, or second input.

---

# 7. Memory/lifetime observables

Measure both direct causal accounting and allocator peaks.

For every arm record:

## Direct accounting
- whether a full VxH tied-weight gradient is ever materialized;
- count and bytes of every full-size gradient/contribution buffer;
- S2 macro-tile buffer bytes;
- compact lookup-gradient bytes;
- saved hidden/LSE/labels bytes;
- persistent candidate metadata bytes;
- AdamW state bytes;
- first time a full dense gradient exists;
- last time it is consumed/released;
- resulting full-gradient lifetime duration where applicable.

## CUDA allocator accounting

Before forward:
- current allocated/reserved;
- reset peak stats.

Record whole-microstep:
- peak allocated;
- peak reserved.

Immediately before backward/target region:
- allocated/reserved baseline;
- reset peak stats again.

Record target-region:
- peak allocated;
- peak reserved;
- peak delta over target-region baseline.

Preallocation outside timing is not free for memory accounting.
List it explicitly.

Do not call logical-byte removal a physical traffic reduction.

---

# 8. Timing boundaries

No profiler during formal timing.

Use CUDA events plus host wall receipts.

## Primary: TARGET_REGION

Starts immediately before backward work begins.

Ends after the tied W AdamW update for that microstep is complete.

Thus it includes:
- candidate split-backward overhead;
- the full dH propagation through the frozen backbone;
- input-embedding contribution;
- candidate compact-row construction;
- late classifier-gradient generation;
- dense or tiled merge;
- candidate/full AdamW update;
- required synchronization/launch overhead.

Nothing candidate-specific may be subtracted afterward.

## Secondary: COMPLETE_MICROSTEP

Starts before the real-model forward.
Ends after the W update completes.

Same forward path/input for all arms.

Report both.
Do not turn this into a full training-throughput claim.

---

# 9. Formal timing protocol

All CUDA/JIT work holds:
`/data/c16/locks/c16_gpu_campaign.lock`

Compilation, source setup, model load, static preallocation, and frozen-state restore are outside measured boundaries.

Arms:
- B0_STRONG
- S1_LATE_FULL
- S2_LATE_TILED

Use one persistent process when practical.

Three paired groups.
For each arm/group:
- 2 warmup microsteps;
- 5 formal microsteps.

Rotate arm order by group:
- G0: B0 -> S1 -> S2
- G1: S1 -> S2 -> B0
- G2: S2 -> B0 -> S1

Before every warmup/formal run:
- restore the exact frozen W/m/v/step state;
- restore exact RNG state if relevant;
- clear only run outputs/grad state, not model/source identity;
- keep input exact.

Retain every sample.

For each formal run record:
- TARGET_REGION GPU ms;
- TARGET_REGION host wall ms;
- COMPLETE_MICROSTEP wall ms;
- peak allocated/reserved;
- target-region peak delta;
- full-gradient materialized yes/no;
- full-gradient lifetime;
- S2 tile count/row count;
- compact lookup rows/bytes;
- semantic/numeric qualification status.

For each group/arm compute median and MAD.
Use the existing engineering stability rule:
a directional timing result is stable only when the median absolute gap exceeds 3x the larger-arm MAD.

No universal 5% benefit gate.

---

# 10. Decision logic

Always report time and memory separately.

## A. R24_TILED_DELAYED_UPDATE_NET_RESPONSE_PRESENT

Requirements:
- all numerical qualification passes;
- formal S2 never materializes full VxH gradient/shadow;
- causal memory accounting and allocator data show a real reduction in tied-gradient materialization/lifetime or target-region peak;
- S2 has no stable TARGET_REGION regression versus B0 or S1;
- and S2 has either:
  - a stable TARGET_REGION timing benefit over S1, or
  - a clear memory-capacity benefit while timing is neutral/mixed rather than stably worse.

Interpretation:
bounded software/dataflow result only.
No hardware promotion.

## B. R24_SIMPLE_LATE_FULL_SUFFICIENT

Requirements:
- S1 qualifies;
- delaying the dense gradient already captures the useful lifetime/time effect;
- S2 adds no clear causal memory advantage or adds no stable timing benefit while increasing complexity.

Interpretation:
prefer the simpler full-gradient software organization.
STOP S2.

## C. R24_CAPACITY_TIME_TRADEOFF

Requirements:
- S2 qualifies and causally removes the full gradient / lowers memory,
- but S2 shows stable TARGET_REGION regression against S1 or B0 in at least two groups.

Interpretation:
record capacity-time tradeoff.
Do not call it a performance positive.
STOP unless a later application explicitly values that capacity tradeoff.

## D. R24_TIED_WEIGHT_GRADIENT_PATH_NOT_BENEFICIAL

Requirements:
- qualified candidates do not establish causal memory/lifetime improvement,
  or no stable/meaningful target response remains.

STOP current candidate.

## Qualification STOPs

- `R24_TIED_STORAGE_NOT_QUALIFIED`
- `R24_INPUT_AUTHORITY_NOT_QUALIFIED`
- `R24_SOURCE_AUTHORITY_NOT_QUALIFIED`
- `R24_NUMERIC_CONTRACT_NOT_QUALIFIED`
- `R24_RESOURCE_NOT_QUALIFIED`

Qualification failure is not a performance negative.

---

# 11. Optional causal profiling

Do not use NCU/NVBit/SASS.

After all formal timing is frozen, at most two NSYS captures total are allowed only if needed to verify a causal implementation fact such as:
- presence/absence of full-size initialization/materialization;
- unexpected extra full-buffer copy;
- candidate split-kernel launch structure.

Profiler timings are diagnostic only and may not replace formal Native timings.

If allocator/direct accounting already closes the causal question, skip NSYS.

---

# 12. Resource and engineering policy

Node109 only.
Do not use node174/Accel-Sim.

Before GPU work check:
- current GPU process list;
- VRAM;
- CPU/RAM/swap;
- local disk;
- node164 path health.

All CUDA/JIT/profiler activity holds:
`/data/c16/locks/c16_gpu_campaign.lock`

Model/raw authority:
- node164 durable;
- node109 active replica allowed;
- no large staging on 174.

If a missing file is P2/P3 derived/wrapper material, reconstruct deterministically from accepted authority and continue.
Only missing unrecoverable scientific payload/identity is a scientific STOP.

Small engineering repairs stay in this Goal.
Do not open a separate long repair Goal.

---

# 13. Forbidden expansions

No:
- second model;
- second token sequence;
- sequence-length sweep;
- batch sweep;
- tile-size sweep;
- optimizer-hyperparameter sweep;
- alternate numerical tolerance;
- training convergence run;
- full-model all-parameter optimizer study;
- NCU;
- NVBit;
- SASS;
- node174;
- Accel-Sim;
- hardware mechanism;
- PPA;
- new literature-driven mechanism during execution.

Do not convert a memory-only result into a speedup claim.

---

# 14. Deliverables

Review pack:
`docs/vm_tlb/review_packs/AWMA_R24_TIED_WEIGHT_GRADIENT_LIFETIME_NATIVE_109_V1/`

At minimum:
- README.md
- FINAL_DECISION.md
- PARENT_AUTHORITY.json
- INPUT_AUTHORITY.json
- SOURCE_IDENTITY.json
- OPTIMIZER_CONTRACT.json
- FROZEN_START_STATE.json
- ARM_CONTRACT.md
- NUMERICAL_QUALIFICATION.tsv
- FIRST_MISMATCH.json
- MEMORY_ACCOUNTING.tsv
- LIFETIME_TRACE.tsv
- FORMAL_TARGET_TIMING.tsv
- FORMAL_MICROSTEP_TIMING.tsv
- GROUP_RESPONSE_SUMMARY.tsv
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Source/tooling under:
`util/vm_tlb/awma/r24_tied_weight_gradient_lifetime/`

Publish compact report/code to Git.
Publish raw/receipts to node164 under a new immutable R24 path.

---

# 15. Closure

Publish one exact execution commit.
Push and fetch-back verify commit/tree.
Release GPU lock.
Terminate campaign GPU processes.
Worktree clean.
STOP.

Final Chinese report must lead with:
1. exact model/input/tied-storage authority;
2. exact B0/S1/S2 semantics;
3. numerical qualification;
4. whether/when a full dense gradient exists in each arm;
5. measured gradient lifetime and peak-memory changes;
6. TARGET_REGION net timing including all S2 costs;
7. whether S1 already suffices;
8. exact scope boundary and whether any further work is justified.

Do not lead with theoretical 259/519 MiB shape arithmetic.
Lead with measured causal memory/lifetime and timing.
