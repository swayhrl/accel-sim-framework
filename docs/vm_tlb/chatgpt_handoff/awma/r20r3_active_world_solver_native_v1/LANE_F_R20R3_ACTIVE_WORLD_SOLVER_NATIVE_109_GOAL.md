# Codex Goal — Lane F / node109
## AWMA R20R3 bounded active-world solver Native diagnostic V1

Date: 2026-10-01

Repository:
`swayhrl/accel-sim-framework`

Execution branch:
`hrl/awma-r20r3-active-world-solver-native-109-v1`

Scientific parent:
`e645b5e011c18f1e44b7a1509fb55c49486adff5`

Stage:
`AWMA_R20R3_ACTIVE_WORLD_SOLVER_NATIVE_109_V1`

Review pack:
`docs/vm_tlb/review_packs/AWMA_R20R3_ACTIVE_WORLD_SOLVER_NATIVE_109_V1/`

This is one bounded solve-and-continue Goal.

It may:
- run one B0 NSYS capture to select an eligible complete solver substage;
- implement exactly one online active-world software diagnostic;
- measure complete `solver.solve(m,d)` on the frozen discovery entries;
- open the predeclared holdout entries only if the discovery response passes the frozen investment gate.

It may not:
- add a second candidate;
- change the solver/math/precision/tolerances;
- claim whole physics-step or RL speedup;
- start 174/Accel-Sim/hardware work.

---

# 0. Frozen authority and revised numerical contract

Reuse exactly:
- MuJoCo Warp source `3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5`
- solver.py blob `090061796792f4d11408eaa69b4ef3c44465c705`
- RTX4080 / SM89
- B=1024
- G1 hfield / shuffle_dance / Menagerie authority from R20/R20R1
- sparse Newton / pyramidal cone / conditional graph
- iterations=10
- ls_iterations=20
- solver tolerance and ls_tolerance unchanged
- exact real solver-entry snapshots from the R20R1 continuous lineage

Discovery entries:
- t128: `8f3d7015979e959625f3b1d1cd1efb3fb2dea65b4e07bc9c9f1795b30dccd85d`
- t136: `07c012c0d17eaba3522bcc35016eff581612c138b7c876dff64455788344e883`
- t144: `4177e0a8a509608651f85f055877576cd71d3f25a40ab2451f276c9b08cdfda6`
- t152: `42e23fbdbb9aaae0dcbeacaa0e7ae278c1728bd9ff3a2881c8410e4f81f98e87`

Holdout steps remain:
- 384, 392, 400, 408

Do not generate or inspect holdout performance before Section 8 authorizes it.

## Revised local numerical contract

R20R1 historical contract remains unchanged.

For this new experiment, hard gates are:
1. exact solver-entry identity/options
2. exact world and constraint identity/coverage
3. exact `nefc`
4. exact outer `solver_niter`
5. no new true capacity overflow
6. finite effective outputs
7. `ctx.done` / completion semantics
8. unchanged frozen per-world and global-RMS numerical screens for:
   - qacc
   - qfrc_constraint
   - efc.Ma
   - valid efc.force
9. qfrc source relation / source-justified residual checks
10. no stale-output or hidden-state failure

`LS_ITERATIONS`:
- must be recorded per world;
- count/location plus selected alpha/improvement impact must be reported when it differs;
- the bit by itself is not a hard B0/S1 equality gate.

But an LS difference accompanied by changed outer niter, changed coverage, output beyond the frozen numerical contract, materially different propagated alpha/path, or hidden-state evidence is a correctness failure.

Outer `ITERATIONS` and true capacity overflow remain separate hard outcomes.

No contract threshold may be changed after seeing S1.

---

# 1. Rebind inputs and OFF baseline

Reuse parent solver-entry payloads and validator rather than regenerating them.

Verify:
- all discovery snapshot hashes;
- Model/source/options identity;
- parent local numerical contract SHA;
- R20R2 semantic-review authority.

