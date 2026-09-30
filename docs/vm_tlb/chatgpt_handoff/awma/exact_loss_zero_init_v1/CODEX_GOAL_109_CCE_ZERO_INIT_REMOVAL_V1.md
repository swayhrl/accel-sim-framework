# Codex Goal — Lane G / node109
## CCE exact dC zero-init software counterfactual V1

Date: 2026-09-30

This is one bounded, solve-and-continue Goal for **Lane G / node109**.

Scientific parent:
`ad9a302a49cdb3b1e75a9bbf04dab819c362cb1a`

Execution branch to use:
`hrl/awma-exact-loss-cce-zero-init-removal-109-v1`

Do not start Lane E / 174, Lane F, another model, a shape sweep, NCU/NVBit/SASS work, or any hardware mechanism.

---

## 0. Scientific question

Accepted exact-loss evidence on the frozen real Qwen shape shows:

- B=1, T=255, H=896, V=151936, BF16
- CCE exact/no-filter median = 7.571456 ms
- explicit full FP32 classifier-gradient accumulator = 544,538,624 bytes
- explicit full-accumulator zero-init = 0.751779 ms
- that zero-init is 9.55% of the profiled CCE GPU-kernel timeline
- materialized PyTorch B0 is still faster at 4.890624 ms on this shape

The only question in this Goal is:

> Is the >5% full-dC zero-initialization residual a simple software-organization artifact that can be removed by changing the CCE accumulation protocol, while preserving the same exact/no-filter full-gradient contract?

This Goal does **not** ask whether CCE beats PyTorch, whether full logits should always be avoided, or whether a hardware accumulator should be built.

---

## 1. Exact authority and read order

Repository:
`swayhrl/accel-sim-framework`

Start from exact scientific parent:
`ad9a302a49cdb3b1e75a9bbf04dab819c362cb1a`

Read:

- `docs/vm_tlb/review_packs/AWMA_EXACT_LOSS_CCE_LIGER_109_V1/FINAL_DECISION.md`
- `.../HEADROOM_ANALYSIS.md`
- `.../MEMORY_ACCOUNTING.tsv`
- `.../PROFILE_SUMMARY.tsv`
- `.../NUMERICAL_QUALIFICATION.tsv`
- `.../RUN_RECEIPTS.json`

Pinned CCE source:

- repo `apple-aiml-research/ml-cross-entropy`
- commit `3de376c106a1916bc5e1b619f9c77c87a461ee1c`

Relevant source facts to re-audit:

- `cut_cross_entropy/cce_backward.py`
  - exact/no-filter path allocates `dc` with `torch.zeros_like(c, dtype=float32)` when `accum_c_fp32=True`
  - the Triton backward kernel combines chunk contributions with lock/add accumulation
- `cut_cross_entropy/tl_utils.py`
  - `tl_lock_add` serializes, loads the existing destination value, adds the new contribution, and stores it
- `cut_cross_entropy/tl_autotune.py`
  - accepted environment should keep `CCE_AUTOTUNE=0`
  - fixed heuristic config is therefore used; do not enable autotuning for C1

Rebind exact source hashes before changes.

---

## 2. Hard scope

Only two formal arms:

- **C0** = accepted CCE exact/no-filter behavior
- **C1** = same CCE exact/no-filter behavior, except full FP32 dC pre-zero is removed and first contribution initializes each destination accumulation tile directly

No B0 rerun is required for the primary comparison.
No Liger rerun.
No alternate CCE presets.
No filtered gradients.
No change to shape, dtype, labels, reduction, block/chunk organization, accumulation precision or final BF16 output.

The frozen real shape remains:

`B=1, T=255, H=896, V=151936, BF16`

Reuse exact accepted hidden, lm_head, labels, model/input identity and timing harness.

If those accepted assets cannot be reproduced exactly, STOP:
`CCE_ZERO_INIT_INPUT_IDENTITY_NOT_REPRODUCIBLE`.

---

## 3. C1 semantic design

### 3.1 Required dataflow

C1 must preserve:

