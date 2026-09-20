# CODEX CLOSEOUT — 174 V4 Remote Publication Blocker

Date: 2026-09-20

Mode:

`PUBLICATION-ONLY / ZERO-SCIENCE`

Priority:

`AWMA_MAINLINE_P0_BLOCKER`

Current remote problem:

`hrl/awma-174-hitpath-v4-provenance-closeout-exec`

still resolves remotely to:

`c8657cf637c5b54a0f40135248ff1eabcfd66696`

which does not expose the reported zero-science reconstructed matrix/envelope closure.

## 1. Mandatory contract

Apply:

`174_MANDATORY_REMOTE_PUBLICATION_CONTRACT.md`

No next 174 science stage may start before this is closed.

## 2. Locate the actual local closeout authority

Primary worktree reported by the user:

`/root/workspace/accel-sim-framework-awma-v4-provenance-closeout-174new`

Inspect:

```bash
git status --short
git branch --show-current
git rev-parse HEAD
git log -10 --oneline --decorate
```

Find the exact local commit containing the reconstructed V4 scientific closure.

Do not assume `c8657cf...` if the files were produced afterward.

## 3. Required files

The exact published remote tree must contain:

- `docs/vm_tlb/codex_handoff/awma/RUNTIME_ACTIVATION_FORENSICS_HITPATH_174NEW_V4_REPORT.md`
- `docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/P34_REPAIRED_QUALIFICATION.md`
- `REPAIRED_HIT_PATH_LATENCY_MATRIX_V4.tsv`
- `TARGET_DELTA_METRICS.tsv`
- `COVERAGE_INVARIANTS.tsv`
- `MODEL_VALIDITY_ENVELOPE.md`
- `NON_ATTENTION_SCREEN_STATUS.md`
- `RUN_RECEIPTS.json`
- `RAW_DATA_INDEX.tsv`
- `SHA256SUMS`

plus the already accepted runtime-load forensics files.

## 4. If local files are not committed

Verify they are exactly the already-produced zero-science closeout artifacts bound to immutable raw receipts.

Commit once.

No simulation.

No scientific-value editing.

No recomputation except deterministic packaging/hash generation from admitted immutable evidence.

## 5. Publish

Publish exact final local HEAD to:

`hrl/awma-174-hitpath-v4-provenance-closeout-exec`

Do not force the ref to an older commit.

Then:

```bash
git fetch origin
git rev-parse HEAD
git rev-parse origin/hrl/awma-174-hitpath-v4-provenance-closeout-exec
```

Require exact equality.

## 6. Remote tree verification

After push, explicitly verify via remote tree that every required report/pack file exists.

Verify SHA256SUMS coverage.

Verify node164 raw receipt authority remains intact.

## 7. Final state

Return:

- execution branch;
- final local HEAD;
- final remote HEAD;
- `remote HEAD == local HEAD`;
- remote matrix present;
- remote envelope present;
- final report present;
- review pack complete;
- worktree clean.

Success:

`AWMA_174_V4_REMOTE_PUBLICATION_CLOSED`

STOP.

No new simulation or mechanism experiment in this Goal.
