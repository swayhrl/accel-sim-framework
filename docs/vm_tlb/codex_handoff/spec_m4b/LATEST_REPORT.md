# Window C — SPECULATIVE M4B DEVELOPMENT current handoff

Status: `SPECULATIVE_CANDIDATE` / `REFERENCE_APPROX_SUBENTRY_16`.

C9 architecture is frozen. C10-A/C10-A2 implementation is complete. C10B-0 through C10B-5 have passed runtime validation, including standard regression, non-identity registration/lifecycle/access/ordering/generation tests, emitted telemetry, F5 physical PWC, and fair-arm sanity.

## Current validated C10B identity

Framework evidence closeout:

`28edd4e6c59691ea2b766f8221d0b0a1442ff167`

Core:

`5b4094931910cd3bb9b30df47a552eb0ae596983`

Validated binary SHA-256:

`74307f3a9b975300e469a7768be1324444c927498e3b19d40d39dc326df31345`

C10B final state was `C10B_HARD_BLOCKER_WITH_EVIDENCE`, but the blocker is C5 input provenance, not C10B model correctness. No C5 performance replay has run.

## C5 blocker

C5 cannot yet bind a fair full prefill+decode matrix because C lacks:

- a C-owned immutable full prefill trace-list;
- a legal C10 V2 prefill non-identity driver registration;
- a fully auditable common PA allocation binding across fair arms.

The old prefill V1 identity-like map and object map are not legal C10 Segment registrations.

## Current authorized Goal

`C11_C5_PREFILL_PROVENANCE_CLOSURE`

Read and execute:

- `docs/vm_tlb/codex_handoff/spec_m4b/C11_C5_PREFILL_PROVENANCE_CLOSURE.md`
- `docs/vm_tlb/codex_handoff/spec_m4b/C11_ACCEPTANCE_MATRIX.md`
- C10B final report / C5 preflight
- C9 Weight Segment architecture specification
- A terminal publication provenance checkpoint `14edbe200859f6ddf42bc3d459334f184a920a82`

A full-ROI trace-list identities are authoritative:

- prefill `a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f`
- decode1 `b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc`

C11 is input/provenance closure only. It may create explicit `MODELED_DRIVER_PA` artifacts under C9's modeled physical namespace using the frozen deterministic `C5_MODELED_PA_HIGH_UNUSED_BIT_V1` policy defined by the handoff. It must not claim modeled PPNs were measured hardware PAs, must not tune them from performance, and must apply one common driver PA mapping across conventional and Segment fair arms for each ROI.

C11 must prepare exact full C5 trace/config/registration/command/acceptance manifests but must not launch C5.

Final C11 status is one of:

- `C11_C5_INPUTS_CLOSED_READY_FOR_C5_REVIEW`
- `C11_HARD_BLOCKER_WITH_EVIDENCE`

`READY_FOR_C5_REVIEW` is not execution authorization.