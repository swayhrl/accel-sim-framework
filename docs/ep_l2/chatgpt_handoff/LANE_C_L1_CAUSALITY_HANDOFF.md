# EP-L2 Lane C — L1 Causality / Headroom Handoff

Owner: dedicated Codex Window C.

## Objective

Determine whether observed L1D pressure is:

```text
1. an independent L1-local bottleneck,
2. mostly downstream backpressure from L2/DRAM,
3. or an upstream throttle that materially masks L2 opportunity.
```

Do not enlarge L1 capacity. Keep hit-rate/capacity semantics fixed and vary only authorized flow-control or bank-throughput resources.

## Scheduling mode

Follow `SPECULATIVE_PARALLEL_EXECUTION_POLICY.md`: unresolved upstream validation gates may block promotion without blocking computation.

## Base / isolation

D256 cells use exact C7e formal semantics. Never modify Lane A or Lane B active runtime directories.

Suggested Lane C worktrees:

```text
/workspace/worktrees/accel-sim-ep-l2-l1-causality/
/workspace/worktrees/gpgpu-sim-ep-l2-l1-causality/
```

Initial experiments are B0-Banked only unless a paired Legacy control is needed.

## Workload set

```text
vectorAdd_4M
scan
spmv
convolutionSeparable
btree
sad
FWT_7_21
```

## Frozen L1 geometry

```text
capacity = 64 KiB
sets = 4
ways = 128
line = 128 B
latency = 20 cycles
```

## D256 cells — continue immediately

### META-HR

```text
MSHR 512 -> 1024
merge cap 8 -> 32
MissQ 16 -> 64
banks = 4
```

### BANK-HR

```text
banks 4 -> 8
MSHR = 512
merge = 8
MissQ = 16
```

Run all seven workloads.

## D512 interaction cells — now authorized speculatively

Current frozen Lane-B D512 candidate:

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
```

Lane C may start now:

```text
D512 + META-HR
D512 + BANK-HR
```

on the same seven B0-Banked workloads without waiting for Lane B's long `scan` equivalence or final `D512_READY` declaration.

These runs must derive from the exact candidate above and remain:

```text
SPECULATIVE_PENDING_GATE
promotion_dependencies:
  D256_EQ_SCAN_PASS
  D512_PREFLIGHT_PASS
```

If Lane B promotes the same exact candidate to `D512_READY`, Lane C can promote matching completed results without rerun. If Lane B supersedes the candidate after a source/config/producer/timing failure, dependent rows are invalidated and rerun.

Do not create an independent D512 implementation.

## Experimental matrix

```text
                         L1 BASE       L1 META-HR       L1 BANK-HR
Descriptor 256          formal data    Lane C run       Lane C run
Descriptor 512          Lane B run     Lane C run       Lane C run
```

## Per-workload decomposition — pipeline it

For a workload whose META-HR result becomes available and is materially sensitive (>~5% cycle response or strong downstream-pressure shift), immediately launch in parallel:

```text
MSHR-only  512 -> 1024
merge-only 8 -> 32
MissQ-only 16 -> 64
```

Do not wait for the other six screening workloads before starting that workload's decomposition.

## Measurements / interpretation

Compare cycles/speedup plus L1 accesses/misses/blockers, L2 tag/MSHR/descriptor/cap/WAD/payload/bank, L2->DRAM/scheduler/ReturnQ, native DRAM BW when available, and 5K temporal pressure.

Do not treat retry counts as unique-request probabilities or occupancy alone as causality.

Use the causal classes and detailed gates in `LANE_C_L1_CAUSALITY_ACCEPTANCE_CRITERIA.md`.

## Deliverables

Maintain:

```text
docs/ep_l2/codex_handoff/LANE_C_LATEST.md
docs/ep_l2/review_packs/L1_CAUSALITY_CALIBRATION_r1/
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
```

Every provisional D512 row records exact candidate identity, local run status, maturity and promotion dependencies.

## Completion / boundary

`L1_CAUSALITY_SCREEN_COMPLETE` requires promoted evidence, not just completed speculative computation.

Do not change L1 capacity/assoc/line/latency, independently alter descriptor semantics, implement RO/TVD/Unified, or declare the primary baseline.
