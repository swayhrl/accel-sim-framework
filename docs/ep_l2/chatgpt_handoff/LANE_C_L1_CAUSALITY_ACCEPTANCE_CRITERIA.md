# EP-L2 Lane C — L1 Causality Acceptance Criteria

This is the authoritative self-gating contract for Lane C.

Lane C is a causality/calibration experiment, not an L1 redesign. Execution scheduling also follows:

```text
docs/ep_l2/chatgpt_handoff/SPECULATIVE_PARALLEL_EXECUTION_POLICY.md
```

Speculative launch does not weaken any acceptance/promotion criterion below.

## C0. Source identity and isolation — mandatory

PASS only if:

```text
D256 cells derive from exact C7e formal source/config semantics
Lane A and Lane B active worktrees/binaries/results remain untouched
Lane C has isolated worktrees/branches/result roots
all runs record Core/Framework SHA, config hash, trace, L1 class and descriptor capacity
```

For D512 cells, Lane C must consume the exact Lane-B D512 candidate; it may not implement a second D512 definition.

Current speculative Lane-B candidate:

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
```

## C1. Frozen L1 geometry — mandatory

Across first-stage cells keep:

```text
capacity = 64 KiB
sets = 4
ways = 128
line = 128 B
latency = 20 cycles
```

No L1 capacity/associativity/line-size/latency change is allowed.

## C2. Authorized cells

### D256 + META-HR

Only:

```text
MSHR 512 -> 1024
merge cap 8 -> 32
MissQ 16 -> 64
banks stays 4
```

### D256 + BANK-HR

Only:

```text
banks 4 -> 8
MSHR/merge/MissQ stay baseline
```

### D512 interaction cells

Use the exact frozen Lane-B candidate plus exactly one Lane-C headroom class:

```text
D512 + META-HR
D512 + BANK-HR
```

No other modeled resource changes.

## C3. Base reproduction — mandatory

Before interpreting Lane-C results, prove the Lane-C D256 BASE path reproduces exact C7e B0-Banked behavior on at least vectorAdd_4M, spmv and one longer selected workload. Require exact cycles/instructions/selected L2/DRAM counters/invariants.

Observation-only instrumentation changes require exact baseline timing neutrality.

## C4. Effective-config delta audit — mandatory

Every cell emits a machine-readable effective-config map and diff.

Require exactly:

```text
D256 META-HR: l1_mshr_entries, l1_merge_cap, l1_missq_entries
D256 BANK-HR: l1_bank_count
D512 META-HR: descriptor_pool_size + META-HR fields
D512 BANK-HR: descriptor_pool_size + l1_bank_count
```

No hidden changes are accepted. The contract must bind to the actual run runtime-config hash and be compatible with Lane D's calibration input contract.

## C5. L1 telemetry correctness — mandatory if code/counters change

Prefer existing C7e L1D counters. Any new/changed field requires a semantic map with event/retry/unique semantics, exact increment point, denominator, scope, reset/delta behavior, directed path test and natural timing-neutral smoke.

Never reinterpret retry/stall attempts as unique-request failure probabilities.

## C6. Build/regression — mandatory

Require Release build, relevant C7e/L1 regressions, config-delta tests, any counter/parser tests, `git diff --check`, and clean frozen experiment worktrees.

## C7. D256 screening — mandatory and independent

Initial workloads:

```text
vectorAdd_4M
scan
spmv
convolutionSeparable
btree
sad
FWT_7_21
```

Complete all seven D256 META-HR and all seven D256 BANK-HR runs unless a proven common producer defect invalidates the lane.

Each run requires local `COMPLETE_VALID`, exact source/config identity, terminal_clean=1, payload consistency, parser success and required telemetry.

### Per-workload early decomposition

Lane C does not need to wait for all seven META-HR runs before launching one-at-a-time follow-up. As soon as one workload has a valid BASE and META-HR result showing the material-response trigger (>~5% or strong downstream-pressure movement), it may launch:

```text
MSHR-only
merge-only
MissQ-only
```

for that workload in parallel with remaining screening runs.

These decomposition runs still require all normal config/provenance checks.

## C8. Causality analysis — mandatory

For each workload/cell compare cycles/speedup, L1 blockers/accesses/misses, L2 descriptor/MSHR pressure, lower traffic, L2->DRAM/scheduler/native-BW where available, and 5K temporal behavior.

Classify only with performance + downstream movement:

```text
L1_NOT_CAUSAL
L1_LOCAL_BOTTLENECK
L1_MASKS_L2
BOTTLENECK_MOVES_DOWNSTREAM
MIXED_OR_INSUFFICIENT
```

## C9. One-at-a-time decomposition — mandatory for material META-HR responses

For sensitive workloads run MSHR-only, merge-only and MissQ-only at the relevant descriptor base. This remains required before `BASELINE-DECISION`.

## C10. D512 interaction — speculative launch now authorized

Lane C no longer has to wait three hours for Lane B to declare `D512_READY` before spending compute.

It may start D512 META-HR/BANK-HR now from the exact frozen Lane-B candidate above, in isolated Lane-C worktrees/results.

Until Lane B publishes `D512_READY`, every such run is:

```text
maturity = SPECULATIVE_PENDING_GATE
promotion_dependencies:
  - D256_EQ_SCAN_PASS
  - D512_PREFLIGHT_PASS
```

If Lane B later passes both gates, exact matching Lane-C rows may be promoted without rerun. If Lane B changes candidate source/config after a source/config/producer/timing defect, all dependent Lane-C D512 rows are `INVALIDATED_BY_UPSTREAM_GATE` and must be rerun from the superseding candidate.

A packaging/parser-only Lane-B failure does not automatically require simulator rerun if raw output remains valid.

## C11. Review pack / return path

Create/update:

```text
docs/ep_l2/review_packs/L1_CAUSALITY_CALIBRATION_r1/
docs/ep_l2/codex_handoff/LANE_C_LATEST.md
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
```

Include source/config anchors, effective-config contracts/diffs, base reproduction, run status + maturity/promotion dependencies, D256 and D512 comparisons, one-at-a-time results, causality classifications, raw-log index, SHA256SUMS and open issues.

## Completion

`L1_CAUSALITY_SCREEN_COMPLETE` requires all mandatory D256 evidence and all required D512/decomposition evidence to be **promoted valid**, not merely computed speculatively.

Lane C must not independently change the primary L1 baseline.

## Hard stops

Do not change L1 capacity/assoc/line/latency, change other L2/DRAM resources, accept unexplained baseline mismatch, alter workloads/traces, modify Lane A/B active worktrees, or rewrite event semantics to obtain a desired conclusion.