The new candidate patch must be opt-in/default OFF.

Before any profiling/candidate selection:
- capture OFF B0 under the new source tree;
- for each discovery entry run at least one OFF regression from the exact snapshot;
- pass the revised contract;
- no unexpected new status bits / hidden-state behavior.

If OFF cannot reproduce the accepted B0 boundary:
`R20R3_OFF_BASELINE_NOT_QUALIFIED`
STOP.

---

# 2. One B0 NSYS capture to choose exactly one eligible substage

A single new NSYS job is allowed in the entire Goal.

Profile one unmodified OFF/B0 run that executes the four discovery solver entries in fixed order:
128 -> 136 -> 144 -> 152.

Use NVTX/event-scope names where already present. Do not insert timing synchronization into the solver.

The purpose is only to select one **complete solver substage** for the software diagnostic.

## Eligible substage criteria

A stage is eligible only if all are true:

1. It occurs within the repeated solver iteration and is paid by the complete `solver.solve`.
2. Its current kernels launch over `d.nworld` or a dimension with a world axis.
3. Completed worlds are skipped using `ctx.done` or an equivalent current-solve mask.
4. `ctx.done` does not change inside the selected stage, so one online active list is valid for the entire stage.
5. The stage has per-world outputs or independent world-local arithmetic; no cross-world numerical reduction may be changed.
6. It can be redirected through an active-world ID list while keeping each active world's **within-world kernel math, block_dim, row order and reduction order** unchanged.
7. The candidate can include all list-build / mapping / reset / synchronization costs in the complete solver timing.
8. It does not require rewriting collision, constraint construction, integrator, line-search tolerance, Newton/CG algorithm, or solver stop rules.

Examples of source families that may be audited for eligibility include:
- line-search preparation/execution family
- update-gradient family
- update-constraint family
- other event-scope-contained repeated solver stages

This list is not a promise that all are eligible.

## Frozen selection rule

Before reading timing results, write:
`ELIGIBLE_STAGE_AUDIT.md`

For every plausible stage record pass/fail for criteria 1–8.

Among eligible stages:
- choose the one with the largest **cumulative B0 GPU time across the four discovery entries** in the single NSYS capture.
- ties within 5% choose the stage with fewer source functions/kernels to modify.
- do not choose by which one is expected to show the largest speedup.

If no stage is eligible or the only eligible stage requires broad solver redesign:
`R20R3_ACTIVE_WORLD_DIAGNOSTIC_NOT_QUALIFIED`
STOP.

After selection, freeze it in:
`DIAGNOSTIC_CONTRACT.md`

No second profile and no second stage.

---

# 3. Candidate: one online active-world execution organization

Implement exactly one opt-in candidate for the selected stage.

## 3.1 Active list

The list must be produced from the **current online `ctx.done`** state at the selected stage.

Requirements:
- no future `solver_niter`
- no pre-recorded active trajectory
- no sorting by difficulty/future work
- preserve logical world IDs
- deterministic ascending-world list preferred where feasible
- list-build/scan/reset cost included
- no CPU readback to determine active count inside solver iterations

If a device compaction/scan primitive is used, record its exact implementation and cost.

## 3.2 Actual reduction in inactive-world execution

The candidate must do more than replace:

`if done[world]: return`

with:

`world = active_ids[i]; if i>=active_count:return`

while still launching the same effective amount of work.

It must reduce the selected stage's inactive-world execution footprint through one bounded mechanism such as:
- a fixed resident worker pool that consumes active IDs;
- a source-supported device-conditional launch organization;
- another single fixed online mapping with fewer world work items after shrinkage.

Do not use host-driven per-iteration launches.

## 3.3 Worker configuration

Only one worker configuration is allowed.

Do not tune by timing.

If a fixed worker pool is used, derive its block count from device/kernel occupancy or another source/device property **before formal candidate timing**, and record the formula.

