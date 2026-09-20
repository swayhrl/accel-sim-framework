# CODEX NEXT STAGE — 174 V4 Provenance Closeout Only

Date: 2026-09-20

Mode:
`GOAL MODE / ZERO-SCIENCE CLOSEOUT`

Node:
`174-new`

Stage:
`AWMA_174_HITPATH_V4_PROVENANCE_CLOSEOUT`

Coordination branch:
`hrl/awma-174-hitpath-v4-provenance-closeout`

Accepted execution branch:
`hrl/awma-174-runtime-load-forensics-hitpath-v4`

Accepted remote execution HEAD:
`c8657cf637c5b54a0f40135248ff1eabcfd66696`

Read:
1. `REVIEW_174_V4_PROVENANCE_GAP_2026-09-20.md`
2. V4 execution report/review-pack in the existing local V4 worktree if present
3. node164 V4 runtime/run receipts
4. this Goal

Suggested execution branch:
`hrl/awma-174-hitpath-v4-provenance-closeout-exec`

Create from `c8657cf...`.

## 1. No new science

Forbidden in this Goal:
- simulator rerun;
- lookup variant rerun;
- GEMM screen;
- config/source change;
- architecture mechanism.

This is packaging/provenance only.

## 2. Recover existing V4 closure artifacts

First inspect the original V4 worktree:

`/root/workspace/accel-sim-framework-awma-runtime-load-forensics-hitpath-v4`

Look for the already-produced:
- final report;
- latency matrix;
- target-delta metrics;
- coverage invariants;
- model-validity envelope;
- run receipts;
- raw-data index;
- SHA256SUMS.

If the old worktree no longer contains them, recover from the exact node164 V4 durable directory and immutable raw run logs.

Do NOT infer missing scientific values from memory.

## 3. Validate each admitted run

For each:
- P34 repaired 10/80 qualification;
- 0/80;
- 0/0;
- 10/0;
- 5/80;
- 2/80;
- 10/40;

verify:
- raw log/receipt exists;
- SHA/size;
- exact loaded repaired core authority;
- Q05 identity;
- natural completion;
- admissions/coverage invariants.

Do not admit a row that cannot be tied to raw evidence.

## 4. Reconstruct derived tables only when needed

It is allowed to regenerate small derived files from immutable admitted raw logs:

- `REPAIRED_HIT_PATH_LATENCY_MATRIX_V4.tsv`
- `TARGET_DELTA_METRICS.tsv`
- `COVERAGE_INVARIANTS.tsv`
- `MODEL_VALIDITY_ENVELOPE.md`

Required envelope formulas:

```text
TOTAL_I0_GAP
 = cycles(10/80) - 758082

L1_ENVELOPE
 = cycles(10/80) - cycles(0/80)

L2_NATURAL_L1_EFFECT
 = cycles(10/80) - cycles(10/0)

ZERO_LOOKUP_RESIDUAL
 = cycles(0/0) - 758082
```

Do not reinterpret them as hardware latency.

## 5. Required Git closure

Final report:
`docs/vm_tlb/codex_handoff/awma/RUNTIME_ACTIVATION_FORENSICS_HITPATH_174NEW_V4_REPORT.md`

Review pack:
`docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/`

Ensure at minimum the existing runtime-forensics artifacts plus:

- `P34_REPAIRED_QUALIFICATION.md`
- `REPAIRED_HIT_PATH_LATENCY_MATRIX_V4.tsv`
- `TARGET_DELTA_METRICS.tsv`
- `COVERAGE_INVARIANTS.tsv`
- `MODEL_VALIDITY_ENVELOPE.md`
- `NON_ATTENTION_SCREEN_STATUS.md`
- `RUN_RECEIPTS.json`
- `RAW_DATA_INDEX.tsv`
- `SHA256SUMS`

If a file is not applicable, write an explicit scoped status.

## 6. Final verification

Before STOP:
- hash all Git-pack files;
- verify node164 raw receipts;
- commit;
- push;
- verify remote branch;
- verify the remote tree actually contains the matrix/envelope files;
- clean worktree.

Success marker:

`AWMA_174_HITPATH_V4_PROVENANCE_CLOSEOUT_COMPLETE`

STOP.

Do not automatically launch any new TLB/PTW experiment.
