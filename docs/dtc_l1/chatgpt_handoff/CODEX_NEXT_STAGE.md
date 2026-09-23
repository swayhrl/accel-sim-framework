# CODEX_NEXT_STAGE

## Status

**ACTIVE — BOUNDED DOWNSTREAM HEADROOM; UNATTENDED SOLVE-AND-CONTINUE**

Do not restart the current scientific program and do not reset any branch.

This file is the executable specification for the next unattended ~20-hour window.

## Objective

Determine whether a source-supported downstream resource enlargement can recover DTC performance **while keeping the default DTC lower-outstanding cap at 8192**.

This stage is not a new broad sweep.

## Source anchors

Before work:

1. `git fetch origin`.
2. Verify actual remote heads.
3. Use newer remote state if any branch advanced; record the delta, never reset.

Review anchors at coordination time:

- SG1: `e909f90a`
- SG3: `4f6e136e`
- SG4A: `42735258`
- SG5: `f4077f46`

Read:

1. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
2. `docs/dtc_l1/chatgpt_handoff/DISCUSSION_REFERENCE.md`
3. this file
4. SG3 source/config/telemetry audit files on the downstream branch.

## Worktree / branch isolation

Execution/evidence branch:

`hrl/iscas2027-dtc-sg3-downstream-localization-v0`

Use an isolated SG3 worktree.

Treat:

- SG1,
- SG4A,
- SG5,
- frozen FAST64/Lane-E/TC80 evidence

as read-only inputs for this stage.

Do not modify ChatGPT-owned files in `docs/dtc_l1/chatgpt_handoff/`.

## Phase A — mandatory zero-simulation telemetry table

**Do not launch a simulator before Phase A is complete and committed.**

From accepted SG3 BICG rows, build a paper-facing table for IO and OO at exactly:

- default
- L2 capacity 2x
- L2 MSHR entries 4x
- DTC cap 2048
- DTC cap 512

Required metrics:

- cycles
- instructions
- DTC lower outstanding average
- DTC lower outstanding peak
- lower-request average lifetime
- lower-request maximum lifetime
- L2 MSHR average occupancy
- L2 miss-queue average occupancy
- L2 total accesses
- L2 total misses
- L2 total pending hits
- `MSHR_ENTRY_FAIL`
- `MSHR_MERGE_ENTRY_FAIL`
- `MISS_QUEUE_FULL`
- `LINE_ALLOC_FAIL`
- `MSHR_RW_PENDING`
- data-port utilization
- fill-port utilization
- classified resource reservation-failure total

### Required formulas

Preserve raw counters and show exact formulas for derived values:

- avg DTC outstanding = outstanding integral / core tick samples
- avg L2 MSHR occupancy per bank = MSHR occupancy integral / L2-bank tick samples
- avg miss-queue occupancy per bank = queue occupancy integral / L2-bank tick samples
- avg lower lifetime = lifetime sum / completed lower requests
- cycle change = row cycles / same-mode default cycles - 1

Do not infer missing fields.

### Resource-failure boundary

Merge-tag identity-guard retries are non-resource telemetry.

Exclude them from:

- resource totals
- rankings
- percentages
- bottleneck attribution

Do not treat aggregate reservation fail as a resource total unless the exact source-defined reconciliation is explicit.

### Phase-A deliverables

Commit/push:

- `docs/dtc_l1/iscas2027/granularity/sg3/SG3_BICG_DOWNSTREAM_TELEMETRY_HEADROOM_TABLE_V1.tsv`
- `docs/dtc_l1/iscas2027/granularity/sg3/SG3_BICG_DOWNSTREAM_HEADROOM_INTERPRETATION_V1.md`

The interpretation must label statements as:

- SOURCE_PROVEN
- MEASURED
- CORRELATION
- INTERVENTION_SUPPORTED
- NOT_SUPPORTED / INSUFFICIENT

## Phase B — predeclared trigger tree

Only the following experiment families may be launched.

### Path Q — miss-queue headroom

Trigger only if Phase A shows a coherent queue-pressure pattern:

- nontrivial `MISS_QUEUE_FULL` and/or high average miss-queue occupancy;
- pressure decreases consistently from default -> cap2048 -> cap512;
- lower-request lifetime and cycles improve in the same direction.

If triggered, test only:

**L2 miss queue 32 -> 128 entries per bank**

Rows:

- BICG IO
- BICG OO
- GESUMMV IO
- GESUMMV OO

Hold fixed:

- DTC cap = 8192
- L2 capacity = default
- L2 MSHR = default
- L2 port width = default
- all other scientific identity