Preferred rule:
- use the CUDA/Warp occupancy information for the selected dominant kernel to choose a pool no larger than the device's estimated concurrently resident block capacity;
- cap by nworld;
- no sweep.

If occupancy APIs are not practically available without invasive tooling, use one documented deterministic device-based rule (for example a fixed multiple of SM count) chosen before timing.

## 3.4 Arithmetic identity

For each active world:
- same input arrays
- same EFC/J row order
- same block_dim / tile shape
- same within-world reduction algorithm
- same outputs
- same stop predicates

World scheduling order may differ only if worlds are mathematically independent in the selected stage and no cross-world reduction/order dependency exists.

Candidate may not:
- alter line-search inner iterations;
- change outer done criteria;
- skip constraints;
- reuse stale outputs;
- change warmstart;
- change precision;
- change graph_conditional semantics.

At most two bounded engineering repairs for correctness/liveness.
A second candidate design is not allowed.

If preserving the math requires broad rewrite:
`R20R3_ACTIVE_WORLD_DIAGNOSTIC_NOT_QUALIFIED`
STOP.

---

# 4. Candidate correctness before timing

Run small engineering canaries first, then all four discovery entries.

For every B0/S1 pair:
- restore the exact same solver entry;
- pass all revised hard gates;
- apply the unchanged floating numerical contract;
- record LS_ITERATIONS differences but do not fail on the bit alone;
- if an LS difference occurs, record affected world, alpha/improvement summary and verify no propagated contract failure.

Required directed canaries where applicable:
- all worlds active
- some worlds done
- zero-active selected stage
- no-constraint world(s)
- outer iteration-limit world(s)

These are engineering checks, not extra scientific shapes.

If any discovery entry fails correctness:
`R20R3_CANDIDATE_NUMERICS_NOT_QUALIFIED`
STOP before formal timing.

---

# 5. Formal discovery timing

Only after correctness qualifies.

No profiler during formal timing.

For each discovery entry t128/t136/t144/t152:

B0 = candidate OFF
S1 = candidate ON

For each entry:
- 3 paired groups
- each group: 2 warmups/arm + 5 formal samples/arm
- alternate arm order across groups
- each sample restores the exact same frozen solver entry before the measured solve
- common restore/preconditioning strategy for B0/S1

Primary interval:
`frozen solver input ready -> complete solver.solve outputs committed`

Both arms include:
- solver initialization
- complete conditional iteration
- list-build / queue / worker management for S1
- all selected-stage work
- all unmodified solver work
- final qfrc/solver output recovery

Restore/snapshot copy is outside both measured arms and separately accounted.

Record:
- wall time
- CUDA event time
- every raw sample
- median/MAD
- selected-stage observer counters outside formal samples if needed
- active counts/list sizes
- LS_ITERATIONS counts
- outer niter / numerical contract receipts

Do not convert the old R20 0.3733 structural ratio into expected timing.

---

# 6. Discovery investment decision

Compute a paired group aggregate.

For each group:
- sum the median complete-solver time over the four discovery entries for B0;
- sum the corresponding S1 medians;
- compute the aggregate relative change.

A discovery response is `MATERIAL` only if:
1. all four entries pass correctness;
2. all three aggregate paired groups show S1 faster than B0;
3. median aggregate improvement >=5%;
4. aggregate gap is >3x the larger-arm aggregate MAD estimate;
5. the response is not explained by less solver work, changed niter/coverage, or contract relaxation.

The 5% threshold is only the investment gate for opening holdout.

If below threshold with stable measurements:
`R20R3_ACTIVE_WORLD_NO_MATERIAL_GAIN`
STOP.

If direction/variance is ambiguous:
`R20R3_RESULT_MIXED_NEEDS_REVIEW`
STOP.

No second worker count/stage/candidate may be tried.

---

# 7. Explain the discovery result without overclaiming

