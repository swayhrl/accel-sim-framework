# C10-B acceptance matrix

Goal: `C10B_POST_A_TERMINAL_BUILD_AND_RUNTIME_VALIDATION`

C10-B may start only after both:

- external A attestation first line is exactly `A_TERMINAL_CONFIRMED`;
- host resource gate is healthy for the requested step.

| Gate | Required PASS evidence | Blocks |
|---|---|---|
| G0 Admission | Framework `447ad52c...`, Core `12267bb7...`, clean explained worktrees, A terminal attestation, resource snapshot | all C10-B |
| G1 Compile/link | focused `-j1` compile plus required simulator/link success; compile errors root-caused/repaired without new architecture | runtime |
| G2 Standard regression | accepted standard VM/TLB/control semantics and exact-once/conservation regressions pass | all candidate results |
| G3 Registration/PA | non-identity PA, transactional rejection, zero-prefix fallback, conventional/Segment PPN agreement | Segment candidate |
| G4 Lifecycle | all-replica install/revoke ack, ACTIVE gating, ASID/epoch/context/wrap behavior | Segment candidate |
| G5 Access class | production READ/WRITE/ATOMIC routing verified end-to-end; write/atomic never Segment hit | Segment candidate |
| G6 Ordering | HIT_FIRST/MISS_JOIN scenarios, exactly-one lower launch, no duplicate completion/reprobe, mismatch detection | Segment candidate |
| G7 Generation | exact/subentry stale fills and stale outcomes discarded after shootdown | fair TLB candidate |
| G8 Fair selector | F0/F1/F2/F3/F4/F6/F7/F8/F9 realized; F5 blocked until physical model; H0 rejected | fair comparison |
| G9 Telemetry | Segment + conventional + cross-layer counters emitted and conserved; no missing schema needed for pressure-shift analysis | performance interpretation |
| G10 F5 | physical 3x40, 4-way pointer-payload PWC implemented+validated, or explicitly remains blocked | F5 comparison only |
| G11 Focused sanity | bounded real/direct runs show intended realized config and no exact-once side-effect regressions | C5 authorization request |

Hard STOP conditions:

- standard-mode regression;
- Segment hit on write/atomic;
- identity-only PA shortcut reappears;
- `OBJECT_WEIGHT` controls eligibility;
- lower L2 launched before both Segment/L1 miss;
- duplicate completion/side effect/repeated Segment probe;
- stale fill after generation advance;
- partial registration visible after semantic rejection;
- lifecycle allows hit before all install acks or after revoke;
- F5/H0 accidentally selectable;
- provenance or telemetry conservation ambiguity.

Final state must be one of:

- `C10B_READY_FOR_C5_RESOURCE_GATED_REPLAY`
- `C10B_PARTIAL_WITH_NAMED_RUNTIME_BLOCKERS`
- `C10B_STANDARD_REGRESSION_FAILED`
- `C10B_ARCHITECTURE_CONTRADICTION_REQUIRES_DECISION`

No final state automatically authorizes C5.