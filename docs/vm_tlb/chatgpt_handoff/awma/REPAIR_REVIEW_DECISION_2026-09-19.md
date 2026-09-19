# ChatGPT Scientific Review — VM Per-Access Coverage Repair

Date: 2026-09-19

## Reviewed authority

Execution branch:
`hrl/awma-vm-per-access-coverage-repair-174new-v1`

Commit:
`3f7bc0cd3cb3667b38fa0dd803ac034e19b493d6`

Parent:
`be82faf264e93396b4b7d4fd72078c7e4491e3e4`

Ancestry:
repair commit is exactly one commit ahead of the expected global-access-determinism parent.

Report:
`docs/vm_tlb/codex_handoff/awma/VM_PER_ACCESS_COVERAGE_REPAIR_174NEW_V1_REPORT.md`

Review pack:
`docs/vm_tlb/review_packs/AWMA_VM_PER_ACCESS_COVERAGE_REPAIR_174NEW_V1/`

## Decision

`PER_ACCESS_VM_COVERAGE_DEFECT_CONFIRMED_REPAIR_QUALIFIED_FOR_REQUALIFICATION`

and

`MATERIAL_SCIENTIFIC_CHANGE_REQUIRES_MINIMAL_REBASELINE`

The repaired runtime is accepted as a correctness-qualified basis for requalification, not yet as the final research baseline.

## Why the defect proof passes

Legacy target-scoped coverage records:

- admissions: 3,090,304
- translated: 776,666
- untranslated: 2,313,638
- unobserved: 2,313,638

This directly observes downstream admission of VM-eligible accesses without translation.

## Why the repair contract passes with scope

The source guard checks the exact current accessq_back immediately before positive/zero-latency L1D and bypass-ICNT admission.

If untranslated:
- the queue entry is not popped;
- existing COAL_STALL behavior is returned;
- the next normal memory-cycle path applies the pre-existing VM helper.

Repaired P34:
- admissions: 3,090,304
- translated: 3,090,304
- untranslated: 0
- unobserved: 0
- post-ready retranslation attempts: 0

The patch does not intentionally change TLB/cache configuration, addresses, coalescing, or scheduler policy.

The effective downstream throughput may change because accesses previously bypassing the modeled translation gate can no longer do so. That is the expected consequence of restoring the existing translation model, not a new architecture mechanism.

## Material impact

P34 target completion cycles:

`871835 -> 1619068`

while gpu_sim_insn remains:

`368696302 -> 368696302`

Therefore old translation-dependent quantitative conclusions cannot be carried forward.

## Important scope caveat

The core VM coverage counters are explicitly target-kernel gated and are sufficient for the defect/repair proof.

However, the compact P34 impact matrix contains auxiliary counters whose scope is not proven target-only. In particular:

`walk_starts = 499`

does not match the historical P34 target-only walk count previously used in contextual analysis.

Likely explanation is whole-prefix cumulative telemetry versus target-delta telemetry, but this must be proven rather than assumed.

Therefore:
- do not reinterpret 499 as repaired Q05 target walks;
- do not compare auxiliary impact-table values to old target-only values until boundary scoping is reconciled.

## Additional qualification gaps to close during rebaseline

1. Durable repaired simulator binary SHA is not recorded in the Git review pack.
2. GLOBAL/LOCAL/PARAM_LOCAL coverage should be reconciled separately where source classification permits.
3. Target-only I0 was correctly deferred and must be made per-access clean before use.
4. MSHR/PWC/PTE/requester/DRAM target-scoped deltas need explicit collection during requalification.

These gaps do not overturn the direct undercoverage proof or the repaired zero-untranslated invariant.

## Authorized next stage

Proceed with:
- repaired runtime materialization and binary freeze;
- target-boundary telemetry reconciliation;
- minimal repaired Q05 requalification;
- existing cross-family evidence analysis;
- at most one conditional non-Attention repaired R0/I0 isolated screen.

Do not run architecture mechanisms or broad historical replay.
