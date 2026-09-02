# CODEX_NEXT_STAGE

## Status

**HOLD — M1-M3 GOAL SPECIFICATION NOT YET AUTHORIZED**

The branches and M0 specification have been initialized. Do not start DTC implementation from this file.

## Objective

Preserve the clean source anchors and wait for the next ChatGPT-authored goal specification.

## Source anchors

Framework:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-v0`
- official base `accel-sim/accel-sim-framework:dev`
- base SHA `d930ad6d02c09bb56867132583735aba0389cff4`

Core:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-v0`
- official base `accel-sim/gpgpu-sim_distribution:dev`
- base SHA `91880c53383d5a6a6742bfb1be2c5f34e39c7871`

## Allowed bootstrap action

Codex may only:

1. fetch/pull the two project branches;
2. create isolated local worktrees for them;
3. read the handoff and core M0 specification;
4. verify/report the checked-out SHAs and working-tree cleanliness to the user.

No repository commit is required for this bootstrap check.

## Explicitly forbidden scope

Do NOT:

- implement Baseline PIB;
- implement IO-DTC or OO-DTC;
- add configuration knobs;
- refactor cache code;
- modify L2/NoC/DRAM;
- run formal workload characterization;
- create performance claims;
- alter ChatGPT-owned handoff files;
- infer the next stage from `DISCUSSION_REFERENCE.md`.

## STOP condition

STOP after branch/worktree bootstrap verification.

The next executable goal will be written only after M1-M3 are jointly planned and reviewed.
