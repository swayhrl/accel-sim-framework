# ChatGPT Review — 174 Hit-Path V1 Deadline Closeout

Date: 2026-09-20

User-reported execution branch:
`hrl/awma-repaired-hitpath-validity-174new-v1`

User-reported final authority:
`b9bb4c6c356f2d98b9213d1d2ac3efdade057901`

At handoff-generation time, the GitHub connector had not yet indexed this branch/commit. Therefore the next Codex Goal MUST independently verify the exact remote branch/commit before reusing its artifacts.

## 1. Decision

Reported V1 stage status is accepted as:

`SCOPED_EXECUTION_CLOSEOUT_WITH_PARTIAL_RUNTIME_QUALIFICATION`

The incomplete rebuilt P34 10/80 run remains:

`PARTIAL_NOT_ADMITTED`

The absence of 5/80, 2/80, 0/80, 10/40, 10/0 and 0/0 results is not a scientific negative result.

## 2. Deadline interpretation

The prior ChatGPT-authored Goal:

`CODEX_NEXT_STAGE_174NEW_REPAIRED_HIT_PATH_MODEL_VALIDITY_V1.md`

contains no fresh stage deadline, no new 20-hour deadline, and no instruction to inherit a previous pipeline deadline.

Therefore the reported 39-minute deadline closeout is treated as an execution/budget boundary, not as a scientific STOP condition.

The next Goal MUST create a fresh stage clock and MUST NOT inherit:

- `AWMA_REPAIRED_VM_REQUALIFICATION_20H_174NEW_V1/PIPELINE_STATE.json` deadline;
- the prior 20h campaign deadline;
- any stale no-new-target cutoff stored in an earlier review pack.

If an external launcher/runtime imposes a stricter real deadline, record its source explicitly and obey it.

## 3. What V1 reportedly completed

Reuse after exact branch/commit verification:

- provenance closeout;
- repaired source recovery;
- hit-path source semantics audit;
- rebuilt runtime/binary authority if present and hash-bound;
- partial P34 10/80 log/receipt on node164.

Do not rerun provenance/source-audit work merely because V1 scientific timing did not complete.

## 4. Runtime qualification requirement

The rebuilt runtime is not admitted for the latency matrix until one complete P34 repaired natural 10/80 target run closes.

The complete qualification target remains:

```text
Q05 target cycles             = 1,619,068
downstream admissions         = 3,090,304
translated admissions         = 3,090,304
untranslated/unobserved       = 0
post-ready retranslation      = 0
same completed target identity
```

Use the exact rebuilt binary from V1 if its SHA/runtime authority is valid.

Do not rebuild again unless the V1 binary is missing or corrupted.

The partial V1 run is evidence of execution progress only; do not extrapolate final cycles or counters from it.

## 5. Next-stage scientific priority

After rebuilt 10/80 qualification, execute the repaired target-only lookup-latency envelope.

Priority order is changed to maximize scientific value if a later real deadline intervenes:

1. 0/80 — closes the L1 hit-path envelope endpoint;
2. 0/0 — closes the zero-lookup residual versus I0;
3. 10/0 — isolates L2 lookup timing with natural L1;
4. 5/80 — intermediate L1 point;
5. 2/80 — intermediate L1 point;
6. 10/40 — intermediate L2 point.

This priority order does not change the predeclared matrix or scientific contract.

Accepted reused anchors remain:

- repaired P34 10/80 = 1,619,068 cycles;
- repaired P34 Q05-only I0 = 758,082 cycles.

## 6. No architecture promotion

This continuation remains:

`MODEL_VALIDITY_CHARACTERIZATION_ONLY`

It does not authorize:
- TLB redesign;
- PTW/PWC redesign;
- lookup-latency hardware claim;
- page-size/segmentation;
- prefetch/speculation;
- cache mechanism.

## 7. Next stage

`AWMA_REPAIRED_HIT_PATH_MODEL_VALIDITY_174NEW_V2`

The V2 review pack must be separate from V1.

V1 remains immutable historical execution evidence.
