# CODEX SIDE GOAL — 109 Early Close After P2C

Date: 2026-09-18

Status: ACTIVE EARLY-CLOSE OVERRIDE.

This file overrides only the remaining queue depth of:

`CODEX_SIDE_GOAL_109_UNATTENDED_CAPTURE_CAMPAIGN_V1.md`

All scientific identity, storage, fail-closed, publication and provenance rules remain unchanged.

## Current observed state

The campaign is currently inside:

`P2C — Decode GEMV Primary temporal evolution`

Accepted reported progress:

```text
STEP4   complete formal + node164 ACK
STEP8   complete formal + node164 ACK
STEP16  complete formal + node164 ACK
STEP24  complete formal + node164 ACK
STEP32  currently running
```

## Early-close instruction

Do not interrupt the currently running STEP32 target.

When STEP32 reaches its nearest natural safe completion boundary:

1. finish target terminal/validator closure;
2. publish/verify/admit/ACK STEP32 if it passes;
3. quarantine it normally if it fails target-locally;
4. do **not** start P2D, P2E, P3, P3B, P3C, P5, optional cross-model census, or any new GPU target;
5. finish only CPU-only/offline bookkeeping needed to make already completed campaign assets usable.

## Required finalization

Close the campaign with current completed scope:

- P0/P1/P2A/P2B/P2C work already completed or attempted;
- all completed child run IDs and node164 ACKs;
- capture footprint summaries for already successful targets;
- model/replica inventory only if already completed or can finish quickly without delaying GPU release;
- target-status table marking all later queued targets as:
  `SKIPPED_BY_USER_EARLY_CLOSE_AFTER_P2C`;
- no attempt to infer results for skipped targets.

Final status remains legitimate:

`AWMA_109_UNATTENDED_CAPTURE_CAMPAIGN_V1_COMPLETE_WITH_SCOPE`

with explicit reason:

`USER_EARLY_CLOSE_AFTER_P2C_TO_RELEASE_NODE109`

## GPU release priority

After STEP32 target closure:

- terminate no unrelated processes;
- ensure no campaign GPU process remains;
- release the 109 GPU lock immediately;
- do not hold the lock while doing review-pack/git-only finalization.

Then:

```text
review pack
-> report
-> hashes
-> commit
-> push
-> remote ref verify
-> clean worktree
-> STOP
```

Do not auto-start another task.
