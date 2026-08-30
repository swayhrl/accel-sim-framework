# EP-L2 Lane B — Descriptor-512 Acceptance Criteria

This file is the authoritative self-gating contract for Lane B.

Codex may autonomously diagnose, repair, recommit, rebuild, and rerun **within Lane B's authorized parameterization/config/analysis scope** until all mandatory gates pass. A failed gate is not a reason to stop unless fixing it crosses a hard boundary below.

Execution scheduling additionally follows:

```text
docs/ep_l2/chatgpt_handoff/SPECULATIVE_PARALLEL_EXECUTION_POLICY.md
```

That policy may allow early computation, but it does **not** weaken any mandatory PASS condition below.

## B0. Source identity and isolation — mandatory

PASS only if:

```text
base Framework == exact C7e formal Framework source
base Core      == exact C7e formal Core source
Lane A worktrees were never modified/rebuilt/cleaned
Lane B has independent worktrees/branches/result roots
all D512 runs record source SHA + config hash + trace identity
```

Formal base:

```text
Framework f08d2ce857972fad73c4e1ab7162ba94c6336507
Core      ece1a3a77c5628763e0a4605bfd1c639ee6a1495
```

Current frozen D512 candidate authorized for speculative execution:

```text
Framework aae62b66685f15437cecf0193934f628e6fac6ae
Core      878f80869ce212e779df20b6421e4dc7f987825d
```

Do not run speculative descendants from a later moving branch tip without publishing a new explicit candidate identity.

## B1. Authorized experimental delta — mandatory

D512 changes exactly:

```text
shared persistent descriptor capacity: 256 -> 512
```

Unchanged:

```text
Line MSHR = 128
per-address cap = 32
WAD = 128
Tag/L2 geometry
payload organization/capacity
C6d bank semantics
L1 config
queue capacities
DRAM timing/scheduler/frequency
workload/trace
```

Any additional modeled timing/architecture change is a hard failure.

## B2. Descriptor cardinality/code audit — mandatory

Audit allocator/lifetime, pool-full logic, per-address-cap independence, occupancy/max/invariants, histogram/vector bounds, p95/max, app/kernel/window delta state, parser/schema/analyzer handling, and review tooling.

PASS only if existing code is parameter-safe or required changes are parameterization/observation-only and B3 passes.

## B3. D256 backward-equivalence — mandatory promotion gate

Configure generalized source back to exact D256 formal settings and compare at least:

```text
vectorAdd_4M
spmv
one longer descriptor-heavy workload: scan or FWT_7_21
```

Require exact equality for:

```text
gpu_tot_sim_cycle
terminal instruction count
successful DRAM read/write transactions
selected L2 request/miss counts
bank logical/conflict/wait counters
terminal invariants
```

Descriptor telemetry may differ only in representation if semantic values are identical.

Current state: short `vectorAdd_4M` and `spmv` checks have passed; long `scan` remains required before promotion.

An unexplained mismatch remains a hard failure for **promotion**. However, while `scan` is still running, B6/B8 computations may execute provisionally under the speculative policy.

## B4. Boundary-directed descriptor tests — mandatory

Validate at least:

```text
used = 255 / 256 / 257 under D512
used = 511 / 512
allocation at full pool
release then allocate
ID reuse/no double ownership
multiple addresses share pool
32/address cap remains independent
```

Require no histogram OOB, no leak/double ownership, correct capacity arithmetic, pool-full only at configured global capacity, cap remains 32, terminal descriptor_used=0.

Also require evidence that D512 telemetry itself can represent values above 256. This may be a directed telemetry fixture or a natural preflight result proving e.g. `descriptor_max > 256` / `descriptor_p95 > 256` when workload pressure warrants it.

## B5. Build/regression — mandatory

PASS only if final candidate has:

```text
Release build PASS
relevant C3-C7/C6d/C7e regressions PASS
D512 boundary tests PASS
D512 config-diff test PASS
parser/schema/analyzer tests PASS
git diff --check PASS
clean frozen source worktrees
```

## B6. D512 natural preflight — mandatory promotion gate, may run early

Run at least:

```text
vectorAdd_4M
scan
spmv
FWT_7_21
one low-descriptor-pressure control: sad or btree
```

