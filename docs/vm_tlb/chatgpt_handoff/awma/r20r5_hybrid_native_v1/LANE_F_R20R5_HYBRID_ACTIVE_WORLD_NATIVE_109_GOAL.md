# Codex Goal — Lane F / node109
## AWMA R20R5 fixed-304 hybrid active-world Native validation V1

Date: 2026-10-02

Repository:
`swayhrl/accel-sim-framework`

Execution branch:
`hrl/awma-r20r5-hybrid-native-109-v1`

Scientific parent:
`769ea5f3592976b2035beb76947b0d934d6efabf`

Stage:
`AWMA_R20R5_HYBRID_ACTIVE_WORLD_NATIVE_109_V1`

This is one continuous solve-and-continue Goal.

Scientific question:

> Does the only source-derived hybrid organization — baseline selected-stage execution while current nsolving>304, then the accepted 304-worker active-world worklist only when current nsolving<=304 — produce a material complete-solver Native response without changing solver semantics?

No threshold or worker search is allowed.

---

# 0. Frozen authority

Reuse exactly:
- MuJoCo Warp source:
  `3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5`
- solver.py blob:
  `090061796792f4d11408eaa69b4ef3c44465c705`
- RTX4080 / SM89
- B=1024
- G1 hfield / shuffle_dance / Menagerie authority
- sparse Newton / pyramidal / graph_conditional
- iterations=10
- ls_iterations=20
- solver tolerance / ls_tolerance unchanged

Discovery solver entries:
- t128 `8f3d7015979e959625f3b1d1cd1efb3fb2dea65b4e07bc9c9f1795b30dccd85d`
- t136 `07c012c0d17eaba3522bcc35016eff581612c138b7c876dff64455788344e883`
- t144 `4177e0a8a509608651f85f055877576cd71d3f25a40ab2451f276c9b08cdfda6`
- t152 `42e23fbdbb9aaae0dcbeacaa0e7ae278c1728bd9ff3a2881c8410e4f81f98e87`

Correctness authority:
- R20R3P2 source-semantic stop contract
- exact nefc / outer solver_niter / non-LS status / capacity / finite / done
- frozen qacc / qfrc_constraint / efc.Ma / valid efc.force screens
- qfrc source relation
- R20R2 LS_ITERATIONS semantics.

Stage authority:
`_update_gradient_incremental`

Worker authority:
304 = 4 × 76 SMs, already frozen.

Previous always-worklist candidate is historical negative and is not rerun.

---

# 1. G0 — pinned-source conditional capability audit

CPU/source audit first.

Verify in the **pinned source/ref actually used here**, not repository main:
- Warp 1.15 runtime exposes `wp.capture_if`;
- pinned MuJoCo Warp already uses `wp.capture_if` in captured graph code;
- solver already uses `wp.capture_while(nsolving,...)`.

Record:
`CONDITIONAL_SOURCE_AUDIT.md`

Do not assume nested `capture_if` inside `capture_while` is valid merely because both APIs exist.

---

# 2. G1 — engineering nested-conditional canary

Before touching the scientific solver candidate, run one tiny CUDA/Warp canary under the GPU lock.

Purpose:
prove this installed Warp/CUDA/runtime can execute a device-side conditional branch inside a captured while body with:
- a one-element device int count;
- threshold comparison on device;
- true and false branch side effects;
- repeated while iterations;
- no host read to choose branch.

The canary should exercise both branches in one graph execution if practical.

Require:
- graph capture succeeds;
- graph replay terminates;
- expected branch sequence/output is exact;
- no host decision inside loop.

At most two bounded engineering repairs:
- exact installed Warp `capture_if` API syntax;
- condition-array dtype/shape;
- nested capture construction mechanics.

Do not change CUDA/driver/Warp installation.

If nested conditional cannot be expressed cleanly:
`R20_ACTIVE_WORLD_LINE_CLOSED_HYBRID_IMPLEMENTATION_NOT_CLEAN`
STOP.

Do not invent host-controlled per-iteration switching or another queue system.

---

# 3. G2 — implement the one frozen hybrid

The hybrid must be opt-in/default OFF.

## Early branch

Condition:
`current nsolving[0] > 304`

