# CODEX NEXT STAGE — 174-new 20h Post-Repair Requalification Pipeline V1

Date: 2026-09-19

Status: ACTIVE AFTER USER LAUNCH

Mode: GOAL MODE / solve-and-continue

Node: 174-new

Coordination:
`hrl/awma-20h-unattended-pipeline-handoff-v1`

Read first:
1. CURRENT_STATE.md
2. DISCUSSION_REFERENCE.md
3. PIPELINE_ACCEPTANCE_CONTRACT_20H_V1.md
4. PIPELINE_SCHEDULER_POLICY_20H_V1.md
5. this file

## 0. Accepted upstream

Repair branch:
`hrl/awma-vm-per-access-coverage-repair-174new-v1`

Repair commit:
`3f7bc0cd3cb3667b38fa0dd803ac034e19b493d6`

Repair parent:
`be82faf264e93396b4b7d4fd72078c7e4491e3e4`

Decision:
`PER_ACCESS_VM_COVERAGE_DEFECT_CONFIRMED_REPAIR_QUALIFIED_FOR_REQUALIFICATION`

Do not rewrite repair or legacy packs.

Suggested execution branch:
`hrl/awma-repaired-vm-requalification-20h-174new-v1`

Create from repair commit.

## 1. Start/timing

At actual Goal start record START_UTC.
Set DEADLINE_UTC=START_UTC+20h.
Set NO_NEW_TARGET_AFTER=DEADLINE_UTC-2h.

Write timing policy into review pack.

## 2. M0 — Materialize repaired runtime and close telemetry scope

The repair pack qualifies the semantic repair, but does not bind a durable repaired binary SHA and the P34 impact
matrix contains auxiliary counters whose scope may be whole-prefix rather than target-only.

### M0.1 Rebuild/freeze

Materialize a clean isolated repaired runtime from the accepted source authority and exact accepted repair semantics.

Do not add mechanism changes.

Record:
- framework source SHA;
- core SHA;
- repair authority SHA;
- exact applied source diff;
- compiler/build environment;
- simulator binary SHA256.

### M0.2 Repair sanity

Reproduce a bounded P34 repaired R0 sanity sufficient to verify:
- target cycles consistent with the qualified repaired behavior;
- 3,090,304 target downstream admissions under same target identity if exact instrumentation is retained;
- zero untranslated/unobserved admissions;
- zero post-ready retranslation attempts.

If exact historical diagnostic instrumentation is not retained, prove equivalent accepted invariants.

### M0.3 Target-boundary telemetry

Implement timing-neutral boundary snapshot/delta reporting for Q05 target so the following are explicitly TARGET_DELTA:
- L1/L2 TLB accesses/hits/misses;
- MSHR;
- walks;
- PWC/PTE;
- requester latency;
- L2 data;
- DRAM;
- VM eligible accesses by GLOBAL/LOCAL/PARAM_LOCAL.

Do not alter scheduling/timing semantics.

Close admission/translation accounting separately by memory class where source classification permits.

Explicitly reconcile why the repair qualification impact table reports walk_starts=499 while historical P34 target-only
reporting used a different scope. Do not assume either is wrong before proving scope.

Deliver:
`TELEMETRY_SCOPE_RECONCILIATION.md`
`REPAIRED_RUNTIME_AUTHORITY.json`
`TARGET_BOUNDARY_DELTA_SCHEMA.md`

If telemetry cannot be made timing-neutral, STOP_SCIENTIFIC for quantitative requalification and continue only
independent CPU-only evidence analysis.

## 3. M1 — Minimal repaired Q05 requalification

Use same accepted context bundle/F0 architecture.

Required experiment identities:

### R1
`FORMAL_ISOLATED_REPAIRED_R0`

### R2
`FORMAL_ISOLATED_REPAIRED_I0`

I0 = ideal identity translation per eligible access.

### R3
`P34_REPAIRED_R0`

Reuse M0/repair run only if binary/input/config/scope all exactly match and target-delta telemetry is complete.
Otherwise rerun.

### R4
`P34_REPAIRED_Q05_ONLY_I0`

All predecessor members repaired natural R0.
Only Q05 uses I0.
No prefix idealization.

### R5
`P8_REPAIRED_R0`

Screen context trend with same-source target.

### R6
bounded target-scoped timeline sanity

Prefer extracting from R1/R3/R4 rather than launching another expensive run if accepted telemetry suffices.

