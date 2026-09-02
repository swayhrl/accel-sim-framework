# Codex handoff

Ownership: Codex

`LATEST_REPORT.md` is the single entry point for ChatGPT review.

At the completion of every Codex round, Codex must update `LATEST_REPORT.md`,
create or update the relevant review pack, record final SHAs, commit, push to a
writable remote, and stop. Raw build and simulator logs must remain out of Git;
the review pack records their identity and location instead.