Execute the **original baseline** `_update_gradient_incremental` selected-stage organization.

Requirements:
- do not build active-ID list;
- original d.nworld H launch;
- original d.nworld blocked-Cholesky launch;
- all original stage kernels unchanged.

## Late branch

Condition:
`current nsolving[0] <= 304`

Only then:
1. build ascending active IDs from current `ctx.done`;
2. use the already-accepted fixed 304-worker mapping for:
   - sparse incremental H update
   - blocked Cholesky/factor/search
3. keep all other selected-stage and solver kernels unchanged.

The threshold is exactly 304.
It may not be changed by timing.

## Online state

Use the existing current device `nsolving` passed into `_solver_iteration`.

At selected-stage entry, it must represent worlds not done **before** the current iteration's later `_solve_done` update.

No future niter.
No host read.
No prerecorded active trajectory.

## Conditional graph

Preferred:
- a device kernel computes one-element late/early condition from `nsolving`;
- `wp.capture_if` selects baseline or late-worklist selected-stage body inside the existing conditional solver graph.

If installed API supports `on_true/on_false`, use one conditional.
If it only supports one-sided branches, a logically equivalent pair of complementary device conditions is allowed **only if both conditions derive solely from current nsolving and both branch bodies remain mutually exclusive**.

No host switch.

---

# 4. G3 — branch-path correctness canaries

Before real discovery entries, run engineering canaries that prove:

1. `nsolving=1024` -> early baseline path only; active list not built.
2. `nsolving=305` -> early baseline path only.
3. `nsolving=304` -> late worklist path only.
4. `nsolving=1` -> late path.
5. `nsolving=0` -> selected stage is not meaningfully executed by solver loop / no invalid work.

Use debug-only branch counters or receipts, disabled during formal timing.

Also rerun:
- all-active
- some-done
- zero-active
- no-constraint
- outer-limit engineering cases as applicable.

No performance conclusions from canaries.

If branch identity or liveness is wrong after at most two local engineering repairs:
`R20_ACTIVE_WORLD_LINE_CLOSED_HYBRID_IMPLEMENTATION_NOT_CLEAN`
STOP.

---

# 5. G4 — OFF regression and four-entry hybrid correctness

Candidate OFF must reproduce accepted B0.

For each discovery entry:
- one OFF B0 regression;
- then paired B0/hybrid correctness from identical frozen input.

Apply the R20R3P2 source-semantic contract exactly.

Hard requirements:
- exact entry/model/options
- exact world/constraint coverage
- exact nefc
- exact outer solver_niter
- exact non-LS hard status
- no new true capacity overflow
- finite outputs
- ctx.done/source-stop consistency
- qacc/qfrc/Ma/valid-force frozen numerical screens
- qfrc source relation
- no stale/hidden state.

LS_ITERATIONS:
- record;
- bit alone not hard;
- material propagated difference remains failure.

Additionally record branch transition:
- first outer iteration where nsolving<=304;
- number of early baseline selected-stage invocations;
- number of late worklist invocations;
- active counts in late invocations.

These diagnostics must not use future information.

If any discovery entry fails correctness:
`R20_ACTIVE_WORLD_LINE_CLOSED_HYBRID_NUMERICS_NOT_QUALIFIED`
STOP.

No alternative hybrid.

---

# 6. G5 — formal discovery complete-solver timing

Only after all four correctness checks pass.

No profiler.

Arms:
- B0 = hybrid feature OFF
- H1 = hybrid feature ON

For each t128/t136/t144/t152:
- 3 paired groups
- 2 warmups/arm/group
- 5 formal samples/arm/group
- alternate arm order by group
- restore exact same solver entry before each sample.

Primary interval:
`frozen solver input ready -> complete solver.solve outputs committed`

H1 timing includes:
- nsolving threshold predicate
- graph conditional overhead
- late active-ID list build
- 304-worker late kernels
- all unmodified solver work.

Formal samples run with debug branch observers OFF.
All 120 formal samples must independently pass semantic gates.

Record wall and CUDA-event raw samples + median/MAD.

---

# 7. G6 — discovery decision

Use same aggregate rule as R20R3.

For each paired group:
- sum four-entry median B0 complete-solver times;
- sum four-entry median H1 times;
- compute relative improvement.