## 4. Required M1 analysis

Produce:
`REPAIRED_Q05_REQUALIFICATION_MATRIX.tsv`

Compare:
- isolated R0 vs isolated I0;
- P34 R0 vs P34 Q05-only I0;
- isolated R0 vs P8 R0 vs P34 R0;
- repaired vs legacy only for metrics with reconciled scope.

Do not import old I0 numeric values into repaired comparisons.

Produce:
`LEGACY_CLAIM_REQUALIFICATION.md`

At minimum reclassify:
- fixed-window R0/I0 sensitivity;
- full-kernel translation behavior;
- timeline/retry interpretation;
- contextual P8/P34 effects;
- old P34 target-only I0 sensitivity;
- lookup-latency decomposition;
- lookup-model-validity claim that 10/80 are generic assumptions.

Note: lookup provenance classification remains valid; quantitative sensitivity must be requalified separately.

No mechanism design.

## 5. O1 — Cross-family existing-evidence analysis

After M1 is accepted or if simulator work is scientifically blocked but CPU-only analysis remains valid, build from accepted
109 V1/V2.1 evidence.

Families:
- Q05 Prefill Flash;
- Prefill GEMM Primary;
- Decode GEMV Primary;
- Decode Flash Primary-1;
- Decode Flash Primary-2 control.

Use accepted V1 campaign anchor:
`8f49ba3b9228b5f8a9163e961225ffd415107734`

and V2.1 anchor:
`8a9d96ceb00e36ebdfa3d56cc277f965fffa649c`

Produce:
- CROSS_FAMILY_EXISTING_EVIDENCE_MATRIX.tsv
- CROSS_FAMILY_EVIDENCE_GAPS.md
- NEXT_FAMILY_SELECTION_RATIONALE.md

Do not infer TLB misses from page footprint.
Do not invent chronology from trace file order.

## 6. C1 — Conditional non-Attention repaired R0/I0 screen

Enabled conditionally.

Entry gates:
- M1 accepted;
- repaired runtime authority frozen;
- target-I0 per-access semantics qualified;
- enough time before no-new-target cutoff;
- exact accepted producer bundle can be admitted to consumer without semantic weakening.

Preferred target:
`PREFILL_GEMM_PRIMARY_OCC0`

Producer authority exists in accepted 109 V1 campaign.
If no SIM_INPUT exists, perform standard consumer admission from exact immutable producer bundle.
No recapture.

Run at most:
- PREFILL_GEMM_REPAIRED_R0
- PREFILL_GEMM_REPAIRED_I0

No context prefix is assumed.
Label:
`ISOLATED_SCREEN_ONLY`

If Prefill GEMM cannot qualify, Decode GEMV may be considered only if it independently satisfies all gates and enough budget remains.
Do not run both families.

## 7. Solve-and-continue

Engineering problems: solve and continue.

Task-local scientific issue: freeze task, preserve evidence, continue independent authorized work.

Whole-goal STOP only for shared repaired-runtime/source/authority failure.

## 8. Forbidden

No:
- TLB capacity/port sweep;
- lookup-latency sweep;
- PTW/PWC mechanism;
- page-size/segmentation;
- prefetch/speculation;
- cache redesign;
- full historical replay;
- automatic architecture mechanism.

## 9. Durable output

Large logs:
`/root/share/mnt164/huangrulin/awma_repaired_vm_requalification_20h_v1/`

Report:
`docs/vm_tlb/codex_handoff/awma/REPAIRED_VM_REQUALIFICATION_20H_174NEW_V1_REPORT.md`

Review pack:
`docs/vm_tlb/review_packs/AWMA_REPAIRED_VM_REQUALIFICATION_20H_174NEW_V1/`

Required:
- README.md
- SOURCE_ANCHORS.md
- PIPELINE_STATE.json
- REPAIRED_RUNTIME_AUTHORITY.json
- TELEMETRY_SCOPE_RECONCILIATION.md
- TARGET_BOUNDARY_DELTA_SCHEMA.md
- REPAIRED_Q05_REQUALIFICATION_MATRIX.tsv
- LEGACY_CLAIM_REQUALIFICATION.md
- COVERAGE_INVARIANTS.tsv
- cross-family files if executed
- non-Attention pair files if executed
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Final 2h: no new scientific target.

Then report -> pack -> hashes -> commit -> push -> remote verify -> clean -> STOP.