Prefer B0-Banked plus at least one Legacy paired control.

Every row requires COMPLETE_VALID, exact source/config identity, terminal_clean=1, payload consistency, parser success, and required telemetry.

Report:

```text
cycles D256 vs D512
descriptor need/block/avg/p95/max
Line-MSHR avg/p95/max/full
per-address cap
L1 pressure
L2->DRAM/scheduler/lower-admission rate
native DRAM BW when available from Lane D
5K temporal movement
```

### Speculative scheduling

B6 may start while B3 `scan` equivalence is still running, provided it uses the frozen candidate above and is marked:

```text
SPECULATIVE_PENDING_GATE
promotion_dependencies = D256_EQ_SCAN_PASS
```

If B3 later fails due a source/producer/timing defect, these preflight results are invalidated.

## B7. D512_READY gate — unchanged

Codex may declare:

```text
D512_READY
```

only when B0-B6 all PASS and no modeled variable except descriptor capacity differs.

Update:

```text
D512-AUDIT = DONE
D512-PREFLIGHT = DONE
```

with exact SHAs/config hashes/results/equivalence evidence.

This is the point where provisional descendants may be promoted.

## B8. Full D512 mirror — mandatory target; speculative early launch authorized

Target remains:

```text
13 workloads x {B0-Legacy, B0-Banked} @850 MHz
Descriptor = 512
= 26 runs
```

All runs use one immutable candidate source/config family.

Lane B is authorized to launch this mirror **before B3/B6 promotion gates finish**. Until both pass, every result is:

```text
run_status = COMPLETE_VALID or local status
maturity   = SPECULATIVE_PENDING_GATE
promotion_dependencies:
  - D256_EQ_SCAN_PASS
  - D512_PREFLIGHT_PASS
```

Prefer one frozen 26-run campaign whose preflight workloads receive scheduling priority. Those identical rows may satisfy B6 once complete, avoiding duplicate simulation.

If both gates pass, exact already-completed rows may be relabeled `PROMOTED_VALID_CALIBRATION` without rerun. If a gate exposes a source/config/producer defect, affected rows are `INVALIDATED_BY_UPSTREAM_GATE` and rerun after repair.

Never label this mirror FORMAL or PRIMARY_BASELINE.

## B9. Mirror completion — mandatory

`D512_MIRROR_COMPLETE` requires:

```text
26/26 COMPLETE_VALID
all rows PROMOTED_VALID_CALIBRATION
single frozen source/config family
all manifests/provenance consistent
terminal invariants clean
no missing required telemetry
analysis-ready D256 comparison
```

A fully computed 26/26 set that is still `SPECULATIVE_PENDING_GATE` is **not** `D512_MIRROR_COMPLETE`.

## B10. Interpretation output

For every workload report D256/D512 cycles, speedup, descriptor pressure, Line-MSHR movement, L1 movement, lower/scheduler/native-BW movement, and whether the bottleneck moved rather than disappeared.

Use conservative classifications:

```text
DESCRIPTOR_CAUSAL_SENSITIVE
DESCRIPTOR_THROTTLE_MOVES_DOWNSTREAM
DESCRIPTOR_PRESSURE_LOW_PERF_SENSITIVITY
D512_STILL_DESCRIPTOR_LIMITED
INSUFFICIENT_EVIDENCE
```

## B11. Review pack / return path

Create/update:

```text
docs/ep_l2/review_packs/D512_CALIBRATION_r1/
docs/ep_l2/codex_handoff/LANE_B_LATEST.md
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
```

Include source anchors, candidate identity, config hashes, D256 equivalence evidence, boundary/telemetry tests, preflight, mirror status with maturity/promotion dependencies, comparison tables, raw-log index, SHA256SUMS, open issues, and a machine-readable equivalence/config contract consumable by Lane D.

## Hard stops

Stop and request review if fixing a failed promotion gate requires changing Line MSHR/per-address cap/L1/lower resources, descriptor lifetime semantics, workload/trace, Lane A runtime state, or accepting an unexplained D256 timing mismatch.

Do not implement RO/TVD/Unified or silently promote D512 to the primary baseline.
