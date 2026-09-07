# Parallel VM/TLB goals start

Status: **AUTHORIZED PARALLEL EXECUTION PLAN**.

This coordination branch exists only to hand three isolated Codex goals to three windows. It is not a formal simulator source anchor and must never be substituted for the immutable C3 anchors.

## Immutable accepted anchors

- Authoritative Framework/C3 source: `a7c0759be7f293ed0d5e2179c62094b6de49c1e8`
- Authoritative Core source: `0d92e6aa8fd8bc885ffdf081a559bc616aaa85fd`
- Authoritative C3 simulator binary SHA-256: `100527f1d54600dcbbf7c713584512344a688521089aaa995a0b7e4106f81eda`
- Verified Core-local simulator runtime SHA-256: `fc07def22e239de9fec8a3dd83d237a607a82162cab2933d6707a37c0a208b0a`
- Decode1 compute-only list SHA-256: `b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc`
- Prefill compute-only list SHA-256: `a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f`

The historical host CUDA `libcudart.so` attribution is superseded by the direct `/proc/<pid>/maps` evidence in `M4C_C3_PROGRESS_REVIEW_20260907/C3_LIVENESS_AND_RUNTIME_PROVENANCE_CHECK.md`.

## Three windows

### Window A — AUTHORITATIVE

Entry: `parallel_goals/WINDOW_A_AUTHORITATIVE_C3_C4_GOAL.md`

Purpose: finish the current formal C3 sequence, perform 8/8 terminal closeout, execute C4 structured export/offline locality/baseline characterization, then STOP for ChatGPT review.

Window A owns the only results that may be promoted to current formal M4C evidence before review.

### Window B — SPECULATIVE EXPERIMENT FARM

Entry: `parallel_goals/WINDOW_B_SPECULATIVE_EXPERIMENT_FARM_GOAL.md`
Matrix: `parallel_goals/WINDOW_B_EXPERIMENT_MATRIX.md`

Purpose: exploit the large CPU/memory host for parallel immutable-trace mining, broad VM sensitivity sweeps, cache sweeps, non-LLM comparison, and optional TLB×L2 cross-product experiments.

All Window-B results are `SPECULATIVE_DIAGNOSTIC` until explicitly promoted after Window-A/C4 review.

### Window C — SPECULATIVE M4B DEVELOPMENT

Entry: `parallel_goals/WINDOW_C_SPECULATIVE_M4B_GOAL.md`
Validation: `parallel_goals/WINDOW_C_VALIDATION_CONTRACT.md`

Purpose: implement/audit the paper paging/sub-entry candidate and Weight Segmentation in an isolated lineage, pass directed regressions, then run bounded and optionally full candidate replays. Never merge into the authoritative lineage automatically.

## Mandatory common documents

All windows must read:

1. repository-root `AGENTS.md`;
2. this file;
3. `parallel_goals/PARALLEL_GOALS_MASTER.md`;
4. `parallel_goals/RESOURCE_AND_EXPERIMENT_FARM_POLICY.md`;
5. `parallel_goals/SPECULATIVE_EVIDENCE_POLICY.md`;
6. the window-specific goal and validation/matrix files.

Existing M4 handoff/specs remain authoritative for architecture semantics. The parallel-goal files change execution scheduling and evidence ownership; they do not silently change VM/TLB/PTW/Segmentation semantics.

## Cross-window rule

- A must never consume B/C code or results during C3/C4 unless ChatGPT explicitly authorizes it.
- B/C must never modify A worktrees, A scratch, A supervisor, A binary, A config, A object maps, or A trace lists.
- B and C use fresh worktrees, branches, build roots, and scratch roots.
- Shared immutable trace trees may be read concurrently by symlink/read-only path.
- No window may kill or attach to another window's simulator processes.

## Problem-solving policy

Ordinary build, path, script, parser, scheduler, resource, and test failures are engineering problems to solve, not reasons to stop. Codex must diagnose root cause, try reasonable fixes, add/re-run focused validation, and continue.

Hard STOP is reserved for semantic correctness/provenance failures, cross-window contamination, source/artifact mismatch that cannot be resolved safely, request loss/duplicate side effects/recursive or misassociated PTE traffic, formal trace corruption, or machine-safety conditions that cannot be mitigated without risking data/results.
