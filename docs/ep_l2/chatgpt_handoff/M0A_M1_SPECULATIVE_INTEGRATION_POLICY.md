# EP-L2 M0a + M1 Speculative Integration Policy

Status: **PREAUTHORIZED ONLY AFTER CHATGPT INTERIM SOURCE REVIEW**

## Objective

Reduce wall-clock delay while the final long M0a/M1 validation workloads finish.

If both interim checkpoints demonstrate that:

```text
- exact M0a and M1 source candidates are frozen and remotely auditable;
- remaining work is validation only;
- M0a is observation-only on completed evidence;
- M1 is behavior-preserving on completed evidence;
- no unexplained source/config/timing mismatch exists;
```

then ChatGPT may authorize a speculative integration child before the remaining long rows finish.

## Promotion semantics

A speculative integration child must carry:

```text
maturity = SPECULATIVE_PENDING_GATE
promotion_dependencies = [M0A_FINAL_PASS, M1_FINAL_PASS]
```

Computation may proceed; accepted evidence promotion may not.

If either parent later fails because of a source/producer/timing semantic defect, affected integration descendants are invalidated and rebuilt/rerun from repaired source.

Parser/package/report-only fixes may be reprocessed without simulator rerun when exact runtime source/config remains unchanged.

## Integration source rule

Create a new clean integration branch/worktree from the exact frozen M1 candidate, then port/cherry-pick only the exact accepted M0a observation changes.

Do not reuse either live parent worktree as the integration worktree.

Suggested names:

```text
Framework: /workspace/worktrees/accel-sim-ep-l2-m0a-m1-int/
Core:      /workspace/worktrees/gpgpu-sim-ep-l2-m0a-m1-int/
branch:    hrl/ep-l2-m0a-m1-int-v0
results:   /workspace/results/ep_l2_m0a_m1_int/
```

## Allowed speculative integration work

Before final parent promotion, the integration child may:

```text
resolve mechanical source/config overlap
Release build
run directed M0a field tests
run directed M1 payload/ownership/lifecycle tests
run config/mode-switch tests
run short natural BASE/OFF equivalence smoke
run short M0a-ON timing-neutrality smoke
prepare parser/analyzer/manifest integration
prepare M0b observation scaffolding that does not change functional behavior
```

## Not allowed before both final parent gates

Do not:

```text
declare integrated source accepted
use integration output as formal/calibration evidence
start Unified/RO/TVD functional behavior
run performance-headroom experiments
change the calibrated base-resource configuration
publish a mechanism performance claim
```

## M0b boundary

M0b implementation may be prepared speculatively on the integration child only after ChatGPT explicitly authorizes the child following interim review.

M0b remains observation/shadow only. No functional mechanism is enabled.

Final M0b evidence promotion requires the integrated parent itself to be promoted after both `M0A_FINAL_PASS` and `M1_FINAL_PASS`.

## Rationale

The remaining long runs are validation gates, not scientific definitions of the M0a/M1 source candidates. When source identity is frozen, dependency gates should control evidence promotion rather than unnecessarily idle compute.
