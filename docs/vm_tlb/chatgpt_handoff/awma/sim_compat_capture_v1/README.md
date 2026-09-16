# AWMA SIM_COMPAT_CAPTURE_V1 — Coordination Handoff

Status: **ACTIVATED IN TWO STEPS**.

Base authority:

```text
NEW_SIM_BASELINE_V1_QUALIFIED
commit: 2cbb3bd7c85dd46977c2dbbbe829961c2f03ab49
qualification scope: HASH_BOUND_FIXED_WINDOW_10000
```

This stage connects the already-qualified Simulation Analysis consumer/runtime on 174-new to a **new, simulator-native capture path on node109**. It does not convert C16WARP1 into traceg and does not change the Native Characterization evidence plane.

## Current activation sequence

Because node109 may be occupied by another formal GPU task, do **not** hold a 174-new Codex window waiting for it.

Use this sequence:

```text
STEP 1 — now, 174-new only
  CODEX_GOAL_174NEW_CONSUMER_PREP_V1.md
  -> complete all producer-independent preparation
  -> stop at 174NEW_SIM_CONSUMER_READY_FOR_INPUT_V1

STEP 2 — later, when node109 is free
  CODEX_GOAL_109_SIM_COMPAT_CAPTURE_V1.md
  -> qualify simulator-native tracer/capture
  -> publish formal READY producer bundle

STEP 3 — after producer READY
  CODEX_GOAL_174NEW_FIRST_CURRENT_MODEL_SIM.md
  -> admit bundle
  -> issue SIM_INPUT_ID
  -> run NEW_SIM_BASELINE_V1 10k replay
  -> repeat/determinism
  -> SIM_RUN_ID + Simulation Evidence
```

The same 174-new working branch may be resumed after Step 1 if its state is clean and review-pack checkpoint is committed/pushed; otherwise use a continuation branch rooted at that accepted prep commit.

## Main objective

End-to-end target state remains:

```text
109 / RTX4080
  simulator-native tracer qualification
  -> SIM_COMPAT_CAPTURE_V1 producer bundle
  -> hash-closed transfer

174-new
  -> consumer admission / SIM_INPUT_ID
  -> parser smoke
  -> NEW_SIM_BASELINE_V1 bounded replay
  -> normalized VM/TLB/PTW/cache telemetry
  -> SIM_RUN_ID + catalog
  -> first current-model Simulation Evidence
```

If the first formal current-model target closes end-to-end, this wave may close both:

```text
S1 SIM_COMPAT_CAPTURE_V1 producer qualification
S2 first current-model baseline simulation
```

for that exact target. It must not start mechanism sweeps.

## Parallelism and resource boundary

- Native Characterization and Simulation Analysis remain separate scientific evidence planes.
- 174-new consumer preparation can run independently of Native work.
- 109 formal simulator capture **must acquire** `/data/c16/locks/c16_gpu_campaign.lock` and must not overlap another formal GPU capture on the RTX4080.
- Never kill/restart another active capture merely to obtain the GPU.
- A busy 109 is not a blocker for the 174-new consumer-preparation checkpoint; simply defer Step 2.

## Read order

For the new 174-new prep window, read:

1. `CODEX_GOAL_174NEW_CONSUMER_PREP_V1.md` — self-contained execution context and Goal.
2. `BASELINE_REVIEW_AND_COMPATIBILITY_NOTES.md`
3. `PRODUCER_CAPTURE_CONTRACT.md`
4. `ACCEPTANCE_REQUIREMENTS.md`

Later node-specific executable Goals:

- node109: `CODEX_GOAL_109_SIM_COMPAT_CAPTURE_V1.md`
- 174-new producer-dependent continuation: `CODEX_GOAL_174NEW_FIRST_CURRENT_MODEL_SIM.md`

## Frozen scientific boundaries

1. Current C16WARP1/MREF data remains Native evidence and `NOT_PROVEN_LOSSLESS` for simulation input.
2. New simulation trace must come from a simulator-native tracer or a formally lossless producer path.
3. No opcode/order/width/sync/control semantics may be synthesized from C16WARP1.
4. `NEW_SIM_BASELINE_V1` is qualified only for `HASH_BOUND_FIXED_WINDOW_10000`; this stage must not silently turn that into a full-ROI qualification.
5. Exact workload/input/backend/dtype/scenario/target binding is mandatory.
6. The first formal current-model target is **Qwen2.5-0.5B S2_TEXT Prefill Attention** unless its already-accepted identity cannot be reproduced exactly. A micro-canary may precede it, but cannot substitute for it.
7. A second current-model target may be added in the same wave only if the first target is fully closed and resource cost remains bounded.

## Efficiency policy

Recoverable engineering issues are solve-and-continue items. Examples include tracer build portability, SM89 compatibility, CUDA include/library paths, stale helper paths, packaging, transfer wrapper issues, parser-format compatibility, and small review-pack inconsistencies. Fix, regression-test, document, continue.

Escalate only changes affecting workload identity, trace semantics, simulator semantics, evidence status, or destructive data operations.
