# Read-only Skill canaries (not executed by this GitHub-only preparation)

Each canary must use the **bootstrap branch's own isolated worktree**. Do not run a GPU task, simulator, profiler or data ingestion. Use only checked-in files.

## A. Scientific-review canary: AWMA R27R3 B0 reference

Ask Codex to invoke `$scientific-evidence-review` and independently inspect the immutable [independent review](https://github.com/swayhrl/accel-sim-framework/blob/d6e9bbfb562814bcd5dc5adb444d3c572e7f446b/docs/vm_tlb/literature_notes/awma/empirical/R27R3_B0_REFERENCE_REPEATABILITY_REVIEW_2026-10-13.md) and execution [fixed commit](https://github.com/swayhrl/accel-sim-framework/commit/7bd31fae4c54e121d54743a803d978ee02a64959).

Expected *reasoning* safeguards, not a predicted automatic PASS:
- Two fresh B0 processes, fixed reference conditions, 25 / 262,668,288 BF16 gradient elements beyond the existing elementwise tolerance; repeatability failed within that scope.
- It does **not** establish that B0 mathematics is wrong, that S2/C1 were executed, or that there is a measured capacity improvement or regression.
- If raw GPU data are not accessible, use `GITHUB_ONLY_NOT_RAW_REVALIDATED` and cite the independent review at immutable SHA; do not say “I independently reran it”.
- Status remains COMPLETE/STOP; no GPU R27R4 or 32-step follow-up.

## B. Paper-group canary: AI-ARCH P01/P13

Ask Codex to use `$paper-experiment-audit` on the frozen [P01/P13 experiment-group audit](https://github.com/swayhrl/accel-sim-framework/blob/2048f23b1a765393cbf27c3ee413ccae1addcf45/docs/ai_workload_research/literature/AI_ARCH_P01_P13_EXPERIMENT_GROUP_AUDIT_2026-10-13_V1.md), cross-referencing original paper links present in that audit when available.

Verify it *does not*:
- Collapse all paper experiment groups into “whole-model native measurement”.
- Treat a numerical utilization metric as a fraction without checking its unit/denominator.
- Treat NanoFlow, MPK or another paper's platform as proof of RTX4080 behavior.
- Invent undisclosed variables or author's workload motivation; paper source access limitations must be explicit.
- Open new GPU, holdout or simulator experiments.

## C. Optional local multiagent canary

Only if the installed Codex supports it without global modification, delegate two independent **read-only** tasks: contract/provenance audit vs claim/unit audit, or separate paper groups. Compare against a single-agent review for coverage, wall-clock and token cost; stop if duplicated work, unavailable version, extra data access or repository write risk. Do not claim subagents are validated merely because the parent agent mentioned delegation.

## Acceptance checklist

- Skill metadata discovered in isolated worktree, or an explicit unsupported-version finding.
- A and B produce evidence-rich reports with immutable sources, no invented raw verification, and no authorization expansion.
- `git status --porcelain` clean after canaries, unless test outputs deliberately written outside the repo to a small isolated scratch directory.
- No node109 GPU use; no simulator execution; no hooks/global Codex config changes; no experiment or status branches moved.
- One bounded report with precise CLI/plugin availability and any needed future opt-in step.
