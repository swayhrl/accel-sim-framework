# CODEX 174 CONTINUATION — V2R1 Publication Repair Only

Date: 2026-09-23

Mode:
`GOAL MODE / PUBLICATION-ONLY REPAIR / solve-and-continue`

Stage:
`AWMA_TRANSLATION_FRONTEND_READY_APPLICATION_RECALIBRATION_V2R1_PUBLICATION_REPAIR`

Read first:

1. `docs/vm_tlb/chatgpt_handoff/awma/REVIEW_174_V2R1_PUBLICATION_AUDIT_2026-09-23.md`
2. execution branch:
   `hrl/awma-174-translation-frontend-ready-application-v2r1 @ 42226dbf4a61be3081c976f639c7d2284db58ff5`
3. raw receipt archive:
   `/root/awma_v2r1_closeout_pending`
4. surviving V2R1 worktree/runtime logs.

## Hard boundary

This is NOT a scientific rerun.

Do NOT run:
- T2 replay;
- T0/T1;
- Native calibration;
- Accel-Sim workloads;
- any new mechanism.

Only recover already-existing scientific outputs and publish them correctly.

## 1. Diagnose publication failure

Confirm that remote HEAD currently contains zero-byte placeholders for most V2R1 review-pack files and that the expected report is absent.

Determine whether:
- local populated files still exist in the V2R1 worktree;
- populated files exist in `/root/awma_v2r1_closeout_pending`;
- they can be reconstructed deterministically from raw receipts/logs.

Record the cause if identifiable, e.g. placeholder creation, wrong source path, staging mistake, or copy command error.

## 2. Recover the required evidence

Reconstruct/populate at minimum:

```text
docs/vm_tlb/codex_handoff/awma/
TRANSLATION_FRONTEND_READY_APPLICATION_RECALIBRATION_174NEW_V2R1_REPORT.md

docs/vm_tlb/review_packs/
AWMA_TRANSLATION_FRONTEND_READY_APPLICATION_RECALIBRATION_V2R1/
README.md
SOURCE_ANCHORS.md
PRE_REPAIR_V2_DIAGNOSIS.md
READY_CONSUMPTION_REPAIR.patch
DIRECTED_READY_CONSUMPTION_TESTS.tsv
T2_REQUALIFICATION.tsv
CONTROLLER_QUIESCENCE.tsv
HOST_TIME_OBSERVATION.tsv
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
RECALIBRATION_DECISION.md
SHA256SUMS
```

The source patch already present may be retained if it matches the actual repaired source.

## 3. Required scientific content

The recovered evidence must explicitly support, from surviving raw receipts:

### T2 requalification
- 10/80 cycles = 111607
- 0/80 cycles = 71743
- residual recomputed from those values;
- instructions;
- CTA;
- unique UID;
- translated_unique;
- untranslated;
- unobserved;
- READY exactly-once accounting;
- Segment dormant.

### Full controller quiescence
For both T2 points:
- `m_lookups = 0`
- `LOOKUP_READY = 0`
- `m_mshrs = 0`
- `m_pwq = 0`
- `active_walks = 0`
- `quiescent_invariants_hold = true`

### Host-time observation
Recover the repaired T2 host rates/timestamps if available and clearly separate them from scientific cycle results.

### Pre-repair provenance
Preserve:
`PRE_REPAIR_READY_RETENTION_INVALID_FOR_FINAL_CLASSIFICATION`

## 4. Publication integrity

Do not create empty placeholder files.

Before commit:

- assert every semantically-required review-pack file has non-zero byte size;
- parse TSV/JSON syntax where applicable;
- confirm the report and decision contain the expected final classification;
- regenerate SHA256SUMS from the actual populated files.

After push:

1. fetch the remote branch back;
2. confirm remote HEAD == local HEAD;
3. inspect the fetched remote tree;
4. verify each promised file exists;
5. verify each promised file has the same non-zero size as local;
6. run `sha256sum -c SHA256SUMS` against the fetched remote-tree contents;
7. explicitly verify the report file is present remotely;
8. clean worktree.

## 5. Scientific classification

If the surviving evidence really supports the reported values and full quiescence, retain:

`READY_APPLICATION_HOL_NOT_PRIMARY`

Do not alter the conclusion merely because publication previously failed.

If the underlying scientific receipt itself is missing/corrupt, STOP and report that exact missing P1 evidence instead of rerunning automatically.

## 6. Stop boundary

After publication repair and remote verification, STOP for ChatGPT review.

Do not start Native↔simulator cross-calibration in this Goal.
