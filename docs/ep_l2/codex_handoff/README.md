# Codex -> ChatGPT handoff protocol

This directory is the permanent, concise navigation point for a completed
Codex stage. `LATEST_REPORT.md` always identifies the newest completed-stage
review and its recommendation.

Directory ownership is deliberately one-way:

| Directory | Owner and purpose |
| --- | --- |
| `chatgpt_handoff/` | ChatGPT -> Codex instructions and context. |
| `codex_handoff/` | Codex -> ChatGPT stage report and navigation. |
| `review_packs/` | Detailed, browsable review evidence. |

Do not modify `chatgpt_handoff/CURRENT_STATE.md` or
`chatgpt_handoff/CODEX_NEXT_STAGE.md` unless ChatGPT explicitly instructs it.
Those files are ChatGPT-owned, even when a Codex stage uses them as context.
