# AI-ARCH / AWMA Codex workflow bootstrap (2026-10-13)

**Status: review candidate on isolated branch, not active coordination policy.** This tree changes no scientific code, simulator configs, experiment identity, Git tags or current coordination states. It provides two inspectable, opt-in research Skills and a concise `AGENTS.md`. Merging into long-lived coordination or execution branches requires separate review.

## Validation update: 174-new report, 2026-10-13

Read [174-new bounded verification receipt](174NEW_SAFE_VALIDATION_RECEIPT_2026-10-13.md). Codex reported that both Skill texts/templates were manually applied to two bounded cases in an isolated 2.1 MB worktree. AWMA R27R3 and AI-ARCH P01/P13 scope was preserved. **Automatic CLI Skill discovery is still unverified** because the CLI process lacked the configured `WCLQ_API_KEY` before any model call. Multi-agent/review/hooks flags and help entries are not equivalent to end-to-end runtime qualification.

**Adoption decision:** use direct ChatGPT GitHub reads and manual single-agent Skill reading immediately; use parallel reviewers only for high-risk independent checks. Do not repeat a large canary, install hooks, rotate credentials, upgrade global Codex or merge into a scientific execution branch. Fix CLI environment propagation only as a tiny isolated opt-in smoke test later. Coordination branch has advanced and diverged from this bootstrap candidate, so future adoption must cherry-pick or transplant only reviewed configuration files onto a fresh branch based on the then-current coordination head.

## Source authority

Prepared from fixed parent `hrl/ai-workload-research-coordination @ 2048f23b1a765393cbf27c3ee413ccae1addcf45` on 2026-10-13. Relevant source documents:
- [coordination policy](../COORDINATION_PROTOCOL.md)
- [state snapshot](../CURRENT_STATE.md)
- [AI-ARCH handoff](../AI_ARCH_DISCOVERY_HANDOFF_CONTEXT_2026-10-13_V1.md)
- [problem atlas](../AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md)
- [cross-project evidence](../AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)

They are versioned navigation/knowledge sources, not SSH/live node status. A future live claim must read newer accepted project authority.

## Included

- `/AGENTS.md`: short project-level invariants and skill triggers. Only applies in a worktree actually containing it.
- `/.agents/skills/scientific-evidence-review/SKILL.md`: formal evidence/claim review with a small output template.
- `/.agents/skills/paper-experiment-audit/SKILL.md`: paper-by-experiment-group audit with a small worksheet.
- `CODEX_174NEW_SAFE_VALIDATION_GOAL_V1.md`: CPU/source-only installation verification; no experimental work.
- `CANARY_TASKS.md`: fixed read-only smoke tests and expected limitations.

## Design choice

First adopt **GitHub-direct read-only ChatGPT review**, then test two project-local Skills in an isolated Codex worktree. Start with a single reviewer; if local subagents are supported, add two bounded, read-only reviewers (source/contract vs numerical/claim; or different paper experiment groups), retaining an integrating human-facing main reviewer. Do not force unsupported multi-agent TOML settings, upgrade global CLI or create persistent hooks until feature detection and isolated smoke tests pass.

See [OpenAI skill guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) and [Codex Skills in OSS](https://developers.openai.com/blog/skills-agents-sdk) for the progressive-disclosure pattern; exact local CLI options must be probed rather than assumed.

## Direct ChatGPT–GitHub workflow

A ChatGPT session with a connected GitHub plugin can read fixed commits and files, compare selected changes, and review evidence available in Git. It does **not** automatically read live processes, private node164 artifacts, uncommitted 109/174 data or unseen device measurements. For audit, ask: “Review project X at fixed SHA Y and files Z; distinguish source-reported scientific PASS from independent raw verification; don't generate a new Goal.”

## Promotion rule

No automatic promotion from these files. After two canaries and a diff review, explicitly choose whether to cherry-pick only the compact `AGENTS.md`/Skills into a compatible non-running development branch. Do not mass-merge this bootstrap branch into AWMA/C16 simulator/production execution histories.
