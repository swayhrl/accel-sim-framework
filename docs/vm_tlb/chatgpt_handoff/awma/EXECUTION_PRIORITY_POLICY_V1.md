# AWMA Execution Priority Policy V1

Date: 2026-09-17
Ownership: ChatGPT
Status: ACTIVE POLICY

## Core rule

AWMA mainline always has highest priority on both 174-new and node109.

Current next mainline question:

> How much of Q05's observed translation/cache behavior is intrinsic to the kernel, and how much is caused by replaying Q05 in isolation without the predecessor-kernel hardware state that exists in the real model execution?

This next mainline stage will study realistic predecessor warm-up / initial-state sensitivity before new TLB/PTW mechanisms are authorized.

## Node priority

### 174-new

Use first for the active mainline simulator/analysis task. Side work may run only when it cannot delay or mutate the active mainline worktree/runtime/evidence.

### node109 / RTX4080

The RTX4080 is a mainline resource first.

A side lane may start only when all of the following are true:

1. the current mainline stage does not require the RTX4080;
2. no already-planned mainline GPU task is waiting to start;
3. the side task is bounded and preemptible at a clean checkpoint;
4. it uses the shared GPU lock and cannot overlap another formal campaign;
5. it cannot change frozen mainline workload/producer/tool identities;
6. it stops immediately if ChatGPT issues a new mainline GPU task.

A side lane must never make the mainline wait for GPU availability, storage closure, branch cleanup, or scientific review.

## Side-lane ordering

When node109 is genuinely idle, side work priority is:

1. tasks that are highly likely to become the next mainline input;
2. bounded repairs to already-discovered capture/tool semantic gaps;
3. prequalified cross-model/native data acquisition;
4. exploratory work only by explicit new handoff.

Do not start Qwen3/DeepSeek/NCU/C16WARP1 or arbitrary new kernel capture merely because the GPU is idle unless a current ChatGPT handoff explicitly authorizes it.

## Stop/preemption rule

If a side lane is running when a mainline GPU task becomes ready:

- finish only the smallest safe atomic operation needed to leave data/provenance consistent;
- release the GPU lock;
- record the side-lane status as paused/incomplete if necessary;
- switch node109 to mainline.

Do not discard valid side-lane data and do not force a side experiment to completion before returning the GPU.

## Scientific ownership

Mainline scientific claims take precedence over side-lane asset generation. Side-lane outputs are inputs/backlog assets until separately reviewed and admitted into the mainline evidence chain.
