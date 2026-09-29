# AWMA R101 transient-L2 architecture exploration - 174 V1

Stage: `AWMA_R101_TRANSIENT_L2_ARCH_EXPLORATION_V1`

Final report status: `R101_TRANSIENT_L2_TRAFFIC_RESPONSE_NO_CYCLE_GAIN`.

## Authorities and scope

- execution branch: `hrl/awma-r101-transient-l2-arch-174-v1`;
- coordination authority:
  `6533872601bb81dae1475b35d365f9dbe418cb23`;
- accepted simulator baseline:
  `AWMA_RTX4080_SIM_BASELINE_V1 @ 8d1f14a32f5538660d74da86ccb03a2c504c5735`;
- producer:
  `hrl/awma-r101-transient-l2-sim-capture-109-v1 @
  bb902283b7ce9e1902b460383fbd3e0bedbd884d`;
- admitted input: `SIM_INPUT_R101_L512_TRANSIENT_V1`, full ordered 18-kernel,
  five-step replay.

This is a model-relative, bounded L2/writeback experiment. It is not an
RTX4080 hardware calibration, full-application training result or paper
mechanism claim.

## Input and implementation

The consumer independently verifies the producer commit, payload/output hashes,
18 trace hashes/order/headers, exact single context/stream, A/B/X0/X1 aligned
regions, lifetime rows, address intersections, and terminal drop/overflow
status. It derives only 16 launch-time producer activations and 15
completion-time deaths. There is no per-line future last-use information.

All behavior is opt-in and default OFF. O1 is a zero-simulated-cost diagnostic
scan. M1 uses four finite descriptors, 11 logical metadata bits per line, no
extra L2 data/victim capacity, and victim order:

`invalid > dead transient > ordinary > live transient`.

All-live sets fall back to the baseline legal victim; live dirty evictions
write back normally. M1 has no whole-cache scan. Formal V1 accepts only
128-byte-aligned regions; arbitrary unaligned/partial-line regions are outside
scope because region-external dirty bytes could share a classified cache line.

The protected-deflection counter is observational and may overcount around
invalid ways, so it is not a decision gate. Forced-live and fallback counters
share the same branch and are reported as an accounting equality, not
independent evidence. Source plus directed tests, generated/completed
writebacks, DRAM byte equality and terminal drain provide the correctness
evidence.

## B0 scope qualification

B0 passes all input, identity, coverage, correctness and full-terminal-drain
gates:

- cycles: 15,374,861;
- instructions: 6,195,889,164; CTAs: 46,860;
- L2 writeback: 2,531,000 transactions / 323,967,936 bytes;
- target-region writeback: 323,966,336 bytes;
- DRAM writeback: 5,061,999 64-byte commands / 323,967,936 bytes;
- 18/18 coverage; untranslated, unobserved and duplicate application zero;
- GPU active, L2-writeback active, max-limit, deadlock and all tracked queues
  zero after a 192-cycle full drain.

The 323.968 MB modeled total is about 6% below the accepted 344.72-346.92 MB
Native/source anchors: the same order of magnitude without tuning platform,
cache, DRAM or translation parameters. This qualifies only the bounded
writeback comparison.

## O1 causal/semantic diagnostic

O1 passes all formal gates and drops 2,505,858 resident dirty dead-region lines
/ 320,749,824 bytes. Actual L2/DRAM writeback falls to 25,582,784 bytes:
a 298,385,152-byte (92.1033%) reduction versus B0. Reserved skips are zero.

This supports the preregistered direction: software-declared region death
exposes resident dead-dirty writeback-elimination opportunity in this
simulator/input, directionally aligned with Native D1. O1 is
`ORACLE_ZERO_COST_SCAN`, not an implementable mechanism. Its 0.9145% cycle
improvement is not a hardware-performance claim.

## M1 result and decision

Formal M1 passes all gates and records:

- cycles: 15,297,575, improving 77,286 cycles / 0.5027% versus B0;
- L2/DRAM writeback: 25,630,144 bytes, a 298,337,792-byte / 92.0887%
  reduction;
- lazy dead-dirty drop: 2,173,674 transactions / 278,230,272 bytes;
- DRAM reads: 80,278,400 bytes, down 70.9360%;
- L2 misses: 12,752,780, down 19.3871%;
- forced-live/fallback: 208,461/208,461;
- generated/completed/outstanding L2 writebacks: 200,236/200,236/0;
- 18/18 coverage and full terminal drain PASS.

The per-kernel sequence confirms the declared-death mediator: kernel 5 has
forced-live writebacks and no dead drop; kernel 6 is the first to drop dead
dirty data, exactly 180,224 lines / 23,068,672 bytes. M1 nevertheless improves
cycles by only 0.5027%, below the preregistered 5% promising gate. It is 0.4156%
slower than O1 while producing just 47,360 more writeback bytes.

The final decision is:

`R101_TRANSIENT_L2_TRAFFIC_RESPONSE_NO_CYCLE_GAIN`

C0 is `NOT_TRIGGERED_M1_NOT_PROMISING`. H0 is
`NOT_TRIGGERED_M1_NOT_PROMISING_NO_PRE_REGISTERED_INPUT`; no new 109 capture
was started.

## Cost and limitations

M1 adds 704 KiB of logical per-line metadata (1.0742% of modeled L2 data
capacity) plus 70 logical bytes for four descriptors. The C++ representation
uses 1 MiB plus 96 descriptor bytes. Region comparison and priority have zero
added modeled cycles, so this is not timing-, area- or energy-closed evidence.

M1 combines live-line priority and lazy dead-dirty drop; the total response
cannot be split between them. Formal V1 supports only 128-byte-aligned regions.
The protected-deflection counter may overcount around invalid ways and is not a
decision gate. The formal replay proves simulator identity, coverage,
exactly-once behavior, sidecar lifetime enforcement and quiescence; it does not
recompute Native numerical output.

No mechanism is promoted. The result does not establish novelty, RTX4080
hardware speedup, universal workload benefit, full-training gain, equivalence
to scratchpad/DSMEM, exact reproduction of Native D1, or an explanation of the
entire R101 fused benefit.

## Evidence

Review pack:

`docs/vm_tlb/review_packs/AWMA_R101_TRANSIENT_L2_ARCH_EXPLORATION_174_V1/`

Durable raw root:

`/root/share/mnt164/huangrulin/awma_r101_transient_l2_arch_174_v1/`

Formal RUN_SUMMARY SHA-256:

- B0: `d34d9cf0fda696e414d947830c81c1c7450954be3ef1615694d04bb803482373`;
- O1: `59e0ef3d53043d255595a1e8184b627b26b9025f32f4fd113be1dab418738eaf`;
- M1: `d5ce6e84a68a9fb98744513b93f04ea0f81ac58374b6fc6c46f449e29024fc98`.
