# DTC Granularity/Fairness Parallel Execution Contract

Status: `ACTIVE_WAVE_A_CONTRACT`

This file is the operational companion to:

`docs/dtc_l1/iscas2027/handoffs/DTC_GRANULARITY_FAIRNESS_PARALLEL_HANDOFF.md`

The handoff defines scientific intent. This contract defines branch isolation, execution order, validation, parallel scheduling, and evidence acceptance.

## 1. Required branch topology

Master coordination branch:

`hrl/iscas2027-dtc-granularity-fairness-v0`

Wave-A lane branches:

- `hrl/iscas2027-dtc-sg0-audit-v0`
- `hrl/iscas2027-dtc-sg1-wholeline-controls-v0`
- `hrl/iscas2027-dtc-sg4a-logical-tag-v0`
- `hrl/iscas2027-dtc-sg5-lower-traffic-observer-v0`

Do not run two source-modifying lanes in the same worktree. Create one worktree per lane.

The live TC80 CM5 worktree/branch is external to this campaign and is read-only.

## 2. Goal-mode bootstrap

Before any lane starts:

1. `git fetch origin`
2. verify master/lane branch HEAD and ancestry;
3. verify the TC80 CM5 branch/processes are not in the lane worktree;
4. record `git status --short`;
5. record available CPU, memory, swap, load, filesystem free space and `iostat`/equivalent availability;
6. create a campaign-level host snapshot under `docs/dtc_l1/iscas2027/granularity/host/`;
7. do not modify frozen FAST64/Lane-E/TC80 accepted paths.

## 3. Lane SG0 exact stage machine

### SG0.0 — source identity lock

PASS requires:

- exact Core/runtime identities for B16/TC80 and IO/OO;
- source-object hashes for `gpu-cache.{h,cc}`, DTC frontend/common source, and integration source;
- no source modification.

### SG0.1 — conventional sector-path proof

Machine-readable table must establish:

- `cache_type=SECTOR` for B16/TC80;
- line size 128 B;
- atom/MSHR address size 32 B;
- per-sector status semantics;
- lower request data size on a miss;
- fill/ready semantics.

### SG0.2 — DTC whole-line proof

Must establish for IO and OO separately:

- logical line size;
- physical allocation unit;
- lower request data size;
- response sectors required for completion;
- pending-hit merge unit;
- duplicate-after-eviction request unit.

### SG0.3 — dissertation alignment

Read Chapter 4 directly. Every statement is one of:

- explicit in dissertation;
- implied but not explicit;
- absent/unspecified.

Do not infer sector behavior if the dissertation only says “cacheline”.

### SG0.4 — implementation asymmetry classification

Produce a final table with columns:

`dimension,base_semantics,dtc_semantics,evidence,classification,possible_performance_effect,paper_implication`

### SG0 final status

`SG0_SOURCE_AND_DISSERTATION_GRANULARITY_AUDIT_PASS`

## 4. Lane SG1 exact stage machine

### SG1.0 — config feasibility

Without launching FAST12, prove that changing the cache-type token from `S` to `N` yields the intended NORMAL whole-line conventional path with no source modification.

Build four immutable configs/overlays:

- B16-S read-only authority
- B16-N new
- TC80-S read-only authority
- TC80-N new

Resolved config diff must reject unrelated changes.

### SG1.1 — directed/smoke qualification

At minimum run NN, Btree, BICG for B16-N and TC80-N.

Every row requires:

- exact frozen trace identity;
- natural exit 0;
- strict parse;
- instruction identity;
- effective geometry proof;
- `NORMAL` cache proof;
- PIB/MSHR entry count identity;
- terminal accounting/drain;
- no fatal/assert/deadlock.

### SG1.2 — G6 full diagnostic

Launch B16-N and TC80-N on fixed G6. Long rows first.

No result interpretation before all G6 rows strictly pass.

### SG1.3 — FAST12 promotion

Unless a scientific/model blocker exists, expand both B16-N and TC80-N to all FAST12. Existing S-mode B16/TC80 and DTC IO/OO are reused by hash/commit lineage.

### SG1.4 — analysis

Required GMs when FAST12 complete:

- `GM(B16-N/B16-S)`
- `GM(TC80-N/TC80-S)`
- `GM(IO/B16-N)`
- `GM(OO/B16-N)`
- `GM(IO/TC80-N)`
- `GM(OO/TC80-N)`

All ratios from integer cycles.

### SG1 final status

`SG1_CONVENTIONAL_SECTOR_WHOLELINE_FAIRNESS_PASS`

## 5. Lane SG4A exact stage machine

### SG4A.0 — one-dimensional config audit

Prove logical Tag capacity can be varied without changing:

- physical pool (80 KiB / 640 lines);
- PIB;
- request granularity;
- banks;
- lower caps;
- scheduler;
- L2/DRAM;
- workload identity.

### SG4A.1 — reuse audit

Identify accepted reusable 32/64-KiB rows for BICG/GESUMMV/Btree. Reuse only with exact identity match.

