# Codex repository guidance (AI-ARCH / AWMA)

This repository also contains historical GPU-simulator code and independent research branches. **Reading this file is not an authorization to run experiments.** Exact scientific contracts and accepted project authority take precedence over this general workflow guide.

- Before research work, identify the project (AI-ARCH Discovery, AWMA, historical C16, or other), its latest **accepted** fixed commit and independent review. `CURRENT_STATE.md` is a dated navigation snapshot, not a live process monitor.
- For experiment/result claims or review packs, use `$scientific-evidence-review`; for literature-derived workload/benchmark decisions, use `$paper-experiment-audit`. Both are **read-only by default**.
- Never silently re-run, reset, restart, relabel, requalify or promote frozen experiments; do not launch GPU, simulator, profiling, downloads or holdout without an explicit project-specific authorization.
- Preserve Native / simulator / source / paper / inference distinctions, exact commit identity, units, negative evidence and STOP boundaries. An engineering PASS is not a scientific claim PASS.
- For authorized code changes, use an isolated worktree, independent build/output paths and feature switches default OFF; never rewrite accepted baseline or shared artifacts. Check CPU/RAM/I/O/GPU locks before any authorized parallel execution.
- Keep 109 as GPU producer when authorized, 174-new as analysis/simulator node when authorized, and 164 as durable large-artifact authority. Do not copy raw traces or model weights into Git.
- Prefer concise tasks and deterministic checks. Minor safe engineering fixes can be included within an already authorized Goal; material scientific identity/contract changes must STOP for review.

Read project-specific scope before changing anything:
`docs/ai_workload_research/COORDINATION_PROTOCOL.md` and
`docs/ai_workload_research/CURRENT_STATE.md` on the actual branch being reviewed.
