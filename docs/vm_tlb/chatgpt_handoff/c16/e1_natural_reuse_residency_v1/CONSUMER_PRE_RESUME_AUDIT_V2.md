# Natural-Reuse Producer / Consumer Pre-Resume Audit V2

## Producer

`hrl/c16-e1-natural-reuse-residency-109-v1@ccfdc89d517766d12588ee131818efe341c7e17c`

Preliminary remote audit supports the reported producer closure:

- AWQ q/down/up show packed-state-scale K1 DRAM and tens-of-KiB K2/K4 DRAM;
- RAW down/up remain ~135.8 MB DRAM across K1/K2/K4;
- fresh-process AWQ natural runs reproduce token sequence `[23578, 11, 323, 3950]` and 12 occurrence bindings;
- natural layer0 up_proj DRAM is ~49 MB and lies above the isolated WARM/DENSE bracket;
- natural layer0 down_proj DRAM is slightly above isolated DENSE while timing remains inside its bracket;
- held-out layer14 up_proj reproduces the natural ~49 MB DRAM pattern;
- optional RAW BF16 full-model control runs cleanly and remains high-DRAM.

Producer framing:
`CASE_B_WITH_CASE_D_ROLE_DEPENDENCE`

No producer rerun is requested.

## Minor correctness/wording repairs handled in consumer hardening

These are consumer-side interpretation/package fixes and must not trigger a separate node109 Goal.

### 1. Capacity "knee" wording

The sampled dose grids do not identify an exact physical knee.

Producer values such as:
- q_proj: 32 MiB
- down/up: 16 MiB

are the **first tested doses meeting the registered DRAM gate**.

They must be reported as:
- first tested trigger dose;
- together with the immediately previous tested dose as a tested-grid bracket.

Examples:
- q_proj first tested trigger = 32 MiB, with previous tested point 0 MiB;
- down/up first tested trigger = 16 MiB, with previous tested point 0 MiB.

Do not state that the true physical cache knee is exactly 32 or 16 MiB.

The consumer hardening adds tested-bracket reporting while preserving producer values for cross-check.

### 2. Layer14 isolated-reference boundary

There is no exact isolated layer14 up_proj WARM/DENSE authority in the accepted upstream evidence.

Therefore:
- do not borrow layer0 isolated references for layer14;
- do not fail the whole natural consumer because layer14 lacks an isolated reference;
- report layer14 warm_fraction as `NO_EXACT_ISOLATED_AUTHORITY`;
- use layer14 only as a held-out **natural cross-layer behavior** validation.

## Consumer hardening authority

Use:

`hrl/c16-e1-natural-reuse-residency-consumer-hardening-v2@97c6852351eddcb258d5c50e18e9387a8c42c4a6`

This branch is based directly on the prep branch:

`hrl/c16-e1-natural-reuse-residency-consumer-174new-v1@bfe3dfdc384b1edd93469ce2adefe26f901ea1c6`

so the consumer worktree should fast-forward it before consuming the producer.

No scientific gate was weakened.
