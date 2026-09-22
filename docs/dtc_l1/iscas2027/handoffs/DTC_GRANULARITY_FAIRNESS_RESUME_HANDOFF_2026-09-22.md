# DTC/ISCAS2027 Granularity-Fairness & Downstream Localization — Resume Handoff (2026-09-22)

Status: `RESUME_AFTER_DISK_REMEDIATION`

This document is the authoritative context handoff for a **new Codex Goal window**. It does not supersede frozen FAST64/Lane-E scientific evidence and does not promote any terminal-but-unvalidated row. Its purpose is to let a fresh Codex instance resume the multi-lane campaign without reconstructing the prior conversation.

## 0. Scientific objective

The ISCAS-2027 Decoupled-Tag Cache (DTC) paper originally showed strong Base→IO/OO speedups, but the capacity-matched TC80 study exposed an important fairness question: a conventional 80-KiB searchable cache can outperform DTC on some workloads while DTC remains much better on others.

Subsequent source audit established a second modeling asymmetry:

- conventional B16/TC80 `S` path is a 128-B line split into 32-B sectors; MSHR/lower atom is 32 B;
- current DTC IO/OO creates 128-B whole-line lower requests and completes the physical line after four 32-B response sectors.

The campaign therefore must separate:

1. conventional 32-B sector vs 128-B whole-line granularity;
2. searchable cache capacity;
3. DTC logical-Tag capacity / pending-Tag behavior;
4. DTC lower-request injection / outstanding concurrency;
5. L2 data capacity;
6. L2 MSHR / queue / reservation concurrency resources;
7. deeper downstream service limits;
8. IO head-of-line and OO lifetime/reclaim behavior.

Do **not** assume one factor is the answer in advance. Negative or mixed results are valid.

## 1. Frozen authorities and historical results

Read-only scientific authorities:

- FAST64 final: `18a68dcccd795f1b6cda75504e9450d00c9cee02`
- Lane-E canonical package freeze: `b201b03f8100b5df0010fb64849a3e826b5a2183`
- TC80 accepted CM3/CM4 branch checkpoint: `hrl/iscas2027-dtc-tc80-baseline-v0@b6248660c290326aee49620b2245ff4cf0baf33c`

Historical TC80 CM4 motivation only (not a substitute for the canonical granularity study):

- TC80-S / B16-S GM ≈ 1.4376x
- IO / B16-S GM ≈ 1.3261x
- OO / B16-S GM ≈ 1.5921x
- IO / TC80-S GM ≈ 0.9225x
- OO / TC80-S GM ≈ 1.1075x

Those results motivated the fairness work. Do not rewrite or relabel them.

## 2. Current branch topology and exact remote heads

At this handoff creation time:

- master coordination:
  `hrl/iscas2027-dtc-granularity-fairness-v0` (must be a descendant of storage-relocation commit `1bae8f55b71ee71e2081dbab8baf1a1960b67e27` and include the efficiency-policy commit `a1c8f0de69b0a920a33c805758cf79caaab2f664`; always verify the actual remote HEAD at resume)
- SG0 source/dissertation audit:
  `hrl/iscas2027-dtc-sg0-audit-v0@721a7676ce7f55c026233ea55d69b5561d6e08a6`
- SG1 whole-line conventional controls:
  `hrl/iscas2027-dtc-sg1-wholeline-controls-v0@8b622bd3f18a554501a5e401223bc71b20c9cfaa`
- SG3 downstream localization:
  `hrl/iscas2027-dtc-sg3-downstream-localization-v0@d5f0d98dccb44719e3dc3cdc2bcbbbeffa81750d`
- SG4A logical-Tag sweep:
  `hrl/iscas2027-dtc-sg4a-logical-tag-v0@97ae15d772187bea27f92771996b4603071da484`
- SG5 comparable lower-traffic observer:
  `hrl/iscas2027-dtc-sg5-lower-traffic-observer-v0@682e9e7408ff02c75c4ad64b26c60e96e6640bbe`