Total: 4 rows.

Do not run queue=64 in this stage.

### Path P — L2 port headroom

Trigger only if queue is not the dominant coherent pattern but data/fill-port utilization is near saturation and cap reduction consistently relieves utilization/lifetime with performance.

If triggered, test only:

**L2 data/fill port 32 -> 64 B/cache-cycle**

Rows:

- BICG IO
- BICG OO
- GESUMMV IO
- GESUMMV OO

Hold fixed:

- DTC cap = 8192
- L2 capacity = default
- L2 MSHR = default
- miss queue = default
- all other scientific identity

Total: 4 rows.

Do not run 128-B port in this stage.

### Path Q+P

If both Q and P independently satisfy their trigger, run both one-dimensional tests.

Only after both one-dimensional families strictly pass and both materially improve performance but remain incomplete may one combined upper-bound be run:

- miss queue = 128
- data/fill port = 64 B/cache-cycle
- DTC cap = 8192

Rows:

- BICG IO/OO
- GESUMMV IO/OO

Total: 4 additional rows.

### Path STOP

If neither Q nor P has a coherent source-supported trigger:

- launch no new downstream simulation;
- record status `NO_SINGLE_ADDITIONAL_L2_RESOURCE_ISOLATED`;
- do not cascade to another resource family.

## Explicitly forbidden scope

Do NOT launch:

- additional L2 capacity points
- additional L2 MSHR points
- cap=1024 or cap=4096
- queue=64
- 128-B L2 port
- ROP-latency sweep
- DRAM latency/bandwidth sweep
- NoC sweep
- extra logical-Tag experiments
- FAST12 sensitivity sweeps
- synthetic infinite-L2 configuration
- new adaptive-admission mechanism

Do not retry the SG5 GESUMMV/IO observer a third time.

## Acceptance requirements for every authorized new row

- fresh UUID
- immutable run directory
- exact Core commit
- exact runtime SHA
- exact ordered config-chain SHA
- exact trace identity
- START receipt
- terminal receipt
- strict validation receipt
- terminal drain / observer closure checks

Preserve all failures. Never overwrite an attempt.

A validator invocation/input error may use same-output named revalidation, preserving the original FAIL receipt.

## Interpretation

The question is:

> Can downstream headroom recover performance under the original cap=8192?

Paper-interesting positive evidence requires:

- material cycle improvement;
- targeted resource pressure moves in the expected direction;
- lower-request lifetime changes coherently;
- exact identity and validation pass.

Do not impose a new arbitrary numeric threshold.

If targeted resource pressure changes but cycles do not materially improve, classify that resource as insufficient.

Do not automatically search deeper resources afterward.

## Resource policy

The user authorizes aggressive compute use and will manage disk capacity.

- Do not use old fixed free-space bands as automatic stop criteria.
- Record free space and projected growth.
- Stop only for actual filesystem exhaustion / I/O risk.
- Never delete accepted/frozen evidence.
- Keep at most two heavy GESUMMV simulator processes concurrently.
- Lightweight work may use remaining safe workers.

## Deliverables

Create a review pack under:

`docs/dtc_l1/review_packs/DOWNSTREAM_HEADROOM_<revision>/`

with at minimum:

- `README.md`
- `SOURCE_ANCHORS.md`
- `VALIDATION_SUMMARY.md`
- `OPEN_ISSUES.md`
- telemetry table
- decision-tree trigger receipt
- authorized run manifest/results if any
- exact paper-safe claims
- forbidden overclaims
- raw-log index only, not large raw logs

Update:

`docs/dtc_l1/codex_handoff/LATEST_REPORT.md`

with the review-pack entry point, final branch SHA, status, conclusion, and remaining issues.

## Allowed final status

Use one of:

- `DOWNSTREAM_QUEUE_HEADROOM_SUPPORTED`
- `DOWNSTREAM_PORT_HEADROOM_SUPPORTED`
- `DOWNSTREAM_QUEUE_AND_PORT_HEADROOM_SUPPORTED`
- `DOWNSTREAM_HEADROOM_PARTIAL`
- `NO_SINGLE_ADDITIONAL_L2_RESOURCE_ISOLATED`

Do not generalize beyond BICG/GESUMMV.

## STOP boundary

Complete the telemetry gate, any triggered bounded headroom rows, review pack, Codex handoff, commit, and push.

Then STOP.

Stop earlier only if continuing would require changing:

- scientific identity,
- experiment definition,
- DTC semantics,
- frozen evidence,
- claim boundary,
- or introducing a new mechanism.
