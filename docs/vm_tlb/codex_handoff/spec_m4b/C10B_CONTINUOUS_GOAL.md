# Window C — Continuous C10-B validation Goal

Goal: `C10B_CONTINUOUS_BUILD_RUNTIME_VALIDATION_GOAL`

Status: `GOAL_MODE / CONTINUOUS / RESOURCE_WAIT_IS_NOT_STOP`.

## 1. Goal boundary

Window A C3 is formally terminal.

Authoritative external evidence:

- A progress-review checkpoint: `14edbe200859f6ddf42bc3d459334f184a920a82`
- `C3_FINAL_STATUS = TERMINAL_PASS`
- `/workspace/m4c-c3-formal-20260905-v1/A_TERMINAL_ATTESTATION.txt`
- attestation first line: `A_TERMINAL_CONFIRMED`

The pre-terminal `C10B0_CONCURRENT_FOCUSED_COMPILE_CANARY` is superseded. The prior `RESOURCE_DEFERRED` checkpoint is not a failure of C10-B; it only recorded a temporary host gate.

This Goal must continuously execute the complete already-defined C10-B chain:

`C10B-0 compile/link -> C10B-1 standard regression -> C10B-2 focused runtime -> C10B-3 telemetry/conservation -> C10B-4 F5 -> C10B-5 fair-arm bounded sanity`

Then produce a full review pack and a C5 execution-preflight package, and STOP before actual C5 replay.

Do not invent C5 performance runs without a separately frozen C5 execution contract.

Retain labels `SPECULATIVE_CANDIDATE` and `REFERENCE_APPROX_SUBENTRY_16`.

## 2. Authoritative C inputs

Framework:

- repo: `swayhrl/accel-sim-framework`
- branch: `hrl/vm-m4b-speculative-v0`
- pre-Goal Framework HEAD: `70499d4790a0d3bd2158a23be7ae260af56f92de`

Core:

- repo: `swayhrl/gpgpu-sim`
- branch: `hrl/vm-m4b-speculative-v0`
- authoritative C10-A2 Core HEAD: `12267bb7ed1dc0257d1d903f6baf7cbdc6ca550e`

Architecture authority remains C9:

`04be2899a19b1fe756956dbe5e459494ae1da8df`

C10-A2 source/static closure remains the implementation baseline. Do not discard or rewrite it merely to get tests green.

Also read:

- `C10B_POST_A_TERMINAL_BUILD_AND_RUNTIME_VALIDATION.md`
- `C10B_ACCEPTANCE_MATRIX.md`
- C9 architecture pack
- C10-A/C10-A2 review packs

## 3. Resource policy: WAIT/RETRY instead of terminating

The previous gate rejected any nonzero PSI-full delta. That is too strict for Goal mode on a busy many-core host. Use bounded PSI percentages.

For each compile/build/runtime heavy step, sample 10 seconds and compute:

`full_pct = delta_full_total_us / (10 * 1,000,000) * 100`

Require:

- `MemAvailable >= max(64 GiB, MemTotal/5)`;
- `SwapFree >= 512 MiB` when swap exists;
- swap-in delta = 0 and swap-out delta = 0;
- memory PSI full <= 0.5%;
- io PSI full <= 1.0%;
- CPU iowait <= 10%;
- no unexplained host-failure state.

Sub-0.05% PSI-full by itself is acceptable and should not end the Goal.

### Shared heavy-slot lock

Before every compile/full-link/test/simulator/trace-heavy step, acquire:

`/workspace/vm_tlb_post_terminal_heavy_slot.lock`

with `flock`.

Only one new B/C heavy operation may hold this lock at a time. Release it after each coherent heavy stage/job; do not hold it while sleeping or doing small report parsing.

If the lock is busy or resources are temporarily above thresholds:

1. append a sample to `RESOURCE_WAIT_HISTORY.tsv`;
2. do only lightweight analysis/checkpoint work;
3. sleep about 5 minutes;
4. retry;
5. **do not terminate the Goal because of transient resource pressure**.

Do not manipulate Window A/B processes, priority, affinity or cgroups to obtain resources.

## 4. Continuous problem-solving policy