A new Codex must `git fetch origin` and verify actual heads. If any branch has advanced, use the newer remote state and record the delta rather than resetting it.

## 3. Host/storage state and Git object-store relocation

At the terminal checkpoint (2026-09-22T07:29:54Z), Wave-A had zero live simulator children and the only active hard blocker was disk space.

Storage remediation is now complete and recorded in:

`docs/dtc_l1/iscas2027/granularity/host/GIT_OBJECT_STORE_RELOCATION_20260922.md`

commit:

`1bae8f55b71ee71e2081dbab8baf1a1960b67e27`

Key facts:

- 139 stale `objects/pack/tmp_pack_*` files were removed after quiescence and Git-connectivity checks;
- about 43.7 GiB was recovered;
- `/workspace` now has about **54.1 GB (~50.4 GiB)** available at the user's latest report;
- the common Git object store is now:
  `/workspace/repos/accel-sim-framework/.git/objects -> /root/share/accel-sim-framework-object-store/objects`;
- post-migration `git fsck --connectivity-only --no-dangling`, HEAD resolution, worktree status reads, and push/write verification passed;
- the relocation changed repository-storage infrastructure only, not simulator science.

The new object-store target makes `/root/share` a Git-availability dependency. At every new-Codex bootstrap and before pack-intensive Git work, verify:

- the symlink resolves to the expected `/root/share` target;
- `/root/share` is mounted/accessible;
- free space is healthy on both `/workspace` and `/root/share`;
- normal Git object resolution succeeds.

No new simulator may be launched until a fresh post-cleanup host/resource snapshot is recorded.

Recommended disk gate:

- >= 60 GiB free: normal rolling execution may resume;
- 45–60 GiB: low-pressure rolling mode; batch size must be justified by projected run-directory growth;
- 35–45 GiB: validators/source work only; avoid new long runs;
- < 35 GiB: hard stop for new simulations.

At the current ~50.4 GiB, perform R0 first, then estimate median/high-percentile run-directory growth from comparable completed attempts before choosing the first heavy batch.

Never automatically delete accepted/frozen evidence. Never use `swapoff`, `drop_caches`, or destructive cleanup as part of this Goal.

## 4. SG0 — CLOSED source/dissertation audit

Current final state:

`SG0_SOURCE_AND_DISSERTATION_GRANULARITY_AUDIT_PASS`

Direct Chapter-4 review is complete and SHA-pinned. It establishes:

- Chapter 4 explicitly describes MSHR same-address merge and DTC duplicate request possibility after a same-address miss;
- the dissertation gives a 128-B cacheline context;
- it **does not specify** a 32-B-sector vs 128-B-whole-line lower transaction rule.

Therefore:

- conventional 32-B sectors are current simulator semantics;
- DTC 128-B lower requests are current simulator semantics;
- neither may be attributed to the dissertation as its explicit lower-transaction contract.

No new SG0 work is required unless provenance validation fails.

## 5. SG1 — canonical NORMAL control state

### 5.1 Historical mixed-Core G6

The old row-local G6 is preserved as:

`ROW_LOCAL_STRICT_PASS_MIXED_CORE_NOT_FINAL_PAPER_EVIDENCE`

Do not delete it. Do not use it for final paper GMs.

### 5.2 Canonical NORMAL Core

Frozen canonical NORMAL Core:

`6582b9d171330d88b17e8d5294c97704229e3823`

runtime SHA-256:

`4fcac62cd7bdccc5a49cc77950ffc45c60d5fce7c4ee44bba877e1fef2d07ef9`

Closure evidence:

`docs/dtc_l1/iscas2027/granularity/sg1/SG1_CANONICAL_NORMAL_CORE_CLOSURE.tsv`

The clean Core is derived from Core95 and contains only the audited correctness repair series:

1. deferred conventional invalidation until miss lifecycle drains;
2. NORMAL split-response owner reconciliation;
3. L1-only scope correction for that reconciliation;
4. NORMAL lazy-fetch same-Tag handling without sector cast;
5. baseline Tag pre-probe before MSHR merge.

