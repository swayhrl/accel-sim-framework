# Codex Goal — verify bootstrap Skills safely on 174-new (V1)

**Authorized scope**: read-only repository/CLI inspection plus tiny CPU-only Skills canaries in an isolated worktree and isolated scratch, when resources permit. This document does not authorize GPU, simulation, profiling, re-running AWMA/C16 tests, changes to existing experiment branches, large transfers, model download, CLI upgrade or persistent hook installation.

## Preflight

1. Read this file, `README.md`, `CANARY_TASKS.md`, root `AGENTS.md`, the two new `SKILL.md`s and their templates.
2. Check current host, physical/logical CPU/RAM/swap/free disk, root filesystem pressure, worktrees, existing processes, and `codex --version` and `codex --help`. Check whether the current Codex surface recognizes repo-local skills and supports subagents/review/hooks. Do not assume a newer feature is enabled, and don't modify `~/.codex/config.toml`, SSH settings, default model or VS Code app-server. Avoid placing large data on 174 local overlay.
3. Fetch the named bootstrap branch, check exact remote commit and select a **small isolated worktree path only if space and permissions permit**. Do not checkout/change any existing running worktree. Abort safely if no space; report the constraint. Do not execute an existing scientific Goal or start scripts merely because the word “canary” appears.

## Bounded canaries

4. Run CANARY A with `$scientific-evidence-review` (or explicitly read SKILL.md if automatic discovery is unsupported). Use only Git committed source and cite its immutable SHA. Outputs can be in a small designated external scratch folder, with no git writes.
5. Run CANARY B with `$paper-experiment-audit` using the fixed P01/P13 literature audit and any original sources already accessible. Do not fetch hundreds of papers or start an open-ended research campaign. If source URLs are inaccessible, record unverified scope rather than guessing.
6. If local Codex supports subagents with a safe read-only mode, optionally run a two-reviewer **CPU/source-only** canary on A or B. If not, mark `NOT_AVAILABLE`; do not add guessed config options or upgrade Codex merely to force the test.
7. Inspect the available `codex review --help` behavior, but do not submit GitHub PRs or automatically review an unrelated experiment branch. Draft a future hooks strategy (manifest/receipt existence and status only), **do not install hooks** or claim scientific qualification from a Hook exit code.

## STOP and deliver

8. Produce a small report: installed CLI/version and feature visibility; skill discovery A/B results; output quality issues; subagent support/cost observation if tested; exact code/ref inspected; no-write/resource guard checks; future opt-in actions. Retain no unnecessary local copies. Do not edit scientific artifacts.
9. Stop. If content fixes to the candidate skills are required, propose them in a separate review patch/branch, not as silent changes to accepted experiments. Any merge/promotion of Skills or AGENTS.md into the long-lived coordination or execution branches needs explicit approval.

**Execution priority**: minimize current-work interference. Ordinary local verification problems can be handled within this bounded Goal without asking for a new scientific authorization; permission or scientific-boundary changes must stop for review.
