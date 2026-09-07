# ChatGPT → Codex Handoff

Ownership: **ChatGPT**.

Codex must not modify files under `chatgpt_handoff/` unless the executable specification for the active goal explicitly authorizes that exact modification.

## Current parallel-goal entry

For the three-window VM/TLB execution plan, start from:

`PARALLEL_GOALS_START.md`

and then read the files under:

`parallel_goals/`

The parallel coordination branch is a docs/handoff branch. It must not replace the immutable simulator source anchors named by the window-specific goal.

## Existing M4 semantics remain active

Architecture/mechanism semantics are still governed by the existing M4 handoff/specification set, including:

- `M4_INTEGRATION_GOAL_START.md`
- `CURRENT_STATE.md`
- `DISCUSSION_REFERENCE.md`
- `CODEX_NEXT_STAGE.md`
- `stage_specs/M4_INTEGRATION_AUTHORIZED_ADDENDUM.md`
- `stage_specs/M4_INTEGRATION_TO_SEGMENTATION_MASTER.md`
- `stage_specs/M4I_AB_INTEGRATION_AND_REPLAY.md`
- `stage_specs/M4C_LLM_BASELINE_CHARACTERIZATION.md`
- `stage_specs/M4C_MEMORY_HIERARCHY_TELEMETRY_ADDENDUM.md`
- `stage_specs/M4B_SEGMENTATION_REPRODUCTION.md`
- `paper_specs/SEGMENTATION_LLM_2026.md`

The parallel-goal documents change scheduling, isolation, evidence ownership, and speculative authorization. They do not silently redefine VM/TLB/PTW/Segmentation semantics.

## Three-window read order

1. repository-root `AGENTS.md`;
2. `PARALLEL_GOALS_START.md`;
3. `parallel_goals/PARALLEL_GOALS_MASTER.md`;
4. `parallel_goals/RESOURCE_AND_EXPERIMENT_FARM_POLICY.md`;
5. `parallel_goals/SPECULATIVE_EVIDENCE_POLICY.md`;
6. the selected Window A/B/C goal file;
7. its matrix/validation file where applicable;
8. the existing M4 stage specs referenced by that goal.

If a chat instruction appears to conflict with committed research semantics, preserve the safer committed semantics and report the conflict before changing mechanism behavior. Ordinary engineering failures are to be solved, not treated as automatic stop conditions.