Only `gpu-cache.cc` and `gpu-cache.h` differ from the base. Debug-only candidate commits were excluded.

### 5.3 D2B smoke

Current state:

`TERMINATED_5_STRICT_PASS_1_PENDING_STRICT_VALIDATION`

Five canonical rows have strict PASS.

The sixth:

- workload: BICG
- variant: B16-N
- UUID: `e7fb57a0-67d1-488b-9729-45ac7ac033fe`
- natural exit: 0
- terminal timestamp: 2026-09-17T07:26:08Z
- **no strict validation receipt yet**

This row is not accepted and no cycle result may be used until strict validation passes.

Immediate SG1 action after disk cleanup is **validation, not rerun**.

### 5.4 Canonical G6 plan

The pre-result G6 plan is frozen in:

`SG1_CANONICAL_G6_PLAN.tsv`

G6 = ATAX, BICG, GESUMMV, Btree, 2DConvolution, Gaussian.

BICG/Btree D2B smoke rows may be reused **only** when exact-identity + strict-PASS reuse is machine-audited. ATAX/GESUMMV/2DConvolution/Gaussian require fresh canonical attempts.

After G6 PASS, extend to full FAST12 B16-N/TC80-N using the frozen `SG1_CANONICAL_FAST12_PLAN.tsv`; reuse canonical G6 cells where exact identity matches and run the remaining FAST12 workloads required by the plan.

### 5.5 New fairness correction: common-Core sector controls

The canonical NORMAL repair series includes two shared conventional-cache correctness fixes that can affect the sector path. Therefore frozen B16-S/TC80-S results and canonical B16-N/TC80-N results must not automatically be treated as a pure S→N delta.

Before making a paper claim about sector-vs-whole-line performance, add a bounded common-Core diagnostic gate:

`SG1.D2C_CANONICAL_SECTOR_G6_CONTROL`

Run B16-S and TC80-S on the same canonical Core/runtime `6582b9d / 4fcac...` for the fixed G6 only.

Purpose:

- isolate S vs N under one Core/runtime;
- quantify whether the canonical correctness repairs materially alter the sector path;
- keep this diagnostic separate from the frozen primary FAST64/TC80 evidence.

Do not replace frozen primary B16-S/TC80-S evidence with D2C rows.

## 6. SG5 — canonical comparable lower-traffic observer

Canonical observer Core:

`1406840bc2000c9f5292f6db64fa84e115568b0c`

parent:

`6582b9d171330d88b17e8d5294c97704229e3823`

runtime SHA-256:

`7d3e80859e482d3a7029e4300a87a61c71c09485d6cfd2c7c0dd97aa02fd89a7`

The observer is default-off and source-closed; deterministic fixtures prove:

- sector conventional miss = 1 transaction / 32 B;
- NORMAL conventional miss = 1 / 128 B;
- DTC IO = 1 / 128 B;
- pending hit adds 0;
- duplicate-after-eviction adds 1 / 128 B.

Canonical C1 state:

`PASS_12_PAIR_EQUIVALENCE_4_TRANSPORT_FAILURES_PRESERVED`

All twelve required fresh OFF/ON pairs for NN/Btree across B16-S, TC80-S, B16-N, TC80-N, IO, OO strictly pass. Preserved transport failures remain excluded.

C2 current row:

- GESUMMV / B16-S retry UUID `c4ee4642-3109-4212-8f2c-1c24e887a311`
- natural exit 0
- **pending strict validation**
- initial UUID `50e5c0da...` remains preserved transport failure

Immediate action: strict-validate the terminal retry before launching new SG5 rows.

The 36-row canonical observer-ON G6 matrix is frozen in:

`SG5_CANONICAL_G6_PLAN.tsv`

Important evidence boundary:

- these rows are **diagnostic common-Core evidence**;
- they do not automatically replace frozen primary performance evidence;
- where Core/config identity is not exact, do not require equality to a historical frozen cycle count;
- where non-observer scientific semantics are proven identical to a canonical primary row, cycle/instruction equality is a strong consistency gate.

