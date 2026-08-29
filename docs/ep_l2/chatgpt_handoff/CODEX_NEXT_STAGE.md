# EP-L2 ChatGPT Handoff — CODEX_NEXT_STAGE

Status: **autonomous target mode authorized for C7e -> final 26-run**.

## Execute this target

Read in order:

```text
CURRENT_STATE.md
C7E_DISCUSSION_REFERENCE.md
C7E_IMPLEMENTATION_HANDOFF.md
C7E_ACCEPTANCE_CRITERIA.md
FINAL_26RUN_HANDOFF.md
FINAL_26RUN_ACCEPTANCE_CRITERIA.md
CODEX_TARGET_GOAL.md
```

Then execute the closed-loop goal in:

```text
CODEX_TARGET_GOAL.md
```

## Completion target

Do not stop merely because one C7e validation attempt fails.

Within the frozen instrumentation/provenance scope, autonomously diagnose, repair, recommit, rebuild and rerun until:

```text
C7e == READY_FOR_FINAL_26_RUN
```

Then automatically freeze the exact final source/config pair and continue, without waiting for a manual ChatGPT checkpoint, into the formal:

```text
13 workloads x {B0-Legacy, B0-Banked} @850 MHz
= 26 runs
```

Continue under the formal campaign repair rules until:

```text
TARGET_BASELINE_26RUN_PASS
```

Generate the analysis-ready aggregate outputs and conservative first-pass bottleneck report, publish the Codex->ChatGPT handoff/review packs to the permanent coordination branch, and then STOP.

## Hard boundary

Self-repair is authorized only for instrumentation, parser/analyzer, runner/provenance, tests and review packaging.

Stop and request ChatGPT review if success appears to require changing any frozen architectural/resource/configuration semantics, workload/trace input, invariant meaning, or accepting unexplained instrumentation ON/OFF timing differences.

## Final STOP boundary

Do not start:

```text
1 GHz experiments
RO oracle/shadow
TVD shadow
Unified borrowing
functional EP-L2 mechanisms
```

after the 26-run. Those require the next ChatGPT review.
