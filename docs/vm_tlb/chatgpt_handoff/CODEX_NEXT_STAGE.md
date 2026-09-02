# CODEX_NEXT_STAGE — Track A

## Status

`M1_VM_CORE_FOUNDATION` has been reviewed by ChatGPT: **PASS**.

Resume the already-authorized target-mode macro task at **M2**, not M1.

Execution order now is:

1. `stage_specs/M2_FUNCTIONAL_TRANSLATION.md`
2. if M2 PASS, continue automatically to `stage_specs/M3_TIMING_REALISTIC_BASELINE.md`
3. after M3 PASS, create `review_packs/M1_M3_VM_BASELINE_CLOSEOUT/`
4. push, report, and STOP before M4B/Segmentation/synthetic-KV/new AI-aware mechanisms.

Read before execution:

1. `CURRENT_STATE.md`
2. `DISCUSSION_REFERENCE.md`
3. repository-root `AGENTS.md`
4. `stage_specs/M2_FUNCTIONAL_TRANSLATION.md`
5. after M2 PASS, `stage_specs/M3_TIMING_REALISTIC_BASELINE.md`

Do not modify `chatgpt_handoff/*`.

## Source anchors

Continue from the current pushed Track-A heads:

- Core branch: `swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`
- M1 Core commit: `82fa2bc79cf09dd137073431dc41e48bc2f30cec`
- Framework branch: `swayhrl/accel-sim-framework:hrl/vm-m1-m3-v0`

Use the existing isolated Track-A worktrees. Verify branch/remote cleanliness before source modification.

## M2 specific review emphasis

In addition to the existing M2 stage spec, preserve these review points:

- `SimPA` is not semantically valid merely because it contains a numeric initialization value; functional translation completion/validity must gate downstream use.
- A request that stalls on translation must not enter the data cache early.
- Replay must not retranslate an already completed request or duplicate load/store/atomic side effects.
- One `(ASID, VPN, page-size-class)` has at most one active walk.
- MSHR merge is not a TLB hit.
- finite L1/L2 TLB lookup throughput/resources, translation MSHR, PWQ, and walker capacity must affect behavior rather than statistics only.
- directed tests must assert expected counts and conservation, not merely exit 0.

## Reporting

Maintain:

`docs/vm_tlb/codex_handoff/m1_m3/LATEST_REPORT.md`

At M2 closeout, update the report and review pack. If M2 PASS, continue to M3 without waiting for another chat round. If M2 FAIL or any STOP condition occurs, push evidence and stop.

## STOP conditions

STOP immediately on any correctness invariant failure, baseline-transparency regression, request loss, duplicate wakeup, duplicate store/atomic effect, deadlock, unexplained nondeterminism, or ambiguity that materially changes the frozen VM semantics.

Do not weaken tests to continue.
