# START — Lane G NVBit 1.7.5 capture qualification

Read-only handoff branch:

```text
hrl/vm-c16-g-retry570-chatgpt-handoff-v2
```

Primary handoff:

```text
docs/vm_tlb/codex_handoff/c16/retry570/LANE_G_NVBIT175_CAPTURE_QUALIFICATION_HANDOFF.md
```

Reusable bootstrap runbook:

```text
docs/vm_tlb/runbooks/AI_TRACE_NVBIT_SERVER_BOOTSTRAP.md
```

## Start procedure

Do not checkout/reset/merge the handoff branch into the active Lane G worktree.

From the existing active worktree:

```bash
git fetch origin hrl/vm-c16-g-retry570-chatgpt-handoff-v2

git show origin/hrl/vm-c16-g-retry570-chatgpt-handoff-v2:docs/vm_tlb/codex_handoff/c16/retry570/LANE_G_NVBIT175_CAPTURE_QUALIFICATION_HANDOFF.md

git show origin/hrl/vm-c16-g-retry570-chatgpt-handoff-v2:docs/vm_tlb/runbooks/AI_TRACE_NVBIT_SERVER_BOOTSTRAP.md
```

Then continue on the current Lane G worktree/branch.

## Immediate execution order

1. Finish and push the current NVBit 1.7.5 version-differential + original Lane G first-kernel evidence closure. Do not lose current local work.
2. Update runtime status with the authoritative 1.7.5 results.
3. Freeze a known-good runtime profile and a known-bad-for-this-lane NVBit 1.8 profile.
4. Implement/consolidate the reusable preflight path described in the runbook.
5. Execute Q0 runtime/prewarm gate with NVBit 1.7.5 + original Lane G tracer + EAGER.
6. Only after Q0 PASS, execute Q1 minimal deterministic capture canary twice in independent processes.
7. Validate Q2 trace correctness/schema/lifecycle.
8. Publish a compact capture-qualification pack and STOP for review before any model/Llama/Qwen run.

## Hard constraints

Until Q1/Q2 publication is reviewed:

```text
NO full model
NO Llama/Qwen
NO C frozen target
NO 300s long-watch
NO historical 6+6 rerun
NO CUDA/driver changes
NO NVBit 1.8 re-debugging
NO broad/scientific model capture
```

Prewarm/startup must occur before `MEASUREMENT_ACTIVE`.

## Required lead fields in next report

```text
NVBIT_175_EVIDENCE_CLOSEOUT_COMMIT=
KNOWN_GOOD_PROFILE=
Q0_RUNTIME_READY=PASS/FAIL
Q1_MINIMAL_CAPTURE=PASS/FAIL
Q1_RUN1_RECORD_COUNT=
Q1_RUN2_RECORD_COUNT=
PREWARM_TRACE_COUNT=
TRACE_SCHEMA_VALIDATION=PASS/FAIL
MEASUREMENT_WINDOW_CLEAN=PASS/FAIL
TARGET_WALL_S=
REMOTE_WALL_S=
LOCAL_SSH_WALL_S=
ACTIVE_GPU_PROCESS_COUNT=
MEASUREMENT_ACTIVE_AFTER_RUN=ABSENT/PRESENT
BOOTSTRAP_RUNBOOK_COMMIT=
```

Do not stop at the first minor implementation obstacle. Attempt bounded fixes consistent with the handoff, keep variables isolated, and only stop early if a safety/measurement invariant would otherwise be violated.
