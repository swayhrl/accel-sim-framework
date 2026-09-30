# Codex Goal — Lane G / node109
## R102 real precision-gated weight-update boundary V2

Date: 2026-09-30

This is one continuous solve-and-continue Goal for **Lane G / node109**.

Execution branch:
`hrl/awma-r102-real-update-boundary-109-v2`

Read first:
- `docs/vm_tlb/chatgpt_handoff/awma/round16_problem_contracts_v1/R102_REAL_UPDATE_CONTRACT_V1.md`
- `docs/vm_tlb/chatgpt_handoff/awma/round16_problem_contracts_v1/SOURCE_AND_SCOPE_NOTES.md`
- `docs/vm_tlb/chatgpt_handoff/awma/round16_dual_lane_v1/START_HERE.md`

Historical R102 execution authority:
`056daae4082aafb4bfaab10db19f004d4d76ec73`

Do not resume its old Goal. Its accepted conclusion is input authority not qualified, CUDA=0.

## 0. Question

Answer only:

> Given **real adjacent RL-published working-precision weights**, bit-exact reconstruction and one strong fused software baseline, does detect -> compact -> package -> apply retain a material GPU-local residual beyond the already-known communication-volume advantage?

Do not rediscover "updates are sparse" as the contribution.

## 1. Phase G0 — bounded new authority search, CPU/source only

Do not rescan the entire node164 filesystem.

Check, in this order:

1. assets/local records that appeared after the old R102 audit;
2. current Helix/SparseRL-Sync public artifacts and dump instructions;
3. PULSE public code/artifact/checkpoint-chain material if actually released;
4. Hugging Face TRL delta-weight-sync implementation/artifacts;
5. one-covenant GRAIL trainer checkpoint/delta publication artifacts if publicly accessible without credentials.

Record exact source commits/URLs/hashes.

The following do **not** qualify as performance input:
- a paper's sparsity percentage;
- aggregate CSV/PNG statistics;
- randomly generated masks;
- only indices without a reconstructible base/new tensor pair;
- R101 CE gradients;
- an unrelated checkpoint pair with unknown training relation.

Do not register services, request credentials, join a network, or start distributed RL training to obtain data.

## 2. Scientific input admission

Accept only one of:

### Form A — four adjacent published full versions
Four consecutive working-precision versions from the same real training run.

### Form B — anchor + ordered real patches + target hashes
A full anchor plus a real, ordered patch chain that deterministically reconstructs four consecutive published working-precision versions with target hashes.

For either:
- same run/model;
- record training algorithm/optimizer if disclosed;
- exact storage dtype/cast;
- exact publication/window identifiers;
- publication interval in optimizer steps if known;
- preserve tensor names/shapes/order;
- prove all four versions reconstruct/load consistently.

A publication window containing multiple optimizer steps is called a **publish interval**, not a single-step update.

If no qualifying input is found:
decision = `R102_REAL_UPDATE_INPUT_AUTHORITY_NOT_QUALIFIED_V2`;
publish a precise search receipt and STOP with CUDA=0.

## 3. Freeze the bucket before inspecting sparsity

After input qualification:

- sort complete tensor names deterministically;
- take whole tensors until cumulative stored size reaches but does not exceed 256 MiB;
- never rank/select by changed fraction;
- preserve native dtype and full shape;
- freeze the exact bucket hash.

Form three adjacent pairs:
- pair0, pair1 = discovery;
- pair2 = sealed temporal holdout.

The holdout is not an independent training run.

Before implementation choices, report for all three pairs:
- exact changed elements by storage bits;
- changed fraction;
- dense bytes;
- ideal index+absolute-value payload bytes under the public reference encoding;
- per-tensor distribution.

Do not change the bucket after seeing these numbers.

## 4. Correctness contract

Changed means storage-bit inequality in the published working precision.

Patch payload carries **absolute new values**, not additive floating-point deltas.

Consumer reconstruction must be bitwise identical for every bucket element.

Explicit tests:
- unchanged elements;
- changed elements;
- zero-change pair fixture;
- NaN payload bits;
- +0 / -0;
- deterministic index order;
- duplicate index rejection;
- wrong-base-version rejection;
- correct target hash.

Fixtures may be synthetic for correctness tests only.
Performance evidence uses real qualified pairs only.

## 5. Arms

### B0 — dense baseline

Given both version tensors already resident as defined by the timing setup, update the consumer bucket by copying the full new bucket.

Do not intentionally use a weak Python element loop.

### B1 — public sparse reference

Reproduce the closest public implementation semantics:
compare -> compact changed indices -> gather absolute new values -> package metadata -> apply.

Bind which project/commit/format is used.
If no public implementation can run on the exact bucket, implement a faithful minimal reference and document which operations correspond to PULSE/SparseRL/TRL semantics.

