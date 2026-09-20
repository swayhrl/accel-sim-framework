# CODEX PUBLISH ONLY — 174 V4 Provenance Closeout Remote Authority

Date: 2026-09-20

Mode:
`PUBLISH-ONLY / ZERO-SCIENCE`

The V4 zero-science provenance closeout is reported complete in the local worktree:

`/root/workspace/accel-sim-framework-awma-v4-provenance-closeout-174new`

GitHub currently does NOT expose a new execution branch/commit containing the completed matrix/envelope closure.

Do not rerun, regenerate, or modify scientific outputs except to complete Git publication metadata.

## 1. Inspect local closeout worktree

Run:

```bash
cd /root/workspace/accel-sim-framework-awma-v4-provenance-closeout-174new
git status --short
git branch --show-current
git rev-parse HEAD
git log -5 --oneline --decorate
```

Confirm the worktree contains the completed V4 closure files:

- `docs/vm_tlb/codex_handoff/awma/RUNTIME_ACTIVATION_FORENSICS_HITPATH_174NEW_V4_REPORT.md`
- `docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/REPAIRED_HIT_PATH_LATENCY_MATRIX_V4.tsv`
- `TARGET_DELTA_METRICS.tsv`
- `COVERAGE_INVARIANTS.tsv`
- `MODEL_VALIDITY_ENVELOPE.md`
- `RUN_RECEIPTS.json`
- `RAW_DATA_INDEX.tsv`
- `SHA256SUMS`

## 2. If files are already committed

Do NOT amend/rewrite the commit.

Publish the exact existing HEAD under:

`hrl/awma-174-hitpath-v4-provenance-closeout-exec`

Example:

```bash
git push origin HEAD:refs/heads/hrl/awma-174-hitpath-v4-provenance-closeout-exec
```

## 3. If files are present but uncommitted

Verify they are exactly the already-produced zero-science closeout artifacts.

Commit them once, with no scientific edits:

`awma: publish V4 hitpath provenance closeout`

Then push the resulting HEAD to:

`hrl/awma-174-hitpath-v4-provenance-closeout-exec`

## 4. Remote verification

After push:

- fetch the remote branch;
- verify remote HEAD == local closeout HEAD;
- verify the remote tree contains every required V4 closure file;
- verify `SHA256SUMS` covers the scientific closure files;
- verify worktree clean.

Return:
- branch;
- final local/remote HEAD;
- matrix file presence;
- envelope file presence;
- no-science confirmation.

STOP.

No simulator execution. No new derivation. No mechanism experiment.
