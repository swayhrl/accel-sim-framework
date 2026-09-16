# AWMA SIM_COMPAT_CAPTURE_V1 — Coordination Handoff

Status: **STEP 2 ACTIVE — node109 producer qualification**.

Base authority:

```text
NEW_SIM_BASELINE_V1_QUALIFIED
commit: 2cbb3bd7c85dd46977c2dbbbe829961c2f03ab49
qualification scope: HASH_BOUND_FIXED_WINDOW_10000
```

Accepted consumer checkpoint:

```text
174NEW_SIM_CONSUMER_READY_FOR_INPUT_V1
consumer-preparation commit: 25aa29862239a408099639ae9d5f1a0ea4fee1e1
SIM_BASELINE_ID: SIM_BASELINE_6305c065f2c4913448b0cb61a85d5003030c5917cd37d6a346fd3f42939d5964
```

This stage connects the already-qualified Simulation Analysis consumer/runtime on 174-new to a **new, simulator-native capture path on node109**. It does not convert C16WARP1 into traceg and does not change the Native Characterization evidence plane.

## Current activation sequence

```text
STEP 1 — 174-new consumer preparation
  COMPLETED
  -> 174NEW_SIM_CONSUMER_READY_FOR_INPUT_V1

STEP 2 — node109 producer qualification
  ACTIVE NOW
  -> CODEX_ACTIVATION_109_NOW.md
  -> CODEX_GOAL_109_SIM_COMPAT_CAPTURE_V1.md
  -> SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS

STEP 3 — after producer READY
  WAITING
  -> RESUME_174_AFTER_109_READY.md
  -> CODEX_GOAL_174NEW_FIRST_CURRENT_MODEL_SIM.md
  -> SIM_INPUT_ID + 10k replay + SIM_RUN_ID + Simulation Evidence
```

The user has confirmed node109 is now available for this work. Codex must still independently verify the GPU lock state before formal GPU execution and must never bypass a valid owner.

## Active node109 read order

A fresh node109 Codex window with no assumed prior chat context should read:

1. `CODEX_ACTIVATION_109_NOW.md`
2. `CODEX_GOAL_109_SIM_COMPAT_CAPTURE_V1.md`
3. `PRODUCER_CAPTURE_CONTRACT.md`
4. `ACCEPTANCE_REQUIREMENTS.md`
5. `BASELINE_REVIEW_AND_COMPATIBILITY_NOTES.md`

The activation document is the operator-facing entrypoint; the Goal is the executable scientific/engineering contract.

## Main objective

Close the producer half of the first current-model simulator-native trace path:

```text
109 / RTX4080
  existing Accel-Sim/NVBit tracer archaeology
  -> SM89 qualification
  -> micro-canary
  -> exact Qwen target binding
  -> target canary / volume qualification
  -> formal simulator-native capture
  -> parser + semantics + completeness + hash closure
  -> accepted 109->174/node164 transfer
  -> SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS
```

This producer stage stops after the READY/hash-closed bundle is transferred. It does **not** issue the formal consumer `SIM_INPUT_ID` and does **not** run current-model Accel-Sim replay on node109.

## Resource boundary

- Formal simulator capture must acquire `/data/c16/locks/c16_gpu_campaign.lock`.
- Re-check the lock immediately before GPU work even though node109 is reported free.
- Never delete, steal, or bypass a live lock.
- Never kill/restart another capture merely to obtain the GPU.
- Build, source audit, manifests, parser tooling and disk/size guards should be completed before expensive formal capture.

## Frozen scientific boundaries

1. Current C16WARP1/MREF data remains Native evidence and `NOT_PROVEN_LOSSLESS` for simulation input.
2. New simulation trace must come from a simulator-native tracer or a formally lossless producer path.
3. No opcode/order/width/sync/control semantics may be synthesized from C16WARP1.
4. `NEW_SIM_BASELINE_V1` is qualified only for `HASH_BOUND_FIXED_WINDOW_10000`; this producer stage does not broaden that scope.
5. Exact workload/input/backend/dtype/scenario/target binding is mandatory.
6. First formal current-model target is the frozen **Qwen2.5-0.5B S2_TEXT Prefill Attention / Q05_PREFILL_ATTN_FLASH occurrence 0** target.
7. The default is one formal target. A second target must not delay first-target closure.

## Efficiency policy

Recoverable engineering issues are solve-and-continue items: tracer build portability, SM89 compatibility, CUDA/NVBit paths, stale helper paths, packaging, parser invocation, transfer wrapper issues and small review-pack inconsistencies. Diagnose, repair safely, regression-test, document, continue.

Escalate only changes affecting workload identity, trace semantics, simulator semantics, scientific scope/status, or destructive data operations.