If MATERIAL, report:
- complete solver response
- selected-stage B0 versus S1 work-item/list counts
- list/queue maintenance cost if measurable
- which outer iterations benefited
- whether benefit grows as active worlds shrink

Do not claim:
- inactive-slot fraction is a speedup ceiling;
- solver response equals physics-step response;
- this is hardware headroom;
- this is RL training speedup.

No NCU is allowed.

The single NSYS capture from Section 2 is the only profiler evidence.

---

# 8. Holdout only for a discovery survivor

Only if Section 6 is MATERIAL.

Generate/freeze exact real solver entries at:
384, 392, 400, 408

using:
- same scene
- original B0 source
- original control generation
- no candidate trajectory
- no tuning by holdout behavior

Freeze all four before running candidate timing.

First:
- B0 qualification under revised contract;
- no threshold/candidate changes.

Then repeat the exact discovery correctness and formal timing protocol.

Holdout success requires:
1. all four holdout entries qualify;
2. all candidate numerical gates pass;
3. all three holdout aggregate paired groups favor S1;
4. median aggregate complete-solver improvement >=5%.

If so:
`R20R3_ACTIVE_WORLD_SOLVER_RESPONSE_REPRODUCED`

This means:
> a bounded online active-world software organization gives a reproducible complete-solver Native response on one public G1 benchmark replay and a sealed later time window.

It does NOT authorize hardware or 174.

If discovery does not reproduce:
`R20R3_RESULT_MIXED_NEEDS_REVIEW`

No additional entries.

---

# 9. Profiling and resource limits

Across the entire Goal:
- NSYS: at most 1 job, Section 2 only
- NCU: 0
- NVBit: 0
- SASS manual analysis: 0
- Accel-Sim: 0
- node174 compute: 0

All CUDA/JIT/capture/replay/profiling:
`/data/c16/locks/c16_gpu_campaign.lock`

Do not busy-poll or preempt another campaign.

Large raw/new snapshots -> node164.
109 keeps active replicas.
No large staging on 174.

---

# 10. Forbidden scope expansion

Do not:
- change scene, batch or replay
- train a policy
- change solver iterations / ls_iterations / tolerance
- change sparse/dense/Newton/CG choice
- modify contact/EFC construction
- make collision deterministic
- change precision
- introduce a second active-list algorithm
- sweep worker count
- optimize constraint capacity
- run whole 32-step B0/S1 trajectory timing
- infer full physics-step or RL speedup
- start hardware design
- start 174

Small engineering issues that do not alter scientific identity may be repaired solve-and-continue.

---

# 11. Deliverables

Review pack:
`docs/vm_tlb/review_packs/AWMA_R20R3_ACTIVE_WORLD_SOLVER_NATIVE_109_V1/`

At minimum:
- README.md
- FINAL_DECISION.md
- PARENT_AUTHORITY.json
- REVISED_NUMERICAL_CONTRACT.md
- OFF_BASELINE_REGRESSION.tsv
- ELIGIBLE_STAGE_AUDIT.md
- B0_PROFILE_SUMMARY.tsv
- DIAGNOSTIC_CONTRACT.md
- CANDIDATE_SOURCE_DIFF.patch
- CANDIDATE_CORRECTNESS.tsv
- DISCOVERY_TIMING.tsv if triggered
- DISCOVERY_DECISION.md
- HOLDOUT_INPUT_RECEIPTS.tsv if triggered
- HOLDOUT_TIMING.tsv if triggered
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

If a stage is not reached, mark it NOT_RUN rather than fabricating data.

---

# 12. Closure

Publish one exact commit.
Push/fetch-back verify commit/tree.
Release GPU lock.
Terminate campaign GPU processes.
Clean worktree.
STOP.

Final Chinese report should first state:
- which complete solver substage was selected and why;
- what S1 actually changed;
- whether all revised numerical gates passed;
- discovery complete-solver response;
- whether holdout ran and reproduced;
- what the result supports and what remains unknown.

Do not lead with PASS counts or internal labels.
