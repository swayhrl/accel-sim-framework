# CODEX_NEXT_STAGE

## Status

**ACTIVE — RESOLVE M5-T005 WITH APPROVED RATIO-0 POLICY, THEN CONTINUE M5.0B -> M5.6**

The prior `RESEARCHER_DECISION_REQUIRED` boundary is resolved.

Specific authoritative resolution:

`docs/dtc_l1/m5/M5_DIRTY_VICTIM_POLICY_RESOLUTION.md`

M1-M4 remain closed PASS. M5.0A is closed PASS. Current work resumes inside M5.0B.

## Active branches

Core:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-m5-v0`

Framework:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m5-v0`

Do not modify validated M1-M4 branches.

## Mandatory read order

Framework:

1. `AGENTS.md`
2. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/dtc_l1/m5/M5_V1_APPROVAL.md`
4. `docs/dtc_l1/m5/M5_DIRTY_VICTIM_POLICY_RESOLUTION.md`
5. `docs/dtc_l1/m5/M5_EXPERIMENT_MATRIX.md`
6. `docs/dtc_l1/m5/M5_PROBLEM_RESOLUTION_POLICY.md`
7. `docs/dtc_l1/m5/M5_HANDOFF_CONTRACT.md`
8. `docs/dtc_l1/m5/M5_GRAPHICS_PREP.md`
9. this file
10. `docs/dtc_l1/chatgpt_handoff/GOAL_START.md`
11. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
12. `docs/dtc_l1/implementation/M5_ISSUE_LOG.md`, especially M5-T004/T005
13. final M4 review pack as regression context

Core:

14. `AGENTS.md`
15. `docs/dtc_l1/DTC_L1_SPEC.md`

## Researcher decision for M5-T005

The 16 KiB conventional L1 geometry remains frozen.

For every paper-facing M5 formal config use explicitly:

```text
-gpgpu_l1_cache_write_ratio 0
```

Preserve the existing write-through and allocation semantics. Do not modify `tag_array::probe` to invent a new dirty-victim fallback for formal M5 merely to retain the inherited 25% heuristic.

The old value 25 is classified as inherited SM7 `DIAGNOSTIC_PLATFORM_POLICY`. It may be retained in diagnostic controls but is not the formal Chapter-4 baseline policy.

## Immediate recovery sequence

Execute R5DV.0-R5DV.5 from `M5_DIRTY_VICTIM_POLICY_RESOLUTION.md`.

Required minimum sequence:

1. preserve all existing ratio-25 deadlock evidence and current in-flight jobs;
2. update the complete LEGACY/Base/IO/OO formal config family to explicit ratio 0, with a strict diff proving no unrelated knob changes;
3. add a deterministic dirty-set conventional-L1 regression proving a fifth same-set access can replace a MODIFIED victim and make forward progress under write-through ratio 0 without weakened assertions;
4. rerun canonical Parboil JDS SpMV medium under corrected 16 KiB LEGACY and PAPER_BASE configs and require valid output and no dirty-set deadlock;
5. refresh formal config hashes/result identities and ratio-0 LEGACY/Base/IO/OO sentinels;
6. update M5-T005 through RESOLVED/REGRESSED/CLOSED when evidence supports it;
7. resume the remaining M5.0B workload recovery immediately.

Do not wait for the already-running 32/128 KiB or other ratio-25 diagnostics to finish before starting corrected work if the calibrated host-concurrency budget permits it. Do not kill them solely because of this resolution either.

## Why this is configuration fidelity, not architecture redesign

The generic GPGPU-Sim cache option defaults the write ratio to zero. The inherited formal files explicitly set 25 from the SM7/Volta platform. Current source uses that threshold to exclude MODIFIED lines from replacement below the global dirty percentage. At 16 KiB/4-way this can create a set with four MODIFIED lines and no eligible victim.

The configured L1 is write-through: writes are sent to the lower level immediately even though local line state is marked MODIFIED. The thesis describes GPU L1 as normally write-through and does not freeze a 25% dirty-retention threshold for the Chapter-4 baseline.

Therefore the approved formal policy is the source-supported ratio 0, not a source-code replacement-policy redesign.

## Continue after issue closure

Once R5DV closes, continue automatically under the existing M5 v1 sequence:

`M5.0B -> M5.0C -> M5.0D -> M5.0E -> M5.1 -> M5.2 -> M5.3 -> M5.4 -> M5.5 -> M5.6`.

Do not stop for ordinary recoverable issues. Follow `M5_PROBLEM_RESOLUTION_POLICY.md` and keep `M5_ISSUE_LOG.md` current.

## Pause conditions

Pause only at a new genuine `RESEARCHER_DECISION_REQUIRED` boundary, such as:

- the only source-correct next step would alter frozen DTC/M0-M4 architecture semantics;
- ratio 0 still cannot provide a source-correct conventional-L1 execution and multiple scientifically distinct paper-facing policies remain;
- an irreducible workload/metric interpretation needs researcher choice;
- or terminal `M5_COMPUTE_READY_FOR_REVIEW` is reached.

A large performance shift from 25 -> 0 is **not** a pause condition. Diagnose it as platform-policy sensitivity and continue.

## Forbidden shortcuts

Do not:

- enlarge the formal 16 KiB Base L1;
- disable deadlock detection;
- weaken pending-write/scoreboard assertions;
- keep ratio 25 for one formal mode but use ratio 0 for another;
- modify DTC architecture to compensate for the conventional cache artifact;
- treat 32/128 KiB controls as replacement paper baselines;
- tune input sizes to recover thesis speedups;
- begin M5.7+ before compute review.
