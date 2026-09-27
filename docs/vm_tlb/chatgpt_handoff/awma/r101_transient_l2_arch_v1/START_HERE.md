# START HERE — AWMA R101 Transient-L2 Architecture V1 (Merged Round)

## Mission

This is one merged round:

`R101R1 review + exact simulator input production + architecture hypothesis + implementation + first screen + diagnosis`.

Do not split deterministic wrapper/build/report work into extra rounds.

Accepted Native authorities:

- R101: `cfbe6503585fa1b10d979db5d26fb9be3a80e563`
- R101R1: `422faf4d8fcdb5ac49068dcf19a6e783954a29a8`
- R101R1 final: `R101R1_EXISTING_L2_CONTROL_INSUFFICIENT_READY_FOR_ARCH_REVIEW`

Literature/architecture note:

`hrl/awma-chatgpt-literature-notes-v1 @ a63574628b2daf20dd3c9256f53d5cd3ff7df26f`

Read:

`docs/vm_tlb/literature_notes/awma/rounds/2026-09-27_ROUND_13_R101_TRANSIENT_L2_ARCHITECTURE.md`

## Parallel lanes

### Lane F — node109 producer

Goal:

`CODEX_GOAL_109_R101_TRANSIENT_L2_SIM_CAPTURE_V1.md`

Suggested branch:

`hrl/awma-r101-transient-l2-sim-capture-109-v1`

Purpose:
- reuse exact accepted R101 L512 scientific payload;
- capture simulator-native SASS trace for the accepted three-kernel recurrence;
- publish A/B/X0/X1 address-region and lifetime sidecar;
- no new mechanism and no new scientific workload.

### 174-new — simulator architecture lane

Goal:

`CODEX_GOAL_174_R101_TRANSIENT_L2_ARCH_EXPLORATION_V1.md`

Suggested branch:

`hrl/awma-r101-transient-l2-arch-174-v1`

This lane may start immediately:
- audit accepted simulator baseline;
- implement directed tests;
- implement O1/M1 behind opt-in switches;
- prepare parser/consumer.

It consumes the Lane F bundle only after READY/hash verification.

Lane G stays free. Do not start a third GPU question.

## Architecture hypothesis

Working name only:

`TRANSIENT_L2_V1`

It is not a novelty or paper claim.

### O1 — DEAD_DROP_ORACLE

Zero-cost diagnostic:
at region-death boundaries, resident dirty lines belonging to the dead transient region may be invalidated without writeback.

Purpose:
- verify the simulator/input can reproduce the same causal direction as Native `discard.global.L2`;
- quantify writebacks that survive until region death.

O1 is not a hardware proposal.

### M1 — BOUNDED_LIVE_RETENTION_DEAD_DROP

No extra L2 data capacity.

For finite software-declared transient regions:
- accesses/stores identify a transient region;
- live transient lines receive lowest eviction priority while any legal alternative victim exists;
- invalid > dead-transient > ordinary > live-transient;
- if all candidate ways are live-transient, normal replacement proceeds;
- dirty **live** transient eviction writes back normally;
- dirty **dead** transient eviction may be dropped;
- dead transient lines are preferred victims;
- no future trace knowledge;
- no unlimited pinning;
- no extra victim buffer.

The exact software-known region state changes only at declared kernel-phase boundaries.

## Simulator scope warning

Existing `AWMA_RTX4080_SIM_BASELINE_V1` was promoted for AWMA memory/translation studies. It is not automatically paper-qualified for this new L2 claim.

This merged round therefore performs a bounded L2/writeback requalification on the exact R101 trace before interpreting M1.

Do not tune platform parameters to Native numbers.

Primary structural endpoint:
- dirty L2 writeback / DRAM-write behavior.

Relative simulator cycles are secondary until the cache/writeback baseline is credible.

## Native comparison anchors

Accepted discovery L512:

- source logical A/B/C writes across five steps: ~346.03 MB;
- R101 NS-family DRAM writes: ~344.72 MB;
- R101R1 matched B0 NS-family DRAM writes: 346.92 MB;
- R101R1 D1 discard: 255.81 MB, -26.26%;
- D1 graph replay: 3.39% slower;
- D2 full A+B persistence+discard: no write reduction and 2.60% slower.

Simulator need not reproduce the exact percentages, but it must represent the same cache/writeback phenomenon before architecture conclusions.

## Closest-work boundary

Do not claim novelty from:
- PTX `discard.global.L2`;
- L2 persistence/access-policy;
- generic software locality descriptors;
- inter-kernel locality scheduling;
- persistent scratchpad across kernels;
- dead-block prediction;
- symmetric NS GEMM;
- Gram Newton-Schulz.

A survivor must later be differentiated from these.

## Shared execution rules

- all new simulator behavior opt-in; default OFF;
- OFF-equivalence must reproduce the accepted comparator;
- preserve accepted Native evidence;
- node164 is durable authority;
- no model download;
- no simulator run on109;
- no Native GPU execution from174-new;
- ordinary engineering solve-and-continue;
- missing deterministic wrappers/manifests are reconstructible controls, not scientific-input loss;
- scientific payload/identity/semantics change => STOP and review.

## Publication

Lane F and174 each publish their own compact pack and exact remote closure.

The174 final report must integrate:
- input admission;
- baseline L2/writeback requalification;
- O1;
- M1;
- mechanism cost accounting;
- diagnosis;
- final classification.

Do not auto-merge into baseline.