- CCE exact/no-filter semantics
- FP32 classifier-gradient accumulation
- original CCE LSE and backward math
- original Triton tiling / fixed heuristic launch configuration
- original final FP32 -> BF16 grad_weight commitment
- original grad_hidden computation
- all current lock-based serialization needed for concurrent contributors

Only remove the need for the **full dC destination to be zero before accumulation**.

### 3.2 Preferred bounded implementation

Preferred implementation is an initialization-aware lock state at the same granularity as the existing dC accumulation lock.

Conceptual states may be:

- 0 = destination tile not initialized / free
- 1 = first writer owns initialization
- 2 = initialized / free
- 3 = initialized / update lock held

The exact encoding may differ, but semantics must be:

1. the first legal contributor for a destination accumulation tile atomically claims initialization;
2. it writes its computed contribution directly, without reading prior dC contents;
3. it publishes the tile as initialized;
4. later contributors acquire the initialized update lock, read the prior value, add, store and release;
5. no valid destination element is read before its first initialization;
6. every valid destination element is initialized exactly once before later accumulation.

Using a separate small init-state array plus the existing mutex is also acceptable if simpler and scientifically equivalent.

### 3.3 Forbidden shortcuts

Do not:

- use a second full-size dC shadow buffer;
- zero dC lazily with another full-size pass;
- precompute contribution ownership from future runtime ordering;
- change BLOCK_B/BLOCK_V/BLOCK_D, num_warps/stages or chunking;
- enable CCE autotuning;
- change FP32 accumulation to BF16;
- remove grad_weight or grad_hidden;
- change final BF16 output dtype;
- change reduction order intentionally beyond the scheduling already present in the existing concurrent lock/add scheme.

The added initialization state must be O(number of accumulation tiles/locks), not O(number of dC elements). Report exact bytes.

### 3.4 Zero-valid fallback

Preserve correct behavior when there are no valid contributing tokens.

If the existing kernel launch would have no legal first writer for dC, explicitly fall back to the original zero result / zero-init semantics for that case.

Do not leave uninitialized output visible.

---

## 4. Directed qualification before real timing

Before the real shape, run bounded correctness tests that include:

1. one contributing B tile;
2. multiple concurrent B contributors to the same dC tile;
3. V tail not divisible by the main block;
4. H/D tail or other supported edge layout if applicable;
5. normal ignore_index mixture;
6. all-ignore / zero-valid fallback;
7. repeated executions to exercise different concurrent arrival orders;
8. full grad_hidden and grad_weight comparison against C0.

Synthetic tensors are allowed for these **correctness tests only**.

For real and directed qualification report:

- loss
- grad_hidden
- grad_weight
- max abs
- mean abs
- max rel
- cosine similarity

Use the already frozen scientific tolerance:
`rtol=1e-2, atol=1e-2`

Do not loosen it.

Also record whether C0/C1 use the same fixed CCE heuristic meta configuration.
Expected environment has `CCE_AUTOTUNE=0`; if not, force the accepted off state before both arms.

If C1 cannot satisfy correctness without broad algorithm redesign, STOP:
`CCE_ZERO_INIT_SOFTWARE_COUNTERFACTUAL_NOT_QUALIFIED`.

---

## 5. Formal paired timing

Only after qualification.

All CUDA/NSYS work must hold:

`/data/c16/locks/c16_gpu_campaign.lock`

Use exact accepted real input.

C0 and C1 are measured in the same isolated environment/process policy.

Use:
- 3 paired groups
- 2 warmups per arm/group
- 5 uninstrumented formal repeats per arm/group
- alternate arm order across groups
- save every sample, median and MAD

Primary boundary:

`real hidden + real lm_head ready -> loss + grad_hidden + grad_weight committed`

Include:
- any small lock/init-state reset needed by C1
- all mandatory synchronization
- FP32 -> BF16 grad_weight commitment

Exclude only common input restoration that is identically outside both operator boundaries.

Compilation/JIT warmup is separate after it reaches stable compiled code.

---

## 6. Required causal checks

After timing, run exactly **one NSYS capture of C1** if C1 passes numerical qualification.

The purpose is not broad profiling. Prove:

