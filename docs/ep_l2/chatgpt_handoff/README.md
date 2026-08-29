# ChatGPT -> Codex Handoff

Ownership: ChatGPT.

Permanent coordination branch:

```text
hrl/ep-l2-exp-v0
```

Codex should fetch this branch and read, in order:

```text
CURRENT_STATE.md
<current stage>_DISCUSSION_REFERENCE.md
CODEX_NEXT_STAGE.md
```

`CURRENT_STATE.md` is the authoritative coordination state.

`*_DISCUSSION_REFERENCE.md` explains the research/source-review rationale for the current stage.

`CODEX_NEXT_STAGE.md` is the executable stage specification and STOP boundary.

Codex must not modify these ChatGPT-owned files unless explicitly instructed.

At stage closeout, Codex should publish its source on the stage implementation branch, but mirror the documentation-only return path to this coordination branch:

```text
docs/ep_l2/codex_handoff/LATEST_REPORT.md
docs/ep_l2/review_packs/<stage>/
```

This gives ChatGPT one stable remote entry point without merging stage source code into the coordination branch.