## 7. SG3 — downstream bottleneck localization

Branch state:

- SG3.0 source/resource map: PASS
- SG3.1a observer source/build/fixtures: PASS
- SG3.1b IO/OO NN+Btree OFF/ON equivalence: PASS
- SG3.2/3/4 V1 OFF-control rows: terminal exit 0 but unvalidated and nonfinal
- final observer-ON V2 sweeps: not started

Downstream observer Core:

`9b6bd33f3fb3236fd493db2dd7e11d356d1f272f`

runtime SHA-256:

`ae9a51942e99c10ab2ffafd1c68bd5f8709911890a5f15283336dfc29b70680d`

Source-mapped current L2:

- 40 L2 banks/subpartitions
- each bank: 128 sets × 16 ways × 128 B = 256 KiB
- aggregate modeled L2 data capacity = 10 MiB
- sector atom = 32 B
- associative MSHR = 192 entries per L2 bank
- merge limit = 4 per MSHR address
- miss queue = 32 per L2 bank
- data/fill port width = 32 B/cache-cycle
- DTC lower outstanding cap = **GPU-wide**, current value 8192
- L2 geometry does not automatically change modeled latency

Qualified SG3 telemetry includes:

- DTC outstanding integral/average;
- L2 MSHR occupancy integral;
- L2 miss-queue occupancy integral;
- DTC lower creation→final-response lifetime;
- existing L2 miss/reservation/failure-reason/port counters.

The final observer-ON G4 plan is predeclared:

G4 = BICG, GESUMMV, Btree, 2DConvolution; IO + OO.

Dimensions:

- L2 capacity: 0.5x / 1x / 2x
- L2 MSHR entries: 0.5x / 1x / 2x / 4x
- global DTC lower outstanding cap: 512 / 1024 / 2048 / 4096 / 8192

Total = 96 observer-ON diagnostic cells.

The twelve terminal V1 OFF-control rows may be strictly validated read-only for historical bookkeeping, but **they are not substitutes** for the 96 observer-ON rows.

Before launching the full SG3 matrix, run/validate the 1x observer-ON G4 baseline cells first. If source closure says DTC semantics are unchanged, check them against the appropriate accepted/canonical IO/OO authority. Any unexplained cycle/instruction mismatch is a blocker.

Queue-size sweep is conditional: run it only if source-defined MISS_QUEUE_FULL evidence and MSHR sweep results indicate that queue capacity remains an independent unresolved limiter.

SG3.5 downstream-service sensitivity remains conditional and should run only when capacity/MSHR/cap evidence fails to localize the limiter.

Allowed final classifications:

- `L2_CAPACITY_SENSITIVE`
- `L2_CONCURRENCY_RESOURCE_SENSITIVE`
- `DTC_INJECTION_OVERSUBSCRIBED`
- `DOWNSTREAM_SERVICE_LIMITED`
- `DTC_INTERNAL_LIFETIME_SENSITIVE`
- `MULTI_FACTOR_SENSITIVE`
- `NO_SINGLE_FACTOR_ISOLATED`

“Bottleneck migrated downstream” is **not** synonymous with “L2 data capacity is too small.”

## 8. SG4A — logical-Tag capacity study

Current frozen plan:

- logical capacities: 32 / 64 / 80 KiB
- modes: IO / OO
- physical pool fixed: 640 × 128 B = 80 KiB
- exact FAST12 pre-result plan frozen
- 16-KiB authority is not rerun

Current terminal state of first 12 BICG/GESUMMV rows:

- eight exit 0, pending strict validation;
- four exit 1, preserved nonaccepted:
  - BICG IO logical80
  - BICG OO logical80
  - GESUMMV IO logical80
  - GESUMMV OO logical80

The failure registry currently contains only the two BICG logical80 failures. The two GESUMMV logical80 failures must be audited and added before the registry is complete.

### Mandatory 80-KiB boundary audit before more logical80 launches

80-KiB logical Tag capacity is currently encoded as:

- 160 logical sets × 4 ways × 128 B = 640 logical lines
- physical pool = 640 physical lines