Goal mode means ordinary engineering problems must be solved, not immediately converted into a stop condition.

For compile/link/test/runtime/script issues:

`reproduce -> isolate root cause -> smallest architecture-consistent fix -> focused validation -> checkpoint -> resume`

Do not blindly repeat an identical failing command. After repeated identical failure, switch to diagnosis.

You may modify Core/Framework to repair integration/correctness bugs that are within the already-approved C9/C10 architecture. Keep fixes small and checkpointed.

Do not redesign C9 merely to make a test pass.

### Hard STOP only for

- a real C9 architecture contradiction;
- standard-mode correctness cannot be restored without changing accepted baseline semantics;
- immutable provenance/source identity is irrecoverably inconsistent;
- the requested test would require inventing a new architecture outside C9;
- evidence corruption makes validation scientifically invalid.

A first compile failure, ordinary assertion, harness bug, path error, parser mismatch, flaky helper, or transient PSI event is not a hard stop.

## 5. C10B-0 — compile/link admission

Start from exact Core `12267bb7...` **before any new functional change**.

1. Compile and run the smallest focused translation targets first, including at least:
   - `vm_c10a2_static_model_test`
   - `vm_c10a_registered_segment_test`
2. Fix compile/unit bugs if found; preserve C9/C10-A2 semantics.
3. Run additional existing VM translation tests needed to establish local integration.
4. Then perform required single-worker (`-j1`) Core/simulator build/full-link under the shared lock/resource gate.
5. Record exact compiler/build command, output SHA/provenance and fixes.

Gate: `C10B_COMPILE_LINK_PASS`.

Do not remain at `RESOURCE_DEFERRED`; wait/retry until the gate can be attempted safely.

## 6. C10B-1 — standard-mode regression

Before candidate claims, prove new opt-in code preserves accepted modes when disabled.

Run the existing focused/standard VM regression sufficient to cover:

- disabled / ideal controls;
- normal exact L1/L2 TLB;
- MSHR/PWQ/walker/PWC/PTE conservation;
- telemetry exact-once invariants;
- prior accepted translation behaviors.

If regression fails, root-cause and repair the C10 delta, then rerun. Do not proceed with a known standard regression.

Gate: `C10B_STANDARD_REGRESSION_PASS`.

## 7. C10B-2 — execute B2–B7 runtime validation

Run the directed/runtime tests specified by the existing C10-B handoff, including:

### Registration/real PA

- non-identity PA;
- >8 extent atomic fallback;
- overlap/unsorted/rights/mapping/ASID/epoch rejection;
- zero live prefix after rejection;
- conventional and Segment translation agreement.

### Lifecycle/replicas

- `INACTIVE -> INSTALLING -> ACTIVE -> REVOKING -> INACTIVE`;
- all 35 install/revoke acknowledgements for official F7/F8;
- no hit before global ACTIVE;
- one provisioned ASID behavior;
- epoch wrap/quiesce.

### Access class

- READ Weight descriptor hit eligibility;
- WRITE Weight conventional path;
- ATOMIC Weight conventional path;
- no functional dependency on `OBJECT_WEIGHT`.

### HIT_FIRST/MISS_JOIN

- L1-first;
- Segment-first;
- either-side miss while other pending;
- both miss -> exactly one lower launch;
- no duplicate completion;
- retry no repeated Segment probe;
- mapping mismatch correctness failure.

### Generation/shootdown

- stale exact fill discarded;
- stale sub-entry fill discarded;
- stale waiter/ready result discarded;
- Segment epoch and conventional generation remain separate.

### Fair selector

- F0/F1/F2/F3/F4/F6/F7/F8/F9 realize expected runtime geometry;
- F5 remains blocked until C10B-4;
- H0 remains permanently rejected;
- G96=6 sets, G32=2 sets;
- F7/F8 require 35 replicas, N=8 and 5/10/20 Lseg.

Gate: `C10B_FOCUSED_RUNTIME_PASS`.

## 8. C10B-3 — telemetry and cross-layer conservation

Run bounded/tiny real or directed workloads, not full C5.

Verify actual emitted output for:

