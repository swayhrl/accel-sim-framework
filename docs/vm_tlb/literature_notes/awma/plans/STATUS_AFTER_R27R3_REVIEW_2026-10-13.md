# AWMA status after R27R3 independent review

Review date: 2026-10-13 (Asia/Shanghai)

This supersedes `STATUS_AFTER_R27R3_AUTHORIZATION_2026-10-13.md` only for the **current AWMA state**, without amending any historical branch, raw data or contract.

## Current execution and accepted conclusion

- Lane G / node109 R27R3: **COMPLETE / STOP**.
- Accepted decision: `R27R3_B0_REFERENCE_NOT_REPEATABLE`.
- Gate A: PASS, accepted R27R2 bank/raw identity and R26 start reused under bounded recheck.
- Gate B1: **FAIL**. Two fresh-process unchanged B0 controls at B1, bank k=0, do not meet the fixed BF16 complete-gradient elementwise `atol=rtol=1e-2` contract: 25 / 262668288 entries exceed tolerance, located in input token rows 198 (12 elements) and 284 (13 elements). Other required observables pass; all tensors finite.
- Gate B2 component attribution, candidate correction, new four-step numeric requalification, freeze, capacity, 32-step/resume and allocator diagnostics: **NOT RUN**.
- No new AWMA GPU Goal authorized after this review. No automatic R27R4, baseline replacement, precision/tolerance revision or capacity retry.

## Exact version and evidence

Execution branch: `hrl/awma-r27r3-numeric-attribution-capacity-109-v1`.

Execution commit: `7bd31fae4c54e121d54743a803d978ee02a64959`.

Execution tree: `bcd3a9ab5890a946d03a49b46df4434abff4238c`.

Exact handoff parent: `29ce051f982f3854bd4392a94e4195c59340123b`.

Independent scientific review:
[`R27R3_B0_REFERENCE_REPEATABILITY_REVIEW_2026-10-13.md`](../empirical/R27R3_B0_REFERENCE_REPEATABILITY_REVIEW_2026-10-13.md).

Execution review pack:
https://github.com/swayhrl/accel-sim-framework/tree/7bd31fae4c54e121d54743a803d978ee02a64959/docs/vm_tlb/review_packs/AWMA_R27R3_NUMERIC_ATTRIBUTION_CONDITIONAL_CAPACITY_109_V1.

Independent reviewer verified 20/20 Git review-pack SHA256 entries and rechecked the reported 25 failing coordinates/thresholds/index formula; it did not independently read back the ~6.31GB two raw control tensors from node164. Node164 21-item manifest, archive hashes, GPU lock and process closure remain execution receipts.

## Scientific interpretation

R27R3 establishes **a same-input, same-start B0 numerical-repeatability qualification failure under the frozen per-element metric**. It is not a proof that the implementation computes mathematically wrong outputs, not an explanation of the kernel-level cause, and not proof that C1/S2 are correct or faulty. R27R2's C1/S2-vs-B0 failure remains its original accepted negative qualification, now with a demonstrated reference-repeatability confound; do not retroactively rewrite either result.

R26's accepted physical-batch one-step extension in a separate repeated-sequence tied-W five-step protocol remains unchanged; no varied-input capacity measurement exists.

The next possible bounded scientific problem is baseline determinism / gradient semantics and the validity of numerical equivalence requirements in BF16 training. It requires independent authorization and a preregistered plan. Do not automatically launch another GPU diagnostic, profiler, new data or hardware mechanism.

## Cross-project coordination

New `hrl/ai-workload-research-coordination` is a read-only scientific planning/evidence-navigation branch, not a merged experimental code base. This independent review is eligible for entry `E-A13` under P08/P09 once cross-project coordination documentation is updated, without changing C16, AWMA lane contracts or GPU permissions.

C16 Stage A/Reset and DTC-L1 remain scientifically separate. Current AWMA node109 lock is not granted to any coordination task.
