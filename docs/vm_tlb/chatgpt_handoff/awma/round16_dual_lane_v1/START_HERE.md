# START HERE — AWMA Round16 dual-lane problem-boundary execution

Date: 2026-09-30

This coordination handoff turns the frozen Round16 contracts into two independent execution Goals.

Scientific/design authority:
- Round15 literature/frontier review: `c6958df456393b46a9268add5898bbd7f12c1ca9`
- Frozen problem contracts: `2b4e37e89a3dea8198a7bbc8c548b3acabdc7779`

## Current lane assignment

- **Lane F / node109 / RTX4080**: VLA / RTC inference-time VJP boundary.
- **Lane G / node109 / RTX4080**: R102 real precision-gated weight-update detect/compact/apply boundary.
- **Lane E / 174-new**: STOP. No new simulator work is authorized.
- CCE/Liger quick-falsification side lane: **DEFERRED**, not authorized in this round.

Lane names remain F/G/E. Do not rename them.

## Shared execution rule

Both Lane F and Lane G may perform CPU/source/input preparation in parallel.

All CUDA/NCU/NSYS activity on node109 must acquire:

`/data/c16/locks/c16_gpu_campaign.lock`

There is one RTX4080. GPU work is strictly mutually exclusive. Do not bypass the lock, create a second lock, or run "small" CUDA jobs outside it.

Do not busy-poll the lock. Finish CPU preparation first; acquire the GPU only for an already-qualified bounded job; release it immediately after the job/canary/profile set.

## Scientific method

For both lanes:

```
natural problem / real input
→ semantic + identity qualification
→ natural timing weight
→ ideal/headroom bound
→ strong software baseline
→ residual localization
→ only then consider architecture
```

A large count, high sparsity, many saved tensors, large traffic, or expensive-looking kernel is not itself a mechanism justification.

5% is the current additional-investment screen, not a universal scientific threshold.

## Missing-input policy

Distinguish:
- scientific payload/identity missing: STOP that lane;
- deterministically reconstructible wrapper/index/manifest missing: reconstruct, record and continue;
- environment/tooling issue that preserves scientific identity: repair and continue.

Do not turn a missing scientific payload into a synthetic proxy merely to keep the lane active.

## Branch/worktree isolation

Each lane uses its own execution branch/worktree and its own env/cache/raw/report directories.

Lane F execution branch:
`hrl/awma-vla-rtc-vjp-boundary-109-v1`

Lane G execution branch:
`hrl/awma-r102-real-update-boundary-109-v2`

Neither lane merges the other during execution.

## Read order

Lane F:
1. `../round16_problem_contracts_v1/VLA_RTC_VJP_CONTRACT_V1.md`
2. `../round16_problem_contracts_v1/SOURCE_AND_SCOPE_NOTES.md`
3. `LANE_F_VLA_RTC_VJP_109_GOAL.md`

Lane G:
1. `../round16_problem_contracts_v1/R102_REAL_UPDATE_CONTRACT_V1.md`
2. `../round16_problem_contracts_v1/SOURCE_AND_SCOPE_NOTES.md`
3. `LANE_G_R102_REAL_UPDATE_109_GOAL.md`

## Cross-lane non-interference

- Lane F must not use R102 inputs or start weight-update experiments.
- Lane G must not download/run VLA assets or edit RTC code.
- Neither lane starts 174/Accel-Sim.
- Neither lane starts CCE/Liger.
- A negative result in one lane does not authorize the other lane to broaden scope.

## Required closure

Every lane ends with:
- exact decision label;
- source/input/target identity receipt;
- raw/hash index;
- exact branch/commit/tree;
- remote fetch-back verification;
- clean worktree;
- GPU lock released;
- STOP.

No automatic next mechanism or follow-on experiment.
