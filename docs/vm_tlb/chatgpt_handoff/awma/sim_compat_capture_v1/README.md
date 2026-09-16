# AWMA SIM_COMPAT_CAPTURE_V1 — Coordination Handoff

Status: **READY TO ACTIVATE**.

Base authority:

```text
NEW_SIM_BASELINE_V1_QUALIFIED
commit: 2cbb3bd7c85dd46977c2dbbbe829961c2f03ab49
qualification scope: HASH_BOUND_FIXED_WINDOW_10000
```

This stage connects the already-qualified Simulation Analysis consumer/runtime on 174-new to a **new, simulator-native capture path on node109**. It does not convert C16WARP1 into traceg and does not change the Native Characterization evidence plane.

## Main objective

In one coordinated wave, complete as much as possible of:

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
- 174-new consumer preparation can run in parallel with Native work.
- 109 formal simulator capture **must acquire** `/data/c16/locks/c16_gpu_campaign.lock` and must not overlap another formal GPU capture on the RTX4080.
- Never kill/restart another active capture merely to obtain the GPU.
- Waiting for the GPU lock is not a scientific blocker; complete CPU/code preparation first and continue when admitted.

## Read order

1. `BASELINE_REVIEW_AND_COMPATIBILITY_NOTES.md`
2. `PRODUCER_CAPTURE_CONTRACT.md`
3. `ACCEPTANCE_REQUIREMENTS.md`
4. node-specific executable Goal:
   - `CODEX_GOAL_109_SIM_COMPAT_CAPTURE_V1.md`
   - `CODEX_GOAL_174NEW_FIRST_CURRENT_MODEL_SIM.md`

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
