# EP-L2 Lane B — Descriptor 512 Calibration Handoff

Owner: dedicated Codex Window B.

## Objective

Determine whether the current 256-entry shared persistent descriptor pool is an unnecessarily tight metadata ceiling and whether 512 entries is a more appropriate calibrated baseline.

Do **not** increase descriptor capacity with the goal of forcing Line MSHR to become the bottleneck. Observe where pressure naturally moves.

## Source identity

Use the exact C7e source/config semantics used by Lane A formal runs as the base. The interim formal manifest declares:

```text
Core      ece1a3a77c5628763e0a4605bfd1c639ee6a1495
Framework f08d2ce857972fad73c4e1ab7162ba94c6336507
```

First verify these exact objects are available locally/remotely. If Lane A has published stable C7e branches, branch from those exact SHAs. Do not recreate equivalent source as a new base commit.

Suggested isolated branches/worktrees:

```text
Core      hrl/ep-l2-d512-cal-v0
Framework hrl/ep-l2-d512-cal-v0
```

Never touch Lane A runtime worktrees/binaries/results.

## Frozen variables

Only the global persistent descriptor capacity changes:

```text
Descriptor pool: 256 -> 512
Line MSHR:        128 unchanged
Per-address cap:   32 unchanged
WAD:              128 unchanged
L2 geometry:      unchanged
Payload:           unchanged
Bank arbitration: unchanged
L1:                unchanged
Queues/DRAM:       unchanged
850 MHz:           unchanged
```

## B1 — Code/cardinality audit

Audit all descriptor-capacity assumptions, including:

```text
descriptor allocator/free-ID structure
descriptor count/invariants
histogram/vector sizing
p95/max calculations
schema/parser/analyzer fields
directed tests
review-pack scripts
```

Search for hard-coded `256`, `257`, descriptor histogram bounds, or assertions whose semantics incorrectly assume the pool cannot exceed 256.

If no source change is necessary, document that D512 is already parameter-safe.

If generalization is necessary, changes must be parameterization/observation only; descriptor lifetime/allocation semantics must remain unchanged.

## B2 — D256 equivalence gate

If any source code changes, prove the generalized source configured at D256 is timing-equivalent to the exact C7e formal source on representative natural workloads.

At minimum use:

```text
vectorAdd_4M
spmv
one longer descriptor-heavy workload (scan or FWT_7_21 if practical)
```

Require exact equality for:

```text
gpu cycles
instructions
major L1/L2 traffic counts
successful DRAM transactions/bytes
terminal invariants
```

Telemetry representation may differ only where cardinality support was generalized.

Do not proceed to D512 if D256 equivalence fails without explanation.

## B3 — D512 preflight

Run D512 with L1 BASE on:

```text
vectorAdd_4M
scan
spmv
FWT_7_21
sad  # low-L2-pressure control
```

Prefer B0-Banked first for fast screening. Add paired Legacy runs where needed to verify static bank-matched baseline behavior and before full mirror launch.

Verify:

```text
COMPLETE_VALID
terminal_clean = 1
payload consistency = 1
descriptor occupancy can exceed 256 when demanded
descriptor max/p95/histogram are not clipped at 256
all required C7e telemetry remains present
Line MSHR remains 128 and cap remains 32
no unintended config delta
```

Primary comparisons against D256:

```text
cycles
descriptor need/block/max/p95
Line MSHR avg/p95/max/full
per-address-cap blocks
L1 pressure
WAD/payload/bank
L2->DRAM/scheduler/BW
5K temporal behavior
```

## B4 — D512 mirror campaign

If B1-B3 pass, launch the speculative mirror:

```text
13 workloads x {B0-Legacy, B0-Banked} @850 MHz
Descriptor = 512
= 26 calibration runs
```

Label every artifact:

```text
SPECULATIVE_CALIBRATION_D512
```

Use a separate result root, e.g.:

```text
docs/ep_l2/calibration_results/d512_850/
```

Large raw logs should remain outside Git; index them with paths/SHA256/provenance.

Parallel simulator processes are encouraged when host memory/CPU capacity allows, but use fixed source/config manifests and avoid oversubscription severe enough to cause run failures.

## Interpretation

Classify each workload into one of these evidence patterns:

```text
A. Descriptor blocks collapse + meaningful speedup + MSHR pressure emerges
   -> D512 strong baseline candidate; MSHR-centric motivation strengthened.

B. Descriptor blocks collapse + little speedup + lower pressure increases
   -> D256 throttled demand, but downstream is causal ceiling.

C. Descriptor blocks collapse + little speedup/pressure movement
   -> D256 creates retry pressure but little performance loss.

D. Descriptor blocks remain material at D512
   -> further calibration only after hardware-cost review; do not automatically enlarge again.
```

Do not call occupancy alone causal.

## Acceptance criteria

Lane B reaches `D512_READY` only if:

```text
[ ] exact C7e base provenance established
[ ] D512 cardinality audit complete
[ ] any generalization is timing-neutral at D256
[ ] D512 preflight COMPLETE_VALID
[ ] telemetry is not clipped/misparsed above 256
[ ] config diff proves descriptor capacity is the only architectural delta
[ ] no functional cache/MSHR/WAD/payload/bank/lower-path semantic change
```

After `D512_READY`, launch/continue the full D512 mirror automatically.

## Deliverables

Push source to lane-specific branches and publish documentation-only review material to the coordination branch:

```text
docs/ep_l2/codex_handoff/LANE_B_LATEST.md
docs/ep_l2/review_packs/D512_CALIBRATION_r1/
```

Include:

```text
README.md
SOURCE_ANCHORS.md
CONFIG_DIFF.md
D256_EQUIVALENCE.md
D512_PREFLIGHT.md
D512_RUN_STATUS.csv
D512_COMPARISON.csv
VALIDATION_SUMMARY.md
OPEN_ISSUES.md
RAW_LOG_INDEX.tsv
SHA256SUMS
```

Update workboard rows `D512-AUDIT`, `D512-PREFLIGHT`, and `D512-MIRROR` after each state transition.

## STOP / escalation boundaries

Stop and report if D512 appears to require changing descriptor semantics rather than capacity/representation, or if D256 equivalence cannot be restored without changing architecture behavior.

Do not implement RO no-MSHR, TVD, Unified borrowing, or change L1/DRAM resources in Lane B.