The four heavy-workload deadlocks make this a scientific boundary, not a routine failed run.

Before launching additional logical80 rows, source-prove:

1. whether 160 logical sets are correctly indexed by the DTC frontend;
2. whether non-power-of-two logical-set count is legal;
3. whether logical-lines == physical-lines violates a required free-physical-line / decoupling-slack invariant;
4. whether the deadlock is an expected resource boundary, an invalid geometry, or an implementation bug.

Classify the 80-KiB point as one of:

- `LEGAL_NONNUMERIC_MECHANISM_BOUNDARY`
- `LEGAL_WORKLOAD_DEPENDENT_DEADLOCK_BOUNDARY`
- `INVALID_GEOMETRY_OR_INDEXING`
- `IMPLEMENTATION_BUG_REQUIRES_REPAIR`
- `INSUFFICIENT_SOURCE_EVIDENCE`

Do not substitute a 72-KiB or other point without researcher authorization. Do not silently discard the predeclared 80-KiB point.

32/64-KiB work may continue after the eight exit-0 rows are strictly validated.

## 9. Resume order after disk cleanup

### R0 — no new simulation

1. fresh resource snapshot;
2. SG1: strict-validate terminal B16-N/BICG D2B smoke;
3. SG5: strict-validate terminal GESUMMV/B16-S C2 retry;
4. SG4A: strict-validate all eight exit-0 rows; complete failure registry for both GESUMMV logical80 failures; perform 80-KiB source-boundary audit;
5. SG3: optionally strict-validate twelve terminal V1 OFF controls for bookkeeping only;
6. commit/push each lane checkpoint separately.

No new simulator is needed for R0.

### R1 — SG1 canonical controls

After D2B smoke becomes 6/6:

- machine-audit exact reuse of canonical BICG/Btree smoke into G6;
- launch missing canonical N G6 rows: ATAX, GESUMMV, 2DConvolution, Gaussian × B16-N/TC80-N;
- in parallel, run the bounded D2C common-Core sector G6 controls B16-S/TC80-S on the same canonical runtime;
- strict-validate all rows;
- produce S-vs-N common-Core comparison plus historical/frozen-boundary note.

Then complete canonical B16-N/TC80-N FAST12 according to the frozen plan, reusing canonical G6 rows where exact identity is authorized.

### R2 — SG5 canonical G6

After the pending C2 row validates:

- continue the complete 36-row observer-ON G6 plan;
- preserve all transport/controller failures;
- report comparable transaction count and payload only from strict accepted rows;
- keep common-Core diagnostic results separate from frozen primary performance.

### R3 — SG3 downstream localization

After disk/resource gate and baseline observer checks:

1. run 1x G4 observer-ON baseline cells first;
2. capacity sweep;
3. MSHR-entry sweep;
4. global DTC cap sweep;
5. conditional queue sweep if warranted;
6. conditional service sensitivity only if prior dimensions remain insufficient;
7. build bottleneck decision matrix.

All first sweeps are one-dimensional; no simultaneous tuning.

### R4 — SG4A completion

- continue 32/64 points after validation;
- handle 80-KiB according to the source-boundary classification;
- never convert deadlock exit-1 attempts into numeric performance rows;
- never tune per workload.

### R5 — final synthesis

Only after SG1, SG3, SG4A, and SG5 close:

- produce the ISCAS-facing review package;
- clearly separate frozen primary evidence, canonical fairness controls, and diagnostic observer/sensitivity evidence;
- state which claims are source-proven, measured correlations, controlled sensitivities, or still insufficient.

## 10. Resource/concurrency policy after cleanup

At resume, choose worker ceiling from fresh measurements.

If free space >=60 GiB, CPU/load/memory/iowait are healthy:

- start at 8 new heavy simulators;
- after >=10 stable minutes may increase to 16;
- may increase to 24 only if CPU <=80%, load1 <410, memory >=25%, iowait <10%, and free space >=50 GiB;
- absolute ceiling under this handoff: 32 new heavy simulators.

