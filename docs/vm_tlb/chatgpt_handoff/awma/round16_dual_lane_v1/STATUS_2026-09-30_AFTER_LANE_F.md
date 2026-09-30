# Round16 status after Lane F closeout

Date: 2026-09-30

## Lane F / VLA RTC-VJP

Execution authority:
- branch: `hrl/awma-vla-rtc-vjp-boundary-109-v1`
- commit: `f8e6e2598e51dae115008a52c9a80110cdf14d83`
- tree: `ef54c9b3156e5ec4248a823ff9d0145dfce7ae86`

Accepted decision:

`VLA_VJP_RESULT_MIXED_NEEDS_REVIEW`

### Accepted facts

- Pinned upstream LeRobot RTC source produced identity-only VJP in 9/9 analytic canaries under the actual wrapper context.
- One permitted semantic repair (establishing input grad before denoiser evaluation) restored the full analytic Jacobian in 9/9.
- The repaired SmolVLA guided path executed 10 full network VJPs through the action expert with frozen weights and zero parameter gradients.
- A0 guided complete-chunk median: 231.912634 ms.
- Diagnostic 10-call VJP interval: ~98.88 ms; this includes mandatory VJP math plus unresolved state/lifetime work and is not a removable-cost estimate.
- A1 fixed-buffer/prefix-weight reuse: 232.688743 ms, numerically exact to A0; no material speedup.
- Author-supported torch.compile/max-autotune did not qualify on the exact path (CUDA misaligned address); no mode scan was performed.
- State/lifetime-only complete-chunk headroom remains UNKNOWN.
- One NSYS attempt produced no report; no NCU target was guessed.
- Episode B remained sealed.

### Interpretation

This stage establishes a real and substantial **inference-time VJP workload phenomenon** on the repaired RTC semantics.

It does **not** establish:
- a >5% removable state/lifetime residual;
- a memory bottleneck;
- an activation-cache opportunity;
- a VLA hardware mechanism candidate.

The upstream semantic gap is a software correctness/implementation issue and must not be counted as an architecture speedup opportunity.

Current disposition:

`VLA_VJP_WORKLOAD_REAL_ARCH_RESIDUAL_NOT_QUALIFIED`

This disposition is a coordination summary, not a replacement for the formal execution label.

Reopen only if a new bounded experiment can isolate a target state/materialization cost from mandatory VJP math without weakening the RTC algorithm/numerical contract. Do not reopen merely to repair NSYS or search profiler counters.

## Round16 primary lanes

- Lane F: COMPLETE / STOP.
- Lane G R102: COMPLETE / DORMANT waiting for real update authority.
- Lane E: STOP.

No VLA/R102 architecture mechanism or 174 simulation is authorized.
