# EP-L2 Lane B — Descriptor 512 Calibration Handoff

Owner: dedicated Codex Window B.

## Objective

Determine whether the 256-entry shared persistent descriptor pool is an unnecessarily tight metadata ceiling and whether 512 entries is a more appropriate calibrated baseline. Do not tune to force Line MSHR to become the bottleneck; observe where pressure naturally moves.

## Scheduling mode

Follow:

```text
docs/ep_l2/chatgpt_handoff/SPECULATIVE_PARALLEL_EXECUTION_POLICY.md
```

Lane B no longer waits idly for a long validation job when the candidate source/config is already frozen. Validation gates still control **promotion**, not necessarily **launch**.

## Source identity

Formal C7e base:

```text
Core      ece1a3a77c5628763e0a4605bfd1c639ee6a1495
Framework f08d2ce857972fad73c4e1ab7162ba94c6336507
```

Current frozen D512 candidate:

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
```

The candidate is a direct descendant/generalization of the formal pair. Use exact immutable SHAs for runs; do not run from a moving branch tip. Never touch Lane A runtime worktrees/binaries/results.

Suggested Lane B worktrees remain:

```text
/workspace/worktrees/accel-sim-ep-l2-d512/
/workspace/worktrees/gpgpu-sim-ep-l2-d512/
```

## Frozen variables

Only:

```text
Descriptor pool: 256 -> 512
```

changes. Line MSHR=128, per-address cap=32, WAD=128, L1, Tag/L2 geometry, Payload, bank semantics, queues, DRAM and 850MHz remain unchanged.

## Current validation state

Already complete/reported:

```text
D512 cardinality source audit
D512 telemetry generalization
boundary tests
Release build/regression
D512 config-diff fail-closed test
D256 equivalence: vectorAdd_4M PASS
D256 equivalence: spmv PASS
```

Still running and mandatory before promotion:

```text
D256 equivalence: scan / B0-Banked
```

Do not interrupt that job.

## Immediate parallel action — authorized now

Do **not** wait for `scan` to finish before using otherwise idle compute.

Using the exact frozen D512 candidate above, immediately launch the D512 calibration campaign as provisional work. Prefer one 13x2 mirror with the following workloads prioritized first because they constitute the natural preflight subset:

```text
vectorAdd_4M
scan
spmv
FWT_7_21
sad or btree
+ at least one Legacy paired control
```

The same mirror rows may serve as preflight evidence; a duplicate preflight campaign is optional, not required.

All early D512 outputs are:

```text
SPECULATIVE_PENDING_GATE
promotion_dependencies:
  D256_EQ_SCAN_PASS
  D512_PREFLIGHT_PASS
```

The 26-run may continue while these gates are pending.

## Promotion logic

If `scan` D256 equivalence and D512 preflight both PASS:

```text
existing exact candidate runs
SPECULATIVE_PENDING_GATE
    -> PROMOTED_VALID_CALIBRATION
```

without simulator rerun.

If `scan` exposes an actual source/timing-equivalence defect, or preflight exposes a D512 source/config/producer defect:

```text
all affected descendants
-> INVALIDATED_BY_UPSTREAM_GATE
```

Keep them for diagnosis, repair the candidate, and rerun only affected descendants.

Parser/packaging-only failures may be reprocessed without simulator rerun when raw producer output remains valid.

## D512 telemetry validation

Before `D512_READY`, explicitly prove occupancy telemetry is not clipped above256. Require a directed telemetry fixture or natural candidate result demonstrating values above256 (e.g. `descriptor_max > 256` and, where natural pressure supports it, `descriptor_p95 > 256`) with correct parser output.

## Analysis

Compare D256 vs D512 using:

```text
cycles
descriptor need/block/avg/p95/max
Line MSHR need/full/avg/p95/max
per-address cap
L1 pressure
WAD/payload/bank
L2->DRAM/scheduler
lower_admission_byte_rate_norm
native DRAM BW from Lane D when available
5K temporal behavior
```

Use both performance and pressure movement; occupancy alone is not causal.

## Formal milestone semantics

`D512_READY` still requires all audit/equivalence/preflight gates in `LANE_B_DESCRIPTOR512_ACCEPTANCE_CRITERIA.md` to PASS.

`D512_MIRROR_COMPLETE` requires 26/26 locally valid runs **and** promotion of all rows. Finishing computations early does not lower this standard.

## Deliverables

Maintain:

```text
docs/ep_l2/codex_handoff/LANE_B_LATEST.md
docs/ep_l2/review_packs/D512_CALIBRATION_r1/
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
```

Record exact source/config/trace identity, maturity and promotion dependencies for every provisional result. Publish machine-readable equivalence/config lineage for Lane C/D.

## STOP boundaries

Do not change descriptor lifetime semantics, Line MSHR, per-address cap, L1, WAD/Payload/bank/lower resources, workloads/traces, or Lane A state. Do not implement RO/TVD/Unified or declare D512 the primary baseline.