- the old full FP32 dC zero-fill is absent;
- no equivalent full-size initialization pass was moved elsewhere;
- the added initialization-state reset is visible/accounted for;
- FP32 -> BF16 output copy/cast remains;
- CCE math kernels remain present;
- no unexpected new large full-dC pass was introduced.

No NCU is authorized in this Goal.

Report both:
- full operator timing change
- timeline-local removal/replacement of the accepted 0.751779 ms zero-init phase

Do not claim the entire timing delta is exactly zero-fill cost; concurrency changes may alter backward scheduling.

---

## 7. Decision logic

### A. Software removal succeeds

Use:
`CCE_ZERO_INIT_SOFTWARE_REMOVABLE`

Require all:

- numerical contract passes;
- full-size pre-zero is absent;
- no equivalent full-size initialization moved elsewhere;
- C1 full operator improves by at least 5% versus paired C0 **or** recovers at least 70% of the accepted 0.751779 ms zero-fill cost after accounting for new init-state overhead;
- result is stable across paired groups.

Interpretation:

> The previously identified >5% zero-init residual is primarily a software accumulation-organization artifact under this frozen shape.

Then STOP.
Do not start hardware or a second shape automatically.

### B. Full pre-zero disappears but benefit is not recovered

Use:
`CCE_ZERO_INIT_REMOVED_BUT_NOT_PERFORMANCE_CAUSAL`

When:
- numerical contract passes;
- NSYS proves the full pre-zero is gone;
- but C1 gains <5% and recovers <70% of the accepted zero-fill cost because synchronization/init-aware accumulation adds equivalent cost or critical path is unchanged.

Interpretation:

> The explicit zero-fill existed, but eliminating it alone does not create a material performance opportunity.

STOP.

### C. Counterfactual cannot qualify

Use:
`CCE_ZERO_INIT_SOFTWARE_COUNTERFACTUAL_NOT_QUALIFIED`

for correctness/liveness/semantic failure that cannot be fixed without changing the bounded design.

### D. Residual survives for a deeper reason

Use:
`CCE_ZERO_INIT_RESIDUAL_SURVIVES_SOFTWARE_COUNTERFACTUAL`

only when:
- C1 is correct;
- implementation is bounded and does not move equivalent work elsewhere;
- the full pre-zero or an unavoidable equivalent initialization cost remains >5%;
- and the cause is not a simple engineering bug.

This label does **not** authorize hardware.
It only triggers review of whether one second natural shape is worth testing.

---

## 8. Resource/engineering policy

Before GPU work, check current 109 health and lock state.

Normal engineering issues:
solve and continue.

Do not broaden the science because:
- Triton code is inconvenient;
- atomics need a small helper;
- a profiler command needs repair.

But if correct first-writer ownership requires a fundamentally new reduction order or a different numerical contract, STOP for review.

Do not use idle GPU time to launch another experiment.

---

## 9. Deliverables

Review pack:

`docs/vm_tlb/review_packs/AWMA_CCE_ZERO_INIT_REMOVAL_109_V1/`

At minimum:

- `README.md`
- `SOURCE_IDENTITY.json`
- `C0_C1_DESIGN.md`
- `DIRECTED_TESTS.tsv`
- `NUMERICAL_QUALIFICATION.tsv`
- `TIMING.tsv`
- `PAIRED_ANALYSIS.json`
- `INIT_STATE_ACCOUNTING.tsv`
- `NSYS_CAUSAL_RECEIPT.md`
- `FINAL_DECISION.md`
- `RUN_RECEIPTS.json`
- `RAW_DATA_INDEX.tsv`
- `SHA256SUMS`
- exact source patch/diff

Large raw stays on node164.

---

## 10. Closure

At completion:

- release GPU lock;
- commit exact patch/tools/review pack;
- push;
- fetch-back verify remote SHA/tree;
- clean worktree;
- report exact branch/commit/tree/node164 path/hashes;
- STOP.

Do not:
- start a second shape;
- start another model;
- start 174;
- design a hardware accumulator;
- optimize the FP32->BF16 cast;
- reopen Liger.
