# Codex → ChatGPT Handoff

Ownership after bootstrap: **Codex**.

`LATEST_REPORT.md` is the single entry point for ChatGPT review.

For every completed executable stage, Codex must:

1. update `LATEST_REPORT.md`;
2. create/update exactly one `docs/dtc_l1/review_packs/<stage>/` directory;
3. record final Core and Framework SHAs;
4. record validation status and remaining issues;
5. push source branches and review material;
6. STOP at the active stage boundary.

ChatGPT should be able to review the stage from `LATEST_REPORT.md` → review-pack README → source/results without relying on Codex chat history.