- Segment attempts/accepts/denials/hit/miss/fallback;
- L1-first/Segment-first/both-miss/join/late discard/mismatch;
- install/revoke/replica-ack/lifecycle/ASID/epoch/Lseg;
- L1/L2/MSHR/PWQ/walker/PWC/PTE/generation/stale-fill;
- requester wait and PTE memory wait;
- existing L1D/L2/queue/DRAM/cross-layer schema continuity;
- exact-once frontend behavior and conservation.

Explicitly look for downstream pressure shifts; fewer TLB misses alone is not sufficient evidence of improvement.

Fix exporter/parser/telemetry bugs if they are behavior-neutral. If telemetry exposes a functional bug, repair the functional bug and rerun the relevant gates.

Gate: `C10B_TELEMETRY_CONSERVATION_PASS`.

## 9. C10B-4 — implement and validate F5 physical PWC

Only after C10B-0 through -3 pass, implement the already-frozen C9 F5 contract rather than the historical logical PWC shortcut:

- 120 entries total = 40/40/40 over three non-leaf levels;
- 4-way organization;
- physical pointer payload / level / prefix / attributes per C9 accounting;
- explicit port/queue/timing model;
- exact E=656 remainder budget;
- no relabeling of legacy 128-entry logical PWC as F5.

Make a serious engineering attempt. Ordinary implementation/test difficulties must be debugged.

Only leave F5 blocked if a faithful implementation would genuinely require reopening a C9 architecture decision. If so, document the exact contradiction/unknown; do not silently substitute another design.

Gate: `C10B_F5_PASS` or, only with evidence, `C10B_F5_REMAINS_BLOCKED`.

## 10. C10B-5 — bounded fair-arm sanity

Run small/bounded sanity tests for executable official arms sufficient to prove:

- intended config actually realized;
- charged capacities/sets/associativity visible;
- exact-once behavior preserved;
- no unexpected cross-arm state leakage;
- 5/10/20 Segment latency points selectable.

These are not performance conclusions.

Gate: `C10B_READY_FOR_C5_RESOURCE_GATED_REPLAY`.

## 11. C5 preflight package

If C10B reaches READY, do **not** invent or run a new C5 workload automatically. Instead prepare a C5 execution-preflight package from the now-validated runtime:

- exact candidate/control arm list;
- exact binaries/configs/registration artifacts;
- trace/ROI provenance;
- commands;
- resource/resume policy;
- expected observables/conservation;
- result acceptance matrix;
- explicit distinction between fair official arms and historical C2/C4 artifacts.

This minimizes delay for the next review while preserving the scientific gate before full performance replay.

## 12. Review pack

Maintain/update:

`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C10B_BUILD_AND_RUNTIME_VALIDATION/`

At minimum final pack contains:

- `INPUT_PROVENANCE.tsv`
- `GOAL_STATE.tsv`
- `RESOURCE_WAIT_HISTORY.tsv`
- `COMPILE_LINK_RESULTS.tsv`
- `STANDARD_REGRESSION.tsv`
- `FOCUSED_RUNTIME_MATRIX.tsv`
- `REGISTRATION_LIFECYCLE_RESULTS.tsv`
- `ACCESS_CLASS_RESULTS.tsv`
- `GENERATION_RACE_RESULTS.tsv`
- `FAIR_ARM_RUNTIME_RESULTS.tsv`
- `TELEMETRY_CONSERVATION.tsv`
- `F5_STATUS.md`
- `KNOWN_REMAINING_BLOCKERS.md`
- `C5_PREFLIGHT.md`
- `FINAL_REPORT.md`

## 13. Commit discipline

Use explicit path staging; never `git add .` or `git add -A`.

Commit coherent fixes separately where useful. Push both Framework and Core branch checkpoints. Never force-push.

## 14. Final Goal status

Use exactly one:

- `C10B_READY_FOR_C5_RESOURCE_GATED_REPLAY`
- `C10B_HARD_BLOCKER_WITH_EVIDENCE`

Do not use `RESOURCE_DEFERRED` as the final Goal status. Temporary pressure means wait/retry.

STOP after C10-B completion + C5 preflight push. Do not start full C5 replay in this Goal.