All SG1/SG3/SG4A/SG5 heavy simulators count toward one common ceiling.

Long jobs first: GESUMMV, BICG, ATAX.

Use rolling queues. Do not launch hundreds merely because the host has 512 logical CPUs.

Backoff for new launches:

- caution: free <45 GiB, memory <15%, iowait >15%, sustained CPU >92%, load1 >512;
- hard stop: free <35 GiB, memory <10%, severe PSI/OOM, iowait >25%, load1 >650 and rising.

Never kill healthy scientific attempts automatically.

## 11. Attempt immutability

Every run requires:

- fresh UUID;
- immutable run directory;
- runtime SHA;
- Core commit;
- ordered config-chain SHA;
- trace identity;
- START receipt;
- terminal receipt;
- strict validation receipt before acceptance.

Never overwrite a failed run.

Validator invocation mistakes may be reconciled only when the immutable simulator run is unchanged, the original FAIL is preserved, and a new named revalidation receipt proves the corrected validator input.

No-terminal launch/controller failures remain transport failures, never scientific rows.

## 12. Claim boundaries for the paper

Until the final matrix closes, do not claim:

- DTC is universally better than equal-storage conventional cache;
- 128-B granularity alone explains DTC regressions;
- L2 capacity is the downstream bottleneck merely because L2 pressure rises;
- duplicate requests are the primary performance cause;
- more DTC physical capacity is monotonically beneficial;
- a deadlocked logical80 point has a numeric speedup.

Current safe working hypothesis:

> DTC removes front-end concurrency restrictions and can migrate the limiting resource downstream. The limiting downstream dimension may be data capacity, miss-handling concurrency, queueing/service throughput, or over-aggressive DTC injection; SG3 is designed to isolate these alternatives.

## 13. Final completion criteria

SG1:
`SG1_CANONICAL_NORMAL_FAST12_READY_FOR_PAPER`

SG5:
`SG5_COMPARABLE_LOWER_TRAFFIC_OBSERVER_PASS`

SG4A:
`SG4A_LOGICAL_TAG_FAST12_PASS`
or an explicitly researcher-approved bounded status if the predeclared 80-KiB point is source-proven invalid/nonnumeric.

SG3:
`SG3_DOWNSTREAM_BOTTLENECK_LOCALIZATION_PASS`

Overall:
`DTC_GRANULARITY_FAIRNESS_AND_DOWNSTREAM_LOCALIZATION_READY_FOR_REVIEW`

No final status may be manufactured from terminal-only rows.

## 14. New-Codex first report

Before any new simulation, report:

1. actual remote heads of master + SG0/SG1/SG3/SG4A/SG5;
2. worktree cleanliness;
3. fresh host resource snapshot after user disk cleanup;
4. exact R0 validation results;
5. SG4A logical80 source-boundary classification progress;
6. number of accepted / terminal-pending / failed-preserved / active rows per lane;
7. proposed initial heavy-simulator ceiling.

Only then proceed automatically if all gates pass.


## 15. Experimental-efficiency and elapsed-time policy

The authoritative efficiency policy is:

`docs/dtc_l1/iscas2027/handoffs/DTC_EXPERIMENTAL_EFFICIENCY_POLICY_2026-09-22.md`

It must be read together with this handoff before new simulation launches.

Key resume changes:

- do not fill matrices merely because they were enumerated;
- reuse exact accepted evidence and validate terminal rows instead of rerunning;
- once a gate passes, batch the remaining independent rows rather than splitting them into many review rounds;
- share SG3 default baselines across capacity/MSHR/cap dimensions;
- use the staged SG3 V2 design: 56-row decisive coarse screen first, conditional refinement only when the claim remains unresolved;
- do not automatically expand SG4A to the pre-enumerated 72-cell FAST12 matrix; first close a fixed G4 characterization and expand only under the predeclared triggers in the efficiency policy;
- estimate disk/time cost before every large batch;
- stop a sensitivity campaign when its scientific question is answered.

No efficiency shortcut may weaken Core/runtime identity, validation, negative-result retention, or claim boundaries.
