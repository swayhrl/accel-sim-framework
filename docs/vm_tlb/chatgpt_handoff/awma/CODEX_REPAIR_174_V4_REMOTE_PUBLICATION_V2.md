# CODEX REPAIR — 174 V4 Remote Publication Verification V2

Date: 2026-09-20

Mode:

`PUBLICATION REPAIR ONLY / ZERO SCIENCE`

Stage:

`AWMA_174_V4_REMOTE_PUBLICATION_REPAIR_V2`

Current independent verification:

```text
remote branch:
hrl/awma-174-hitpath-v4-provenance-closeout-exec

remote SHA observed by GitHub:
c8657cf637c5b54a0f40135248ff1eabcfd66696
```

At that remote commit the final V4 report/matrix/envelope/receipts are NOT present.

Previous `CLOSED` marker is therefore superseded.

## 1. No science

Forbidden:

- simulation;
- rebuilding scientific results from memory;
- new lookup runs;
- TLB/PTW/cache changes.

Only recover existing zero-science closeout artifacts and publish them correctly.

## 2. Find the commit that ACTUALLY contains the files

In:

`/root/workspace/accel-sim-framework-awma-v4-provenance-closeout-174new`

run:

```bash
git status --short
git branch --show-current
git log --all --decorate --oneline -20
```

For every candidate local HEAD/commit, test the COMMIT TREE itself:

```bash
git cat-file -e <SHA>:docs/vm_tlb/codex_handoff/awma/RUNTIME_ACTIVATION_FORENSICS_HITPATH_174NEW_V4_REPORT.md

git cat-file -e <SHA>:docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/REPAIRED_HIT_PATH_LATENCY_MATRIX_V4.tsv

git cat-file -e <SHA>:docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/MODEL_VALIDITY_ENVELOPE.md

git cat-file -e <SHA>:docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/RUN_RECEIPTS.json

git cat-file -e <SHA>:docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/SHA256SUMS
```

Do not use filesystem existence as Git proof.

## 3. If no local commit contains the files

Then the previous closeout artifacts were never committed.

Verify the filesystem files against the already accepted immutable node164/raw evidence.

Then:

```bash
git add <exact required report/review-pack files>
git status --short
git diff --cached --stat
git diff --cached
```

Confirm no scientific-value edits beyond the already completed zero-science reconstruction.

Commit once:

`awma: publish complete V4 hitpath provenance closure`

## 4. Prove local commit-tree completeness

Let:

`FINAL_SHA=$(git rev-parse HEAD)`

Before push, every command below must succeed:

```bash
git cat-file -e $FINAL_SHA:docs/vm_tlb/codex_handoff/awma/RUNTIME_ACTIVATION_FORENSICS_HITPATH_174NEW_V4_REPORT.md

git cat-file -e $FINAL_SHA:docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/REPAIRED_HIT_PATH_LATENCY_MATRIX_V4.tsv

git cat-file -e $FINAL_SHA:docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/TARGET_DELTA_METRICS.tsv

git cat-file -e $FINAL_SHA:docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/COVERAGE_INVARIANTS.tsv

git cat-file -e $FINAL_SHA:docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/MODEL_VALIDITY_ENVELOPE.md

git cat-file -e $FINAL_SHA:docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/RUN_RECEIPTS.json

git cat-file -e $FINAL_SHA:docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/RAW_DATA_INDEX.tsv

git cat-file -e $FINAL_SHA:docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/SHA256SUMS
```

If any fails, do not push/close.

## 5. Push exact commit

Push:

```bash
git push origin +$FINAL_SHA:refs/heads/hrl/awma-174-hitpath-v4-provenance-closeout-exec
```

The force form is allowed here only to move this publication ref from the known incomplete old commit to the exact complete closeout commit. Do not rewrite the scientific commit itself.

## 6. Verify the ACTUAL remote ref

Do not trust a stale local `origin/*`.

Run:

```bash
git ls-remote origin refs/heads/hrl/awma-174-hitpath-v4-provenance-closeout-exec
```

Require returned SHA == `$FINAL_SHA`.

Then fetch the exact ref:

```bash
git fetch origin refs/heads/hrl/awma-174-hitpath-v4-provenance-closeout-exec:refs/remotes/origin/hrl/awma-174-hitpath-v4-provenance-closeout-exec
```

Set:

`REMOTE_SHA=$(git rev-parse origin/hrl/awma-174-hitpath-v4-provenance-closeout-exec)`

Require:

`REMOTE_SHA == FINAL_SHA`.

## 7. Verify file contents FROM REMOTE TRACKING COMMIT

Every command must succeed:

```bash
git cat-file -e $REMOTE_SHA:docs/vm_tlb/codex_handoff/awma/RUNTIME_ACTIVATION_FORENSICS_HITPATH_174NEW_V4_REPORT.md

git cat-file -e $REMOTE_SHA:docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/REPAIRED_HIT_PATH_LATENCY_MATRIX_V4.tsv

git cat-file -e $REMOTE_SHA:docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/TARGET_DELTA_METRICS.tsv

git cat-file -e $REMOTE_SHA:docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/COVERAGE_INVARIANTS.tsv

git cat-file -e $REMOTE_SHA:docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/MODEL_VALIDITY_ENVELOPE.md

git cat-file -e $REMOTE_SHA:docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/RUN_RECEIPTS.json

git cat-file -e $REMOTE_SHA:docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/RAW_DATA_INDEX.tsv

git cat-file -e $REMOTE_SHA:docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/SHA256SUMS
```

Also show:

```bash
git show $REMOTE_SHA:docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/REPAIRED_HIT_PATH_LATENCY_MATRIX_V4.tsv

git show $REMOTE_SHA:docs/vm_tlb/review_packs/AWMA_174_RUNTIME_ACTIVATION_FORENSICS_HITPATH_V4/MODEL_VALIDITY_ENVELOPE.md
```

This is the required remote-tree proof.

## 8. Final report

Return:

- FINAL_SHA;
- `git ls-remote` returned SHA;
- REMOTE_SHA;
- exact equality;
- commit-tree file proof PASS;
- remote-tracking tree file proof PASS;
- SHA256SUMS verification;
- worktree clean.

Only then emit:

`AWMA_174_V4_REMOTE_PUBLICATION_CLOSED_VERIFIED_V2`

STOP.

Do not start the cross-target simulation automatically.
