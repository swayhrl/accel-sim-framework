# C14 Path P prototype audit

Status: `NO_GO_WITH_EVIDENCE`

## Candidate A — Segment-before-L2 gated issue

No new timing mechanism was implemented because the C12 Core already has the
claimed gate.  In `translation_controller::cycle`, L1 and Segment service run
in parallel; a Segment hit completes the requester.  The L2 launch state is
entered only after *both* services have completed and missed.  The source
audit records the exact state transitions in
`COMMON_TRANSLATION_PATH_MAP.md` and `CURRENT_SEGMENT_RACE_TIMELINE.md`.

Therefore an additional “Segment-before-L2” prototype would be a duplicate
of the present control flow, not an optimization.  C14 P telemetry was added
only to falsify this conclusion at runtime.  Its fields show that every
observed Segment winner had `l2_not_issued=1`, `mshr_not_allocated=1`,
`ptw_not_started=1`, and `pte_not_issued=1`.

Decision: `NO_GO_WITH_EVIDENCE` — no redundant exact L2 admission exists on
the Segment-hit path to gate away.

## Candidate B — opportunistic cancel-before-admission

No cancel prototype was implemented.  The only exact work started before the
Segment result is the L1 lookup, whose port is consumed during requester
admission.  It has no reversible pre-admission handle.  L2 admission, MSHR
allocation, PWQ/walk launch, and PTE issue are downstream of the joint-miss
gate.  Once an MSHR exists it can have independent merged requesters, so
per-request cancellation would require a new ownership/refcount/liveness
contract rather than a local removal.

The only current “discard” is a logical late-shadow discard: it suppresses a
losing result from completing the requester; it does not undo a consumed L1
port or cancel shared work.  A purported cancellation implementation without
those new contracts would risk losing a requester or cancelling work owned by
another waiter.

Decision: `NO_GO_WITH_EVIDENCE` — no safe cancel boundary exists in the C12
implementation for this proposal.

## Observational instrumentation and non-perturbation

Core branch: `hrl/vm-m4b-c14-segment-positive-v0` at `ce05732b`.

- Configuration is default-off: `-gpgpu_vm_c14_segment_race_telemetry 0`.
- The counter-only path records admissions, Segment/L1/L2/PTW outcomes,
  Segment-winner L1 state, and terminal latency samples.  It neither changes
  service-ready cycles nor state transitions.
- The direct unit test runs telemetry off/on over a Segment hit and a
  fallback walk, and asserts equal ready cycles, completion behavior, and
  conventional resource outcomes.
- The runtime off/on pair for `P-AP-L7` has identical `gpu_tot_sim_cycle`
  (`138163`) and identical existing translation counters.  The telemetry-on
  run merely appends the C14 counter block.

This validates non-perturbation for the exercised direct and trace-replay
paths, not every possible simulator workload.
