# AWMA Execution Priority Policy V2

Date: 2026-09-20
Ownership: ChatGPT
Status: ACTIVE POLICY

## 1. Core rule

AWMA mainline has absolute priority over candidate side lanes on both 174-new and node109.

Current mainline:

`AWMA_CROSS_TARGET_HITPATH_VALIDITY_AND_NATIVE_CROSSVIEW_V1`

Current scientific question:

> Is the large repaired translation hit-path sensitivity robust across representative AI kernel families, or specific to Q05 / current simulator timing semantics?

## 2. Mainline ordering

```text
P0:
  109 pause active MoE causal-closure at safe checkpoint
  174 finish V4 remote publication

P1:
  174 Prefill GEMM repaired hit-path screen
  109 exact-target native evidence closure

P2:
  174 Decode GEMV repaired hit-path screen

P3:
  Cross-view synthesis and scientific review

STOP before architecture mechanism
```

No side-lane experiment may delay these steps.

## 3. 109 / RTX4080 priority

The GPU is a mainline resource first.

If a side-lane campaign is running when mainline becomes READY:

1. do not kill an in-flight CUDA call mid-operation;
2. stop at the smallest safe checkpoint supported by the campaign;
3. persist already-completed evidence and scheduler state;
4. mark unfinished work `PAUSED_FOR_AWMA_MAINLINE`;
5. publish the paused state remotely;
6. release `/data/c16/locks/c16_gpu_campaign.lock`;
7. switch to mainline.

A side lane must not insist on using its originally allocated 20h window.

## 4. 174-new priority

174 is Simulation-plane mainline owner.

Before a new scientific stage starts:

- prior accepted report/review pack must be remotely published;
- execution branch remote HEAD must equal local accepted HEAD;
- required scientific files must be visible in the remote tree.

A local-only or node164-only result is:

`PROVENANCE_CLOSEOUT_REQUIRED`

and blocks the next 174 science stage.

Publication failure never authorizes science rerun.

## 5. Candidate side lanes

Candidate side lanes are preserved research assets, not abandoned work.

They may resume only when:

- no mainline task is READY on that node;
- ChatGPT explicitly reactivates the candidate;
- continuation answers a predeclared research question;
- it does not mutate mainline runtime/model/input authority.

## 6. Selection discipline

New mainline experiments are selected by scientific question, not asset availability.

Do not run a model, scenario, operator, or mechanism merely because:

- the model is already downloaded;
- an input pool exists;
- a profiler script already works;
- GPU/CPU time is otherwise idle.

## 7. Mechanism gate

No TLB/PTW/cache/MoE scheduling/AWQ optimization mechanism is authorized until the current mainline Cross-view stage is reviewed.

## 8. Solve-and-continue

Routine engineering issues:

- build;
- paths;
- parser;
- selector;
- receipt;
- transfer;
- Git publication;
- exact-target adapter;

are solve-and-continue.

Stop for scientific review only when continuation changes:

- workload/target identity;
- model revision;
- simulation functional/timing semantics beyond the declared diagnostic;
- evidence classification;
- claim boundary.
