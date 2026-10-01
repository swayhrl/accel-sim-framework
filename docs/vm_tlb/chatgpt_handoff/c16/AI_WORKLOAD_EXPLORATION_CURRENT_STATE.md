# C16 AI-workload exploration current state

Date: 2026-10-01. Status: `EXPLORATION_WAVE_COMPLETE`.

Canonical terminal review pack:

`docs/vm_tlb/review_packs/C16_AI_WORKLOAD_EXPLORATION_WAVE_TERMINAL_SYNTHESIS_174NEW_V1/`

Project decision:

`NO_CURRENT_C16_MECHANISM_READY_FOR_PROMOTION`

There are zero active promotion candidates. One heterogeneous tile-handoff
question remains in a future-only parking lot without experiment authorization
or a current paper claim.

Key closed lines are current-scope residency/M1F, new cache-aware Split-K,
conversion-result cache, FFN materialization as the main opportunity,
two-stream gate/up performance, plain merged gate/up novelty, generic Ada W4
kernel stories, and replacement-policy/PASCAL cache mechanisms.

Two-stream V2 remains classified
`CONCURRENCY_ACTIVATED_BUT_RESOURCE_CONTENTION_LIMITED`: B0=74.2159 ms,
B1=81.4339 ms, speedup=0.91136x, with overlap in 10/112 windows. Resource
contention is directly observed through gate/up duration inflation, but is not
proven to explain the entire whole-decode slowdown; stream/event coordination
and limited realized overlap remain possible contributors.

This context authorizes no GPU, NCU, NVBit, SASS, trace, Accel-Sim or new
mechanism experiment. Resume only under a separately reviewed project goal.
