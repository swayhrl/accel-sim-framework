# DTC-L1 / ISCAS 2027 Discussion Reference

Last update: 2026-09-25

## 1. Final downstream story

The downstream-localization program is closed.

The accepted evidence supports a three-part interpretation:

1. DTC removes L1-side miss-concurrency constraints and exposes substantially more memory-level parallelism.
2. For BICG/GESUMMV, simply enlarging tested explicit queues does not convert that concurrency into performance.
3. A source-discriminating idealized increase in detailed-DRAM service timing/rate produces large speedups, while BICG also retains an additional L2-capacity sensitivity.

The paper should therefore avoid the simplistic statement:

> “DTC moves the bottleneck to the L2.”

A better statement is:

> DTC shifts the resource balance downstream. For difficult workloads, explicit queue capacity is not the dominant tested limiter; performance is instead strongly sensitive to deeper memory-service timing/rate, with L2 capacity contributing an additional workload-dependent effect.

## 2. Queue evidence

Tested queue interventions include:

- L2-internal miss queue 32->128;
- L2->DRAM 64->256;
- DRAM scheduler/admission 64->256;
- DRAM return path 192/64 -> 768/256;
- full queue-chain headroom;
- ICNT->L2 ingress 64->256.

None produces material BICG speedup.

This matters methodologically because several corresponding pressure counters are large. Direct intervention shows that large pressure counts alone do not establish queue capacity as the performance bottleneck.

## 3. DRAM-service evidence

The accepted E probe changes only the DRAM clock domain:

`1410:1410:1410:850 -> 1410:1410:1410:1700`

with DRAM timing cycle counts, channels, mapping, queues, bus width, L2 resources, and DTC cap held fixed.

This is an idealized **detailed-DRAM service-rate/time-domain upper bound**.

It yields large cycle reductions on both BICG and GESUMMV.

Do not describe it as a physical V100/HBM frequency experiment.

## 4. GESUMMV validation

GESUMMV confirms the same direction:

- E/IO 107,119,606 vs default 210,667,785 cycles;
- E/OO 79,382,011 vs default 143,059,605;
- F/IO 103,536,854;
- F/OO 77,454,520.

Therefore the DRAM-service sensitivity is not a BICG-only artifact, within the tested workload scope.

## 5. BICG residual capacity effect

BICG receives meaningful benefit from larger L2 capacity even after service headroom is introduced.

The pre-registered all-headroom ceiling:

- 20-MiB L2 + full queue chain + DRAM2x

reaches:

- IO 47,347,123 cycles;
- OO 22,204,820 cycles.

Treat this as an upper-bound decomposition point, not a practical hardware prescription.

## 6. Final ingress result

The source-defined `gpu_stall_icnt2mem` counter measures ICNT->L2 ingress-admission pressure when a packet waits and the finite FIFO cannot accommodate worst-case sector expansion.

R5 directly enlarges that FIFO:

- G: 64->256 at default DRAM service;
- H: 64->256 on top of E/DRAM2x.

Both are effectively neutral.

Therefore the large ingress-stall counter should be described as pressure/backpressure telemetry, not proof that the 64-entry ingress FIFO is the capacity limiter.

## 7. Paper claim boundaries

Supported:

> DTC can expose more concurrency than a fixed downstream hierarchy can efficiently service for some workloads.

Supported:

> Queue-capacity interventions across the tested path do not explain the large slowdown in BICG/GESUMMV.

Supported:

> The tested workloads are strongly sensitive to an idealized increase in detailed-DRAM service timing/rate.

Supported:

> BICG also exhibits a separate L2-capacity sensitivity.

Not supported:

- “DRAM is the unique bottleneck.”
- “Real hardware needs a 2x memory clock.”
- “All DTC workloads need more DRAM bandwidth.”
- “Queue pressure never matters.”
- “NoC is not a bottleneck.”
- any generalization beyond the tested workload/configuration scope.

## 8. Paper-use recommendation

Use the downstream section to answer a mechanism question, not to propose a second architecture.

A compact paper-facing sequence is:

1. BICG/GESUMMV are cap-sensitive.
2. L2 capacity helps partially; L2 MSHR does not.
3. queue-pressure counters are large, but direct queue enlargement is ineffective.
4. detailed-DRAM service headroom strongly recovers performance.
5. therefore DTC exposes useful MLP, but downstream service balance determines whether that MLP is beneficial.

This is sufficient. Do not continue simulator localization.