Discovery MATERIAL only if:
1. all correctness passes;
2. all formal samples semantically qualify;
3. all three aggregate groups favor H1;
4. median aggregate improvement >=5%;
5. gap >3x larger-arm aggregate MAD estimate;
6. no reduced solver work/coverage/niter.

## Stable no material gain

If H1 is stable but median aggregate improvement <5%:

`R20_ACTIVE_WORLD_LINE_CLOSED_AFTER_HYBRID_NEGATIVE`

STOP.

Do not try another threshold, worker count, stage or queue algorithm.

## Mixed / noisy / direction inconsistent

`R20_ACTIVE_WORLD_LINE_CLOSED_AFTER_HYBRID_MIXED`

STOP.

No rescue experiment.

---

# 8. G7 — automatic sealed holdout for discovery survivor

Only if discovery MATERIAL.

Generate/freeze all four holdout solver entries before H1 timing:
- 384
- 392
- 400
- 408

Use:
- original B0 source
- original G1 scene/control lineage
- no hybrid trajectory to generate inputs
- no tuning by holdout result.

Freeze hashes first.

For each holdout entry:
- B0 source-semantic qualification;
- B0/H1 correctness;
- then same 3-group formal timing.

No threshold/worker/candidate changes.

Holdout success requires:
1. all four inputs qualify;
2. all correctness gates pass;
3. all formal samples semantically qualify;
4. all three aggregate groups favor H1;
5. median aggregate improvement >=5%.

Success:
`R20R5_HYBRID_SOLVER_RESPONSE_REPRODUCED`

Meaning only:
a single source-derived hybrid active-world software organization gives a reproducible complete-solver Native response on the public G1 replay across discovery and sealed later-time windows.

Still no automatic hardware/174 admission.

If holdout fails:
`R20_ACTIVE_WORLD_LINE_CLOSED_AFTER_HYBRID_NONREPRODUCED`

STOP.

---

# 9. No parameter fishing

Forbidden:
- threshold other than 304
- worker count other than 304
- second stage
- second worklist/queue algorithm
- host-controlled switch
- NSYS/NCU/NVBit/SASS
- whole 32-step timing
- second scene/batch
- policy training
- solver tolerance/iterations changes
- contact/EFC changes
- precision changes
- hardware design
- node174/Accel-Sim.

The hybrid is the final authorized R20 active-world candidate.

---

# 10. Resource policy

All CUDA/JIT/capture/replay:
`/data/c16/locks/c16_gpu_campaign.lock`

NSYS = 0
NCU = 0
NVBit = 0
SASS = 0
Accel-Sim = 0
node174 compute = 0

Large raw/new holdout snapshots -> node164.

---

# 11. Deliverables

Review pack:
`docs/vm_tlb/review_packs/AWMA_R20R5_HYBRID_ACTIVE_WORLD_NATIVE_109_V1/`

At minimum:
- README.md
- FINAL_DECISION.md
- PARENT_AUTHORITY.json
- CONDITIONAL_SOURCE_AUDIT.md
- NESTED_CONDITIONAL_CANARY.json
- HYBRID_CONTRACT.md
- HYBRID_SOURCE_DIFF.patch
- BRANCH_PATH_CANARY.tsv
- OFF_BASELINE_REGRESSION.tsv
- CANDIDATE_CORRECTNESS.tsv
- DISCOVERY_TIMING.tsv if reached
- DISCOVERY_DECISION.md
- HOLDOUT_INPUT_RECEIPTS.tsv if reached
- HOLDOUT_TIMING.tsv if reached
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Unreached stages explicitly NOT_RUN.

---

# 12. Closure

Publish one exact commit.
Push/fetch-back verify commit/tree.
Release GPU lock.
Terminate campaign GPU processes.
Clean worktree.
STOP.

Final Chinese report must clearly say:
- whether nested device conditional was cleanly implementable;
- exact early/late branch semantics;
- whether four discovery entries remained correct;
- measured complete-solver hybrid response;
- whether holdout ran/reproduced;
- whether R20 is now formally closed or survives as a reproduced Native software response.

Do not use O2 ideal headroom as measured speedup.