### SG4A.2 — missing FAST12 matrix

Run all missing 32/64/80-KiB logical points for IO and OO over FAST12. Negative results remain accepted if correct.

### SG4A.3 — mechanism join

For each accepted row collect source-qualified fields where available:

- Tag eviction;
- pending Tag eviction;
- duplicate-after-eviction;
- lower-created;
- physical pool/full exposure;
- cycles/instructions.

Do not infer missing observer metrics.

### SG4A final status

`SG4A_LOGICAL_TAG_CAPACITY_FAST12_PASS`

## 6. Lane SG5 exact stage machine

### SG5.0 — source design review

Before modifying Core, define the exact new counters and prove they are observer-only.

### SG5.1 — implementation

Implement default-off telemetry on dedicated observer descendants, never on accepted frozen commits.

### SG5.2 — deterministic directed fixtures

Required exact tests:

1. one 32-B sector miss -> 1 transaction, 32 payload bytes;
2. one 128-B normal miss -> 1 transaction, 128 payload bytes;
3. one DTC NEW_MISS -> 1 whole-line lower creation, 128 payload bytes;
4. DTC pending hit -> 0 new lower bytes;
5. duplicate-after-eviction -> +128 DTC lower bytes;
6. terminal lower payload/accounting closes.

### SG5.3 — telemetry equivalence

On NN and Btree for each supported mode, telemetry OFF and ON must have identical cycles, instructions and all pre-existing scientific counters.

### SG5.4 — G6 observer campaign

Run G6 for every available mode/variant. Observer runs are diagnostic only and never replace SG1/FAST64 primary rows.

### SG5 final status

`SG5_COMPARABLE_LOWER_TRAFFIC_OBSERVER_PASS`

## 7. Parallel scheduler requirements

A single coordination process may schedule across SG1/SG4A/SG5 but each scientific attempt belongs to exactly one lane and one immutable run directory.

### Initial worker ceiling

`192`

### Scale-up checkpoints

Raise to `256` only after a 10-minute observation with:

- swap used = 0;
- available memory >35%;
- iowait <10%;
- no filesystem/launch instability.

Raise to `320` only after a second equivalent stable window.

Absolute campaign cap: `384` simulator processes.

Never launch new work that causes available memory <20%, swap activity, or iowait >20%.

### Priority

Use `nice +5` for new campaign simulators if supported. Do not alter priority of the existing TC80 CM5 processes.

### Staggering

Launch no more than 32 new heavy trace consumers in any 60-second window. This avoids decompression/filesystem stampedes.

## 8. Run identity and immutability

Every run directory name contains:

`lane_stage_variant_workload_uuid`

Every run records:

- branch/commit;
- source commit;
- runtime SHA-256;
- runner SHA-256;
- config SHA-256;
- trace-list SHA-256;
- trace member manifest SHA-256;
- launch UTC;
- terminal UTC;
- exit code;
- cycles/instructions;
- validation artifact SHA-256.

No retry overwrites a prior attempt.

## 9. Fail-closed scientific acceptance

A run may be accepted only after natural termination and strict validation.

Process alive != PASS.
Empty error scan != PASS.
Timeout != scientific PASS.
Partial output != PASS.

Environment/controller/parser failures may be repaired and retried with a new UUID. Scientific-model changes require lane-stage documentation and directed requalification.

## 10. Cross-lane synchronization

SG1 may start immediately after its own SG1.0 source/config proof; it does not wait for SG0 final prose if the required source facts are independently proven and recorded.

SG5 may implement observer counters in parallel with SG1, but its runtime campaign should consume SG1 NORMAL variants only after SG1 freezes those config identities.

SG4A is independent of SG1 and SG5 and may run immediately after SG4A.0.

Wave-B SG2/SG3/SG4B must not start merely to fill CPUs. They require the handoff start conditions.

## 11. Master status integration

Each lane pushes compact evidence to its own branch. The master branch remains coordination-only until lane review.

After a lane PASS, record on the master branch:

`lane,accepted_commit,status,review_pack_sha256,notes`

Do not merge source-modifying observer/prototype commits into the master coordination branch unless explicitly needed for paper artifact generation.

## 12. Minimal final review packs

Each lane must generate:

- input manifest;
- config/source diff;
- run manifest;
- validation table;
- analysis table;
- claim boundary;
- reproduce instructions;
- output manifest.

No lane may self-certify via a text-only PASS without machine-verifiable evidence.

## 13. Stop conditions requiring researcher review

Stop a lane only if continuing requires:

- changing frozen FAST12 traces;
- modifying accepted FAST64/Lane-E/TC80 evidence;
- a new architectural choice not authorized by the handoff;
- destructive action against running CM5/raw evidence;
- interpreting an unresolved dissertation/RTL ambiguity as fact;
- an invasive Core change outside the lane's authorized scope.

Ordinary build/config/parser/environment failures are not researcher stop conditions.
