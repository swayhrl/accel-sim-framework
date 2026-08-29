# ChatGPT -> Codex Handoff

Ownership: ChatGPT.

Permanent coordination branch:

```text
hrl/ep-l2-exp-v0
```

## Current EP-L2 target-mode read order

Codex should fetch this branch and read:

```text
CURRENT_STATE.md
C7E_DISCUSSION_REFERENCE.md
C7E_IMPLEMENTATION_HANDOFF.md
C7E_ACCEPTANCE_CRITERIA.md
FINAL_26RUN_HANDOFF.md
FINAL_26RUN_ACCEPTANCE_CRITERIA.md
CODEX_TARGET_GOAL.md
CODEX_NEXT_STAGE.md
```

`CURRENT_STATE.md` records the reviewed research/architecture state.

`C7E_DISCUSSION_REFERENCE.md` explains why the remaining C7e telemetry work is required.

`C7E_IMPLEMENTATION_HANDOFF.md` defines the allowed C7e implementation scope.

`C7E_ACCEPTANCE_CRITERIA.md` is the authoritative C7e self-gating contract.

`FINAL_26RUN_HANDOFF.md` defines the one clean 13x2 @850 MHz formal campaign.

`FINAL_26RUN_ACCEPTANCE_CRITERIA.md` defines when that campaign is complete.

`CODEX_TARGET_GOAL.md` defines the autonomous repair/transition loop from C7e through 26/26 completion.

`CODEX_NEXT_STAGE.md` is the short executable entry point and current authorization/STOP boundary.

For the current target-mode stage, the explicit authorization in `CODEX_NEXT_STAGE.md` / `CODEX_TARGET_GOAL.md` supersedes any older wording in historical coordination text that required a manual ChatGPT pause between C7e acceptance and the final 26-run.

Codex must not modify these ChatGPT-owned files unless explicitly instructed.

## Codex -> ChatGPT return path

At closeout, Codex should publish source on the stage implementation branch, but mirror documentation-only return artifacts to this coordination branch:

```text
docs/ep_l2/codex_handoff/LATEST_REPORT.md
docs/ep_l2/review_packs/<stage>/
```

For the current goal, expected final review packs are:

```text
docs/ep_l2/review_packs/C7E_FINAL_READINESS_r1/
docs/ep_l2/review_packs/FINAL_TARGET_BASELINE_850_r1/
```

This gives ChatGPT one stable remote entry point without merging stage source code into the coordination branch.