### B2 — one strong bounded GPU software implementation

Same payload semantics and deterministic index order as B1.

At most:
- two logical scans of the source;
- one bounded fused compare/compact design plus efficient scatter/apply;
- no multi-variant tuning tournament.

Use Triton/CUDA/PyTorch custom code as appropriate, but do not turn this Goal into a general compiler project.

### D1 — precomputed payload apply diagnostic

Using the exact B1/B2 payload bytes/order, time consumer apply only.

D1 diagnoses encode vs apply.
It is not an online candidate and cannot use hidden knowledge in B2.

## 6. Timing setup

Only after input/correctness/bucket close, acquire the shared GPU lock.

Use one RTX4080.

Each real arm/pair:
- 3 paired groups;
- 2 warmups/group;
- 5 uninstrumented measurements/group;
- save each sample, median, MAD.

Primary local boundary:

`old/new versions ready in GPU memory -> payload + mandatory metadata ready -> consumer bucket equals new version`

Also report separately:
- detect/compare;
- compact/prefix-scan;
- gather/package;
- host synchronization/shape retrieval if required;
- apply;
- full B1/B2 path.

Reset may occur outside timing only if reset is not part of the candidate's deployment cost.
Required synchronization/allocation/shape extraction stays inside.

Compile/JIT startup is separate from steady-state only if legitimately amortizable.

## 7. Headroom and system relevance

First report local GPU costs.

Then calculate the no-overlap communication break-even model:

`T_dense(B) = D/B + T_dense_apply`

`T_sparse(B) = T_encode + S/B + T_sparse_apply`

where:
- D = dense payload bytes;
- S = sparse payload bytes including required metadata;
- B = parameterized effective link bandwidth.

This is a model, not measured network performance.

Use a small transparent bandwidth table; do not claim a specific deployment speedup without measured system overlap/timing authority.

If existing real system timing for the exact publish path is publicly available and identity-compatible, report it separately rather than mixing it into node109 local timing.

## 8. B2 / holdout gate

Run B2 on discovery pairs first.

Proceed to sealed pair2 only if:
- real input and bitwise reconstruction pass;
- B2 improves a material local component or leaves a clearly localizable residual;
- there is a defensible >=5% remaining ideal opportunity in the relevant full local path or compatible system scope.

Do not alter B2 after opening pair2.

At most one NSYS capture if needed.
At most two NCU targets if a real residual needs classification.
Query actual SM89 metrics first.
No NVBit/SASS trace.

## 9. Decision labels

Use exactly one primary label:

- `R102_REAL_UPDATE_INPUT_AUTHORITY_NOT_QUALIFIED_V2`
- `R102_REAL_UPDATE_SPARSE_STRUCTURE_CONFIRMED_SOFTWARE_SUFFICIENT`
- `R102_GPU_LOCAL_ENCODE_APPLY_RESIDUAL_PRESENT`
- `R102_VALUE_IS_COMMUNICATION_ONLY_NO_GPU_ARCH_GAP`
- `R102_REAL_UPDATE_RESULT_MIXED_NEEDS_REVIEW`

`GPU_LOCAL_ENCODE_APPLY_RESIDUAL_PRESENT` requires:
- real adjacent versions;
- bitwise reconstruction;
- frozen unbiased bucket;
- strong B2;
- temporal holdout same direction;
- >=5% defensible remaining opportunity;
- residual localized to a GPU capability rather than only lower network bytes.

Even then, no hardware mechanism is authorized in this Goal.

## 10. Deliverables

Review pack:
`docs/vm_tlb/review_packs/AWMA_R102_REAL_UPDATE_BOUNDARY_109_V2/`

At minimum:
- `README.md`
- `AUTHORITY_SEARCH.md`
- `SOURCE_INPUT_RECEIPT.json`
- `VERSION_CHAIN.tsv`
- `BUCKET_MANIFEST.tsv`
- `CHANGE_DISTRIBUTION.tsv`
- `CORRECTNESS_TESTS.tsv`
- `B0_B1_B2_TIMING.tsv` if GPU phase runs
- `D1_APPLY_DIAGNOSTIC.tsv` if GPU phase runs
- `BREAK_EVEN_ANALYSIS.tsv`
- `PROFILE_SUMMARY.tsv` if profiling runs
- `FINAL_DECISION.md`
- `RUN_RECEIPTS.json`
- `RAW_DATA_INDEX.tsv`
- `SHA256SUMS`

Large public/raw assets remain on node164.

## 11. Closure

Release GPU lock if acquired.
Commit/push/fetch-back verify exact SHA/tree.
Clean worktree.
STOP.

Do not train an RL model, start 174, start CCE/Liger, or design an R102 hardware mechanism automatically.
