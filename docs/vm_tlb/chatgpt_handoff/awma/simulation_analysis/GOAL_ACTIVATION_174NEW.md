# 174-new Simulation Foundation — Goal Activation

Use this file to start a **new Codex window** on 174-new while the existing Qwen Decode/native-analysis Goal continues in another worktree.

## Required branch

Fetch/pull:

```text
hrl/awma-simulation-analysis-plan-v1
```

Use the latest branch HEAD shown by Git after fetch.

## Required read order

```text
docs/vm_tlb/chatgpt_handoff/awma/simulation_analysis/README.md
docs/vm_tlb/chatgpt_handoff/awma/simulation_analysis/CURRENT_STATE.md
docs/vm_tlb/chatgpt_handoff/awma/simulation_analysis/SIMULATION_ANALYSIS_ARCHITECTURE.md
docs/vm_tlb/chatgpt_handoff/awma/simulation_analysis/RUNTIME_BASELINE_AND_CALIBRATION_PLAN.md
docs/vm_tlb/chatgpt_handoff/awma/simulation_analysis/SIMULATOR_INPUT_AND_CAPTURE_PLAN.md
docs/vm_tlb/chatgpt_handoff/awma/simulation_analysis/SIMULATION_METRICS_AND_DATA_MODEL.md
docs/vm_tlb/chatgpt_handoff/awma/simulation_analysis/EXECUTION_ROADMAP.md
docs/vm_tlb/chatgpt_handoff/awma/simulation_analysis/PARALLEL_EXECUTION_AND_AUTONOMOUS_RECOVERY.md
docs/vm_tlb/chatgpt_handoff/awma/simulation_analysis/ACCEPTANCE_AND_REVIEW_REQUIREMENTS.md
```

Then execute in **GOAL MODE**:

```text
docs/vm_tlb/chatgpt_handoff/awma/simulation_analysis/CODEX_NEXT_STAGE_174NEW_SIMULATION_FOUNDATION.md
```

## Suggested execution branch

```text
hrl/awma-simulation-foundation-174new-v1
```

Create a fresh worktree. Do not reuse the active Qwen/native-analysis worktree.

## Operating instruction

Treat this as a substantial solve-and-continue Goal.

Do not stop at the first missing dependency, build failure, stale path, parser mismatch, fixture issue or absent helper binary. Diagnose and solve recoverable engineering problems autonomously when scientific meaning is unchanged. Use isolated user-space/build environments where appropriate, regression-test repairs, log them, and continue.

A missing default `nvcc` or missing historical exact binary is a recovery problem to investigate, not an immediate whole-Goal STOP condition.

If runtime recovery is genuinely exhausted, record the exact blocker and continue every independent simulation-foundation phase. The Goal may finish as `AWMA_SIMULATION_FOUNDATION_PASS_RUNTIME_BLOCKED` only when the strengthened acceptance document permits it.

Do not:

```text
interrupt the active Qwen/native Goal
kill/restart unrelated Codex/VS Code/SSHFS processes
modify another active worktree
use 109 GPU in this foundation stage
mutate accepted C16/native raw
fabricate C16WARP1→traceg semantics
run production mechanism sweeps
mass-rename legacy C16 paths
```

## Finish condition

Continue through implementation, recovery attempts, tests, node164 metadata/catalog, review pack, Codex report, commit and push.

STOP only at the stage boundary defined by `CODEX_NEXT_STAGE_174NEW_SIMULATION_FOUNDATION.md`, or earlier only for a genuinely scientific-semantic/destructive blocker that cannot safely be resolved under the frozen contracts.
