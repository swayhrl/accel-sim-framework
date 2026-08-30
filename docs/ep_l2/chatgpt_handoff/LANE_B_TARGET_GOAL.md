# EP-L2 Codex Target Goal — Lane B Descriptor-512 Calibration

## One-line goal

> Starting from the exact C7e formal pair and the frozen D512 candidate, maximize wall-clock efficiency by running remaining validation, D512 preflight and the full 13x2 mirror concurrently where safe; keep early outputs provisional until promotion gates pass; self-repair within Lane-B scope until `D512_READY` and `D512_MIRROR_COMPLETE` are both achieved; then STOP before baseline promotion or RO/TVD/Unified.

## Read order

From `/workspace/worktrees/accel-sim-ep-l2/` fetch/pull latest `hrl/ep-l2-exp-v0`, then read:

```text
docs/ep_l2/chatgpt_handoff/CURRENT_STATE.md
docs/ep_l2/chatgpt_handoff/INTERIM_22OF26_CHATGPT_REVIEW.md
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
docs/ep_l2/chatgpt_handoff/PARALLEL_MASTER_PLAN.md
docs/ep_l2/chatgpt_handoff/SPECULATIVE_PARALLEL_EXECUTION_POLICY.md
docs/ep_l2/chatgpt_handoff/PARALLEL_NEW_WINDOW_BOOTSTRAP.md
docs/ep_l2/chatgpt_handoff/LANE_B_DESCRIPTOR512_HANDOFF.md
docs/ep_l2/chatgpt_handoff/LANE_B_DESCRIPTOR512_ACCEPTANCE_CRITERIA.md
docs/ep_l2/chatgpt_handoff/LANE_B_CHATGPT_INTERIM_REVIEW.md
```

## Frozen candidate

Use exact immutable candidate identity for all newly launched speculative D512 work unless a gate failure forces a superseding candidate:

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
```

Do not rebuild or modify the active Lane-A worktrees. Do not disturb the running `scan` D256 equivalence job.

## Execute now — do not wait for scan

Continue the live `scan` D256 equivalence in parallel with:

```text
1. D512 preflight-priority workloads;
2. the full 13 x 2 D512 speculative mirror;
3. >256 telemetry validation.
```

Prefer scheduling the preflight workloads first inside the same frozen mirror so completed mirror rows double as preflight evidence.

Every early D512 run must record:

```text
maturity = SPECULATIVE_PENDING_GATE
promotion_dependencies:
  - D256_EQ_SCAN_PASS
  - D512_PREFLIGHT_PASS
```

A locally `COMPLETE_VALID` result is still provisional until promoted.

## Promotion / invalidation loop

If `scan` D256 equivalence and D512 preflight PASS, promote exact matching already-computed rows without rerun.

If an upstream gate finds a source/config/producer/timing defect, mark affected descendants `INVALIDATED_BY_UPSTREAM_GATE`, repair within Lane-B scope, freeze a new candidate identity, and rerun affected descendants. Do not stop merely because speculative compute must be discarded.

If the failure is parser/packaging-only and producer output is valid, reprocess rather than rerun simulator jobs.

## Target-mode self-repair

Allowed autonomous repairs:

```text
descriptor-capacity parameterization/telemetry generalization
D512 overlay/config-diff enforcement
runner/provenance/maturity plumbing
parser/analyzer/schema/test/review-pack fixes
```

Not allowed:

```text
Line MSHR change
per-address cap change
L1/WAD/Payload/bank/lower change
descriptor lifetime/functional semantic change
trace/workload change
Lane-A runtime modification
```

## Completion states

Lane B completes only when:

```text
D512_READY
D512_MIRROR_COMPLETE
```

both satisfy the original acceptance criteria. `D512_MIRROR_COMPLETE` requires all 26 rows promoted, not merely computed.

## Outputs

Push source on Lane-B branches and mirror documentation-only outputs to coordination:

```text
docs/ep_l2/codex_handoff/LANE_B_LATEST.md
docs/ep_l2/review_packs/D512_CALIBRATION_r1/
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
```

Publish exact candidate lineage/equivalence/config contract for Lane C/D.

Then STOP before `BASELINE-DECISION` or functional mechanism work.
