# Final decision

Decision:

`R101_TRANSIENT_L2_TRAFFIC_RESPONSE_NO_CYCLE_GAIN`

## Gate closure

### B0 - qualified

- exact admitted 18-kernel replay, 6,195,889,164 instructions and 46,860 CTAs;
- 323,967,936 bytes of real L2 writeback, exactly equal to modeled DRAM
  writeback bytes;
- target-region dirty writeback is 323,966,336 bytes;
- all identity, coverage, exactly-once, translation/controller and full
  GPU/cache/memory/interconnect drain gates pass.

The modeled 323.968 MB is within about 6% of the accepted 344.72-346.92 MB
Native/source anchors without parameter tuning. B0 is qualified only for this
bounded model-relative L2/writeback comparison.

### O1 Gate A - passed

O1 `ORACLE_ZERO_COST_SCAN` drops 2,505,858 resident dirty dead-region lines /
320,749,824 bytes. L2/DRAM writeback falls to 25,582,784 bytes, a 92.1033%
reduction versus B0. All correctness and terminal gates pass.

This supports the semantic direction that software-declared region death
exposes resident dead-dirty writeback-elimination opportunity in this
simulator/input. O1 is not an implementable mechanism and its 0.9145% cycle
improvement is not a hardware-performance claim.

### M1 Gate B - traffic response, no material cycle gain

The fixed finite M1 produces:

- 2,173,674 lazy dead-dirty drops / 278,230,272 bytes;
- L2/DRAM writeback of 25,630,144 bytes, down 298,337,792 bytes or 92.0887%
  versus B0;
- DRAM read traffic down 195,934,464 bytes or 70.9360%;
- L2 misses down 3,067,000 or 19.3871%;
- 208,461 forced-live selections and 208,461 matched baseline fallbacks;
- generated/completed writebacks 200,236/200,236, outstanding zero;
- 18/18 coverage and every correctness/full-drain gate PASS.

M1 cycles are 15,297,575 versus B0's 15,374,861: a 77,286-cycle or 0.5027%
improvement. This is below the preregistered 5% promising threshold. M1 is
63,319 cycles (0.4156%) slower than O1 while producing only 47,360 additional
writeback bytes, reinforcing that the large traffic response is not
performance-primary in this simulator scope.

Per-kernel telemetry gives the expected temporal mediator: kernel 5 has
forced-live writebacks but no dead drop; after the declared death, kernel 6
first selects/drops exactly 180,224 dead dirty lines / 23,068,672 bytes. This
supports lazy death-boundary activation, not a decomposition of the total
cycle response.

## Conditional follow-ups

- C0: `NOT_TRIGGERED_M1_NOT_PROMISING`. The Goal permits C0 only after a
  >=5% promising M1 result.
- H0: `NOT_TRIGGERED_M1_NOT_PROMISING_NO_PRE_REGISTERED_INPUT`. No second
  preregistered admissible holdout is available, and no new 109 capture was
  requested.
- No threshold, cache, DRAM, translation or platform sweep was run.

## Interpretation and limits

M1 is a combined intervention: live-line victim priority plus lazy dead-dirty
drop. M1-versus-B0 cannot assign response to either component separately.
Replacement priority is modeled with zero added cycles; the result is not
timing-, area- or energy-closed hardware evidence.

Formal V1 admits only 128-byte-aligned regions. Unaligned/partial-line regions
are unsupported. The protected-deflection counter may overcount around invalid
ways and is not used as a causal fraction or decision gate.

This result does not establish novelty, RTX4080 hardware speedup, universal
LLM/optimizer benefit, full-training gain, equivalence to persistent
scratchpad/DSMEM, reproduction of Native D1's exact percentage, or an
explanation of the complete R101 fused benefit. The mechanism is not promoted
into the accepted simulator baseline.
