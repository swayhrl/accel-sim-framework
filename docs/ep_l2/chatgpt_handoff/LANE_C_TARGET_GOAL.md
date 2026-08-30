# EP-L2 Codex Target Goal — Lane C L1 Causality

## One-line goal

> Maximize wall-clock efficiency by continuing D256 L1 causality work, launching per-workload decomposition as soon as triggered, and running D512×L1 interaction cells speculatively from the exact frozen Lane-B candidate before `D512_READY`; keep those descendants provisional until Lane-B promotion gates pass; self-repair within Lane-C scope until `L1_CAUSALITY_SCREEN_COMPLETE`; then STOP before primary-baseline changes or EP-L2 mechanisms.

## Read order

From `/workspace/worktrees/accel-sim-ep-l2/` fetch/pull latest `hrl/ep-l2-exp-v0`, then read:

```text
docs/ep_l2/chatgpt_handoff/CURRENT_STATE.md
docs/ep_l2/chatgpt_handoff/INTERIM_22OF26_CHATGPT_REVIEW.md
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
docs/ep_l2/chatgpt_handoff/PARALLEL_MASTER_PLAN.md
docs/ep_l2/chatgpt_handoff/SPECULATIVE_PARALLEL_EXECUTION_POLICY.md
docs/ep_l2/chatgpt_handoff/PARALLEL_NEW_WINDOW_BOOTSTRAP.md
docs/ep_l2/chatgpt_handoff/LANE_C_L1_CAUSALITY_HANDOFF.md
docs/ep_l2/chatgpt_handoff/LANE_C_L1_CAUSALITY_ACCEPTANCE_CRITERIA.md
```

## Execute immediately

Continue/complete:

```text
D256 + L1 META-HR: 7 workloads, B0-Banked
D256 + L1 BANK-HR: 7 workloads, B0-Banked
```

As soon as any META-HR workload triggers material sensitivity, launch its MSHR-only / merge-only / MissQ-only decomposition immediately; do not wait for the full seven-workload screen.

## Speculative D512 interaction — start now

Use exactly:

```text
Lane-B Core candidate:
878f80869ce212e779df20b6421e4dc7f987825d

Lane-B Framework candidate:
aae62b66685f15437cecf0193934f628e6fac6ae
```

Create isolated Lane-C descendants and launch:

```text
D512 + META-HR × 7
D512 + BANK-HR × 7
```

without waiting for Lane B's long `scan` equivalence or `D512_READY`.

Every such run records:

```text
maturity = SPECULATIVE_PENDING_GATE
promotion_dependencies:
  - D256_EQ_SCAN_PASS
  - D512_PREFLIGHT_PASS
```

Do not recreate D512 locally or modify Lane-B worktrees.

## Promotion / invalidation

If Lane B publishes `D512_READY` for the exact candidate above, promote exact matching completed Lane-C D512 rows without rerun.

If Lane B changes candidate source/config after a source/config/producer/timing failure, invalidate dependent D512×L1 rows and rerun them from the superseding candidate. Continue target mode; wasted speculative compute is acceptable under this policy.

Packaging/parser-only upstream failures may be reprocessed if producer data remain valid.

## Self-repair boundary

Allowed:

```text
isolated L1 config overlays
runner/provenance/maturity plumbing
observation-only L1 telemetry fixes if required
parser/analyzer/tests/review packaging
one-at-a-time decomposition
```

Not allowed:

```text
L1 capacity/assoc/line/latency changes
independent D512 implementation
other L2/DRAM resource changes
Lane A/B active runtime modification
functional RO/TVD/Unified
```

## Completion

Complete only when:

```text
L1_CAUSALITY_SCREEN_COMPLETE
```

is supported by the acceptance criteria and all required D512 descendants are promoted valid rather than merely computed.

## Outputs

Mirror:

```text
docs/ep_l2/codex_handoff/LANE_C_LATEST.md
docs/ep_l2/review_packs/L1_CAUSALITY_CALIBRATION_r1/
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
```

Then STOP before `BASELINE-DECISION` or functional mechanism work.
