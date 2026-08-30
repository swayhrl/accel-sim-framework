# EP-L2 Lane B — Descriptor-512 Acceptance Criteria

This file is the authoritative self-gating contract for Lane B.

Codex may autonomously diagnose, repair, recommit, rebuild, and rerun **within Lane B's authorized parameterization/config/analysis scope** until all mandatory gates pass. A failed gate is not a reason to stop unless fixing it crosses a hard boundary below.

## B0. Source identity and isolation — mandatory

PASS only if:

```text
base Framework == exact C7e formal Framework source
base Core      == exact C7e formal Core source
Lane A worktrees were never modified/rebuilt/cleaned
Lane B has independent worktrees/branches/result roots
all D512 runs record source SHA + config hash + trace identity
```

Current expected formal anchors:

```text
Framework f08d2ce857972fad73c4e1ab7162ba94c6336507
Core      ece1a3a77c5628763e0a4605bfd1c639ee6a1495
```

If Lane A publishes a superseding exact-final source pair before Lane B freezes, reconcile against the formal campaign manifest rather than guessing.

## B1. Authorized experimental delta — mandatory

D512 changes exactly:

```text
shared persistent descriptor capacity: 256 -> 512
```

These remain unchanged:

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

Before D512 simulation, audit all source and tooling assumptions for capacities above 256.

Must explicitly inspect and document:

```text
allocator/free descriptor IDs
allocation/release lifetime
pool-full condition
per-address cap independence
occupancy/max/invariant arithmetic
histogram/vector bounds
p95/max implementation
kernel/app/window delta state
parser/schema/analyzer numeric handling
review-pack scripts/tests
```

Search for hard-coded `256`, `257`, or equivalent bit widths/bounds whose semantic role is descriptor capacity.

PASS only if either:

```text
A. existing code is already parameter-safe for 512
```

or:

```text
B. all required changes are parameterization/observation-only and B3 equivalence passes
```

## B3. D256 backward-equivalence after any code generalization — mandatory when source changes

Configure generalized code back to the exact D256 formal settings.

Use at least:

```text
vectorAdd_4M
spmv
one longer descriptor-heavy workload: scan or FWT_7_21
```

Compare against exact C7e D256 reference.

Require exact equality for:

```text
gpu_tot_sim_cycle
terminal instruction count
successful DRAM read/write transactions
selected L2 request/miss counts
bank logical/conflict/wait counters
terminal invariants
```

Descriptor telemetry may differ only in formatting/schema if the semantic value is identical.

Any unexplained simulated timing difference is a HARD STOP.

## B4. Boundary-directed descriptor tests — mandatory

Add/retain directed tests that exercise descriptor capacity boundaries without depending on long natural traces.

At minimum validate behavior around:

```text
used = 255 / 256 / 257 under D512
used = 511 / 512
attempt allocation at full pool
release one descriptor and allocate again
reuse descriptor IDs without double ownership
multiple addresses sharing the pool
one address hitting the independent 32/address cap while global pool remains available
```

Required assertions/evidence:

```text
no out-of-bounds telemetry histogram access
no descriptor leak
no duplicate live ownership
free + used == configured capacity at valid checkpoints
pool-full only at configured global capacity
per-address-cap remains 32 and is not silently widened
terminal descriptor_used == 0
```

## B5. Build and regression — mandatory

PASS only if final Lane B source has:

```text
full Release build PASS
relevant existing C3-C7/C6d/C7e descriptor regressions PASS
new D512 boundary tests PASS
parser/schema tests PASS
analyzer tests PASS
git diff --check PASS
clean frozen source worktrees
```

If new telemetry is added, apply the universal timing-neutral instrumentation gate from `PARALLEL_NEW_WINDOW_BOOTSTRAP.md`.

## B6. D512 natural preflight — mandatory

Run at least:

```text
vectorAdd_4M
scan
spmv
FWT_7_21
one low-descriptor-pressure control: sad or btree
```

Prefer B0-Banked for fast screening; use Legacy paired control where needed to ensure no unexpected bank/port interaction.

For every run require:

```text
COMPLETE_VALID
normal exit
expected source/config hashes
terminal_clean = 1
payload consistency = 1
parser success
all C7e telemetry families present
```

The preflight must report, not assume:

```text
cycles D256 vs D512
descriptor need/block/avg/p95/max
Line-MSHR avg/p95/max/full
per-address-cap
L1 pressure
L2->DRAM/scheduler/BW
5K temporal movement
```

## B7. D512_READY gate — mandatory before full mirror

Codex may declare exactly:

```text
D512_READY
```

only if B0-B6 pass and no modeled variable except descriptor capacity differs.

Update workboard:

```text
D512-AUDIT = DONE
D512-PREFLIGHT = DONE
```

with exact source/config/result paths.

This handshake authorizes Lane C to consume the exact D512 source/config for D512 L1 interaction cells.

## B8. Full speculative D512 mirror — mandatory target after D512_READY

Launch:

```text
13 workloads x {B0-Legacy, B0-Banked} @850 MHz
Descriptor = 512
```

Label every result:

```text
SPECULATIVE_CALIBRATION
```

not `FORMAL` and not `PRIMARY_BASELINE`.

All 26 runs must use one frozen Lane B source/config pair unless a proven simulator defect forces a restart. Parser/analyzer-only fixes may reprocess raw logs without rerunning simulator jobs when producer data is sufficient.

## B9. Mirror completion — mandatory

PASS only if:

```text
26/26 COMPLETE_VALID
single frozen source pair
single intended D512 config family
all manifests/provenance consistent
all terminal invariants clean
no missing expected telemetry
analysis-ready comparison to D256 generated
```

Do not declare D512 the primary baseline. Final status is:

```text
D512_MIRROR_COMPLETE
```

and requires later `BASELINE-DECISION` review.

## B10. Required interpretation output

For every workload report:

```text
D256 cycles
D512 cycles
speedup/slowdown
descriptor block/need change
descriptor occupancy distribution change
Line-MSHR pressure change
L1 pressure change
lower/scheduler/BW change
whether bottleneck moved rather than disappeared
```

Classify evidence conservatively:

```text
DESCRIPTOR_CAUSAL_SENSITIVE
DESCRIPTOR_THROTTLE_MOVES_DOWNSTREAM
DESCRIPTOR_PRESSURE_LOW_PERF_SENSITIVITY
D512_STILL_DESCRIPTOR_LIMITED
INSUFFICIENT_EVIDENCE
```

## B11. Review pack / return path — mandatory

Create a directly browsable pack such as:

```text
docs/ep_l2/review_packs/D512_CALIBRATION_r1/
```

with source anchors, config hashes, changed files, equivalence evidence, boundary tests, preflight, 26-run status, comparison tables, raw-log index, SHA256SUMS, and open issues.

Update:

```text
docs/ep_l2/codex_handoff/LANE_B_LATEST.md
```

and the Lane B rows in `PARALLEL_WORKBOARD.md`.

## Hard stops

Stop and request review if completion would require:

```text
changing Line MSHR/per-address cap/L1/lower resources
changing descriptor lifetime/semantics rather than capacity/parameterization
accepting unexplained D256 equivalence mismatch
changing workload/trace
modifying Lane A formal worktrees
silently promoting D512 calibration to formal baseline
